from django.conf.urls import re_path
from docs.views import DocsRootView, serve_docs, DOCS_DIRHTML

urlpatterns = []

if not DOCS_DIRHTML:
    urlpatterns += [
        re_path(r'^$', DocsRootView.as_view(permanent=True), name='docs_root'),
    ]

urlpatterns += [
    re_path(r"^(?P<path>.*)$", serve_docs, name="docs_files"),
]
