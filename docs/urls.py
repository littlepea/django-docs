from django.conf.urls import url
from docs.views import DocsRootView, serve_docs, DOCS_DIRHTML

urlpatterns = []

if not DOCS_DIRHTML:
    urlpatterns += [
        url(r'^$', DocsRootView.as_view(permanent=True), name='docs_root'),
    ]

urlpatterns += [
    url(r"^(?P<path>.*)$", serve_docs, name="docs_files"),
]
