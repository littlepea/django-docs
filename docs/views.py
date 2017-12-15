from django.views.generic import RedirectView

try:
    from django.core.urlresolvers import reverse
except ModuleNotFoundError:
    from django.urls import reverse

from django.views.static import serve
from django.conf import settings
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.views import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext as _


def superuser_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, displaying the login page if necessary.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and request.user.is_superuser:
            # The user is valid. Continue to the admin page.
            return view_func(request, *args, **kwargs)

        assert hasattr(request, 'session'), "The Django admin requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        defaults = {
            'template_name': 'admin/login.html',
            'authentication_form': AdminAuthenticationForm,
            'extra_context': {
                'title': _('Log in'),
                'app_path': request.get_full_path(),
                REDIRECT_FIELD_NAME: request.get_full_path(),
                },
            }
        return login(request, **defaults)
    return _checklogin


def public(function=None):
    """
    Dummy decorator that doesn't check anything.
    """
    return function


class DocsAccessSettingError(ValueError):
    pass


class DocsRootSettingError(ValueError):
    pass


DOCS_ACCESS_CHOICES = (
    'public',
    'login_required',
    'staff',
    'superuser',
)
DOCS_ROOT = getattr(settings, 'DOCS_ROOT', None)
DOCS_ACCESS = getattr(settings, 'DOCS_ACCESS', DOCS_ACCESS_CHOICES[0])

if DOCS_ACCESS == 'public':
    decorator = public
elif DOCS_ACCESS == 'login_required':
    decorator = login_required
elif DOCS_ACCESS == 'staff':
    decorator = staff_member_required
elif DOCS_ACCESS == 'superuser':
    decorator = superuser_required
else:
    decorator = public


@decorator
def serve_docs(request, path, **kwargs):
    if DOCS_ACCESS not in DOCS_ACCESS_CHOICES:
        raise DocsAccessSettingError('DOCS_ACCESS setting value is incorrect: %s (choises are: %s)' % (
            DOCS_ACCESS,
            DOCS_ACCESS_CHOICES
        ))
    if 'document_root' not in kwargs and not DOCS_ROOT:
        raise DocsRootSettingError('DOCS_ROOT setting value is incorrect: %s (must be a valid path)' % DOCS_ROOT)
    if 'document_root' not in kwargs and DOCS_ROOT:
        kwargs['document_root'] = DOCS_ROOT
    return serve(request, path, **kwargs)


class DocsRootView(RedirectView):
    def get_redirect_url(self, **kwargs):
        return reverse('docs_files', kwargs={'path': 'index.html'})

