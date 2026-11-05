from urllib.parse import urlencode, urljoin
from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.templatetags.static import static
from django.utils.html import strip_tags
from .models import Post
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string

# Create your views here.

SITE_DESCRIPTION = (
    "Embracing the Girl Child Initiative advances girls' rights, education, "
    "safety, and wellbeing in Nigeria."
)


def _seo_context(request, title, description, image=None, og_type='website',
                 canonical_url=None):
    site_url = settings.SITE_URL.rstrip('/')
    canonical_url = canonical_url or urljoin(site_url + '/', request.path.lstrip('/'))
    image_url = urljoin(site_url + '/', image or static('images/logo.jpg'))
    return {
        'seo_title': title,
        'seo_description': description,
        'seo_canonical_url': canonical_url,
        'seo_image_url': image_url,
        'seo_logo_url': urljoin(site_url + '/', static('images/logo-main.png').lstrip('/')),
        'seo_type': og_type,
        'site_url': site_url,
    }


def home(request):
    post_list = Post.objects.filter(status='published')[:3]
    context = {'posts': post_list}
    context.update(_seo_context(
        request,
        "Embracing the Girl Child Initiative | Girls' Rights in Nigeria",
        SITE_DESCRIPTION,
    ))
    return render(request, 'index.html', context)



def about(request):
    context = _seo_context(
        request,
        "About Us | Embracing the Girl Child Initiative",
        "Learn about Embracing the Girl Child Initiative and our work supporting "
        "girls' rights, education, safety, and wellbeing in Nigeria.",
    )
    return render(request, 'about.html', context)



def gallery(request):
    context = _seo_context(
        request,
        "Our Gallery | Embracing the Girl Child Initiative",
        "See photos from Embracing the Girl Child Initiative's outreach, "
        "campaigns, and community activities in Nigeria.",
    )
    return render(request, 'gallery.html', context)



def videos(request):
    context = _seo_context(
        request,
        "Videos | Embracing the Girl Child Initiative",
        "Watch videos about our work empowering girls and advancing girls' "
        "rights and wellbeing in Nigeria.",
    )
    return render(request, 'videos.html', context)



def contact(request):
    context = _seo_context(
        request,
        "Contact Us | Embracing the Girl Child Initiative",
        "Contact Embracing the Girl Child Initiative to learn about our work, "
        "partnerships, and ways to support girls in Nigeria.",
    )
    return render(request, 'contact.html', context)



def blog(request):
    post_list = Post.objects.filter(status='published')
    paginator = Paginator(post_list, 6)  # Show 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    canonical_url = urljoin(settings.SITE_URL.rstrip('/') + '/', request.path.lstrip('/'))
    if page_obj.number > 1:
        canonical_url += '?' + urlencode({'page': page_obj.number})
    context = {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    context.update(_seo_context(
        request,
        ("Blog - Page " + str(page_obj.number) + " | Embracing the Girl Child Initiative")
        if page_obj.number > 1 else "Blog | Embracing the Girl Child Initiative",
        "Read news, stories, and insights on girls' rights, education, health, "
        "and empowerment from Embracing the Girl Child Initiative.",
        canonical_url=canonical_url,
    ))
    return render(request, 'blog.html', context)




def blog_single(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()

    description = strip_tags(post.content).strip()
    description = ' '.join(description.split())[:300]
    image_url = post.image.url if post.image.name else None
    context = {'post': post, 'comments': comments, 'form': form}
    context.update(_seo_context(
        request,
        f"{post.title} | Embracing the Girl Child Initiative",
        description or post.title,
        image=image_url,
        og_type='article',
    ))
    return render(request, 'single-blog.html', context)

   






    
@login_required
def dashboard(request):
    qs = Post.objects.filter(author=request.user)

    # Filters
    status = request.GET.get('status')
    category = request.GET.get('category')
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    total_posts = qs.count()
    total_views = sum(getattr(p, 'views', 0) for p in qs)
    total_comments = sum(p.comments.count() for p in qs)

    context = {
        'posts': posts,
        'total_posts': total_posts,
        'total_views': total_views,
        'total_comments': total_comments,
        'paginator': paginator,
    }

    # If AJAX request for a page (used by pagination/filter UI), return HTML fragment
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/_posts_table.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'dashboard.html', context)

@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # AJAX response with rendered row
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('partials/_post_row.html', {'post': post}, request=request)
                return JsonResponse({'success': True, 'html': html})
            return redirect('dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('partials/_post_row.html', {'post': post}, request=request)
                return JsonResponse({'success': True, 'html': html})
            return redirect('dashboard')
    else:
        form = PostForm(instance=post)
    return render(request, 'post_form.html', {'form': form})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        post.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard')
    return render(request, 'post_delete.html', {'post': post})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


def sitemap(request):
    posts = Post.objects.filter(status='published').order_by('-created_at')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    static_views = ['home', 'about', 'gallery', 'videos', 'contact', 'blog']
    for name in static_views:
        page_url = urljoin(settings.SITE_URL.rstrip('/') + '/', reverse(name).lstrip('/'))
        xml += f'<url><loc>{escape(page_url)}</loc></url>\n'
    for post in posts:
        post_url = urljoin(
            settings.SITE_URL.rstrip('/') + '/',
            reverse('post_detail', args=[post.slug]).lstrip('/'),
        )
        xml += (
            f'<url><loc>{escape(post_url)}</loc>'
            f'<lastmod>{post.updated_at.date().isoformat()}</lastmod></url>\n'
        )
    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml; charset=utf-8')


def robots_txt(request):
    content = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /dashboard/\n'
        'Disallow: /login/\n'
        f'Sitemap: {settings.SITE_URL.rstrip("/")}{reverse("sitemap")}\n'
    )
    return HttpResponse(content, content_type='text/plain; charset=utf-8')