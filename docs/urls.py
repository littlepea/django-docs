from django.conf.urls import url
from docs.views import DocsRootView, serve_docs


urlpatterns = [
    url(r'^$', DocsRootView.as_view(permanent=True), name='docs_root'),
    url(r'^(?P<path>.*)$', serve_docs, name='docs_files'),
]
