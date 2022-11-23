"""
This ``urls.py`` is only used when running the tests via ``runtests.py``.
As you know, every app must be hooked into yout main ``urls.py`` so that
you can actually reach the app's views (provided it has any views, of course).

"""
from django.urls.conf import include, re_path


urlpatterns = [
    re_path(r'^', include('docs.urls')),
]
