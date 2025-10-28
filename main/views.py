from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Post
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string

# Create your views here.

def home(request):
    post_list = Post.objects.all()[:3]

    return render(request, 'index.html', {'posts': post_list})



def about(request):
    return render(request, 'about.html')



def gallery(request):
    return render(request, 'gallery.html')



def videos(request):
    return render(request, 'videos.html')



def contact(request):
    return render(request, 'contact.html')



def blog(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 6)  # Show 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog.html', {'posts': page_obj.object_list, 'page_obj': page_obj, 'paginator': paginator})




def blog_single(request, slug):
    post = get_object_or_404(Post, slug=slug)
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

    return render(request, 'single-blog.html', {'post': post, 'comments': comments, 'form': form})

   






    
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
    posts = Post.objects.all().order_by('-created_at')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    # Static pages
    static_views = [
        ('home', None),
        ('about', None),
        ('gallery', None),
        ('videos', None),
        ('contact', None),
        ('blog', None),
        ('dashboard', None),
        ('login', None),
        ('logout', None),
    ]
    for name, args in static_views:
        url = request.build_absolute_uri(reverse(name))
        xml += f'<url><loc>{url}</loc></url>\n'
    # Blog posts
    for post in posts:
        post_url = request.build_absolute_uri(reverse('post_detail', args=[post.slug]))
        xml += f'<url><loc>{post_url}</loc><lastmod>{post.updated_at.date()}</lastmod></url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')