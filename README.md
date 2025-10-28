Embracing the Girl Child Initiative — Django Project

Overview
--------
This repository contains a Django website for "Embracing the Girl Child Initiative" (EGCI). It provides an informational front-facing site (home, about, blog, gallery, videos, contact) and an authenticated admin dashboard where site maintainers can manage blog posts. The dashboard supports server-driven filtering, pagination, and AJAX-powered modal create/edit/delete operations for a smooth, no-page-reload experience.

Quick features
--------------
- Public pages: Home, About, Blog listing, Blog detail, Gallery, Videos, Contact.
- Authenticated dashboard at `/dashboard/` for managing posts.
- Post model includes: title, slug, content, image, author, created_at, updated_at, category, status, views.
- Post CRUD in dashboard:
  - Create & Edit in a modal using AJAX (no full page reload)
  - Delete via AJAX (row removed without reload)
  - Server-side filtering (status/category)
  - Server-side pagination (10 posts per page), with AJAX fetching of page fragments
- Comment model (for blog posts) with a simple form on post detail pages.

Requirements
------------
- Python 3.8+ (tested with 3.11+)
- Django 4.x (or compatible)
- Pillow (for image uploads)
- A virtual environment is strongly recommended

Setup (Windows cmd)
-------------------
Open a Command Prompt in the project root (where `manage.py` sits).

1. Create and activate a virtual environment (recommended):

```cmd
py -3 -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies (create a `requirements.txt` if you want to pin them):

```cmd
pip install django pillow
```

3. Configure settings if needed:
- Open `embracingmain/settings.py` and ensure `INSTALLED_APPS` includes `'main'`.
- Set `DEBUG = True` for development and configure `ALLOWED_HOSTS` when deploying.
- Configure `MEDIA_ROOT` and `MEDIA_URL` for image uploads, for example:

```py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

4. Make migrations and migrate: (required after adding new fields to Post)

```cmd
py -3 manage.py makemigrations
py -3 manage.py migrate
```

5. Create a superuser (for dashboard login):

```cmd
py -3 manage.py createsuperuser
```

6. Run the development server:

```cmd
py -3 manage.py runserver
```

Open your browser at http://127.0.0.1:8000/dashboard/ and log in with the created user.

How the dashboard works (developer notes)
----------------------------------------
- `main/views.py`:
  - `dashboard` view supports GET params `status`, `category`, and `page`. If the request has `X-Requested-With: XMLHttpRequest`, the view returns an HTML fragment containing the table body and pagination controls (rendered by `main/templates/partials/_posts_table.html`).
  - `post_new` and `post_edit` accept POST (and file uploads) and return JSON on AJAX calls with a rendered row HTML snippet (`partials/_post_row.html`) so the front-end can insert or replace rows without reloading.
  - `post_delete` returns JSON {success: true} for AJAX POST delete requests.

- Templates:
  - `main/templates/dashboard.html` contains client-side JS to:
    - open the modal for create/edit
    - submit the modal form via `fetch` using `FormData`
    - fetch table fragments for filters/pagination (using `X-Requested-With` header to indicate AJAX)
    - intercept delete form submissions in the table and perform AJAX deletes
  - `partials/_post_row.html` is used to generate a single table row for AJAX responses.
  - `partials/_posts_table.html` renders the table body and simple previous/next buttons.

Notes on AJAX flow
------------------
- Create/Edit: modal submits FormData to `/post/new/` or `/post/<slug>/edit/`. On success the server returns `{'success': True, 'html': '<tr id="post-row-...">...</tr>'}`. The front-end inserts or updates the row in the DOM and shows a toast notification.
- Delete: delete form posts to `/post/<slug>/delete/`. The view returns JSON for AJAX, and the front-end removes the row on success.

Testing the AJAX flows
----------------------
- Use the dashboard UI to add, edit, delete posts. Monitor the browser console for errors.
- If uploads fail, ensure `MEDIA_ROOT` exists and Django is configured to serve media in development (add to `urls.py`):

```py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Troubleshooting
---------------
- CSRF errors when using fetch: make sure the forms include `{% csrf_token %}` and the front-end sends the cookie. The current delete handler reads the csrf token from the inline form.
- If AJAX returns HTML instead of JSON on create/edit: ensure the request includes header `X-Requested-With: 'XMLHttpRequest'`. The dashboard JS sets that header.
- If migrations fail: check for uncommitted model changes, run `makemigrations`, and inspect the generated migration.

Security & Deployment notes
---------------------------
- For production, set `DEBUG = False` and configure `ALLOWED_HOSTS`.
- Use a proper media file server (S3, nginx etc.) for uploaded images.
- Use HTTPS and configure secure cookies.
- Consider adding permissions so only certain users can create/edit posts.

Recommended next improvements
-----------------------------
- Add unit tests for AJAX create/edit/delete and server-side filtering/pagination.
- Replace repetitive template code (nav/footer) with a `base.html` and template inheritance.
- Add server-side search and sorting for the dashboard.
- Improve accessibility for modal dialogs (focus trap, ARIA attributes).
- Implement optimistic undo for delete (temporary soft-delete + undo via AJAX).

Contact / Contributors
----------------------
This README was generated by the developer assistant during a refactor. For questions about the repository structure or to request further changes, update the issue tracker or contact the original project maintainers.
