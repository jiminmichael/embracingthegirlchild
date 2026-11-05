import json
import re

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Post


class SeoMetadataTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='seo-author')

    def create_post(self, slug, status):
        return Post.objects.create(
            title=f'Test article {slug}',
            slug=slug,
            content='A useful article about girls education and wellbeing.',
            author=self.author,
            status=status,
        )

    def test_public_pages_have_canonical_social_and_description_metadata(self):
        for path in ('/', '/about/', '/gallery/', '/videos/', '/contact/', '/blog/'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<meta name="description"')
                self.assertContains(response, '<link rel="canonical"')
                self.assertContains(response, '<meta property="og:url"')
                self.assertContains(response, '<meta name="twitter:card"')
                self.assertContains(response, 'application/ld+json')

    def test_blog_post_has_post_specific_open_graph_and_article_schema(self):
        post = self.create_post('published-article', 'published')

        response = self.client.get(f'/blog/{post.slug}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<meta property="og:title" content="{post.title}')
        self.assertContains(
            response,
            f'<meta property="og:url" content="https://www.embracingthegirlchild.org.ng/blog/{post.slug}/"',
        )
        schema_blocks = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            response.content.decode(),
            re.DOTALL,
        )
        schemas = [json.loads(block) for block in schema_blocks]
        article_schema = next(schema for schema in schemas if schema.get('@type') == 'Article')
        self.assertEqual(article_schema['headline'], post.title)

    def test_drafts_are_not_publicly_listed_rendered_or_sitemapped(self):
        published = self.create_post('published-article', 'published')
        draft = self.create_post('draft-article', 'draft')

        blog_response = self.client.get('/blog/')
        home_response = self.client.get('/')
        sitemap_response = self.client.get('/sitemap.xml')

        self.assertContains(blog_response, published.title)
        self.assertNotContains(blog_response, draft.title)
        self.assertNotContains(home_response, draft.title)
        self.assertContains(sitemap_response, published.slug)
        self.assertNotContains(sitemap_response, draft.slug)
        self.assertNotContains(sitemap_response, '/dashboard/')
        self.assertEqual(self.client.get(f'/blog/{draft.slug}/').status_code, 404)

    def test_robots_txt_references_sitemap_and_excludes_private_routes(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sitemap: https://www.embracingthegirlchild.org.ng/sitemap.xml')
        self.assertContains(response, 'Disallow: /dashboard/')
