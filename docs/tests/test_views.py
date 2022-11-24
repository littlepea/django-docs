import os
from django.test import TestCase
from django.test.client import Client, RequestFactory

try:
    from django.core.urlresolvers import reverse
    # fix for python 3.6
except ImportError:
    from django.urls import reverse

from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.http import Http404
from docs import views

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

TEST_DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_docs'))


class DocsViewsTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.rf = RequestFactory()
        self.user = User(username='testuser')
        self.staff = User(username='teststaff')
        self.admin = User(username='testadmin')
        self.user.set_password('123')
        self.staff.set_password('123')
        self.admin.set_password('123')
        reload(views)


class A_DefaultSettingsTest(DocsViewsTestBase):
    def test_settings(self):
        self.assertEqual(views.DOCS_ROOT, None)
        self.assertEqual(views.DOCS_ACCESS, views.DOCS_ACCESS_CHOICES[0])

    def test_index_html(self):
        self.assertRaises(views.DocsRootSettingError, views.serve_docs, self.rf.request(), 'index.html')
        self.assertRaises(Http404, views.serve_docs, self.rf.request(), 'index.html',
                          document_root='wrong')


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS='wrong-value')
class B_IncorrectAccessTest(DocsViewsTestBase):
    def test_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertNotIn(views.DOCS_ACCESS, views.DOCS_ACCESS_CHOICES)

    def test_index_html(self):
        self.assertRaises(views.DocsAccessSettingError, views.serve_docs, self.rf.request(), 'index.html')


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS='public')
class C_PublicAccessTest(DocsViewsTestBase):
    def test_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertEqual(views.DOCS_ACCESS, 'public')
        self.assertEqual(views.DOCS_DIRHTML, False)

    def test_index_html(self):
        self.assertEqual(views.serve_docs(self.rf.request(), 'index.html').status_code, 200)

    def test_incorrect_path(self):
        self.assertRaises(Http404, views.serve_docs, self.rf.request(), 'wrong.html')
    
    def test_sub_directory_path(self):
        self.assertRaises(Http404, views.serve_docs, self.rf.request(), 'sub_dir/')
    
    def test_root_redirects(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/index.html")


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS='public', DOCS_DIRHTML=True)
class D_DIRHTMLTest(DocsViewsTestBase):
    def test_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertEqual(views.DOCS_ACCESS, 'public')
        self.assertEqual(views.DOCS_DIRHTML, True)

    def test_sub_directory_path_with_trailing_slash(self):
        self.assertEqual(views.serve_docs(self.rf.request(), 'sub_dir/').status_code, 200)
    
    def test_sub_directory_path_without_trailing_slash(self):
        self.assertEqual(views.serve_docs(self.rf.request(), 'sub_dir').status_code, 200)

    # This conflicts with the `test_root_redirects` above
    # def test_root_redirects(self):
    #     response = self.client.get("/")
    #     self.assertEqual(response.status_code, 200)


@override_settings(DOCS_ROOT=TEST_DOCS_ROOT, DOCS_ACCESS='login_required')
class E_LoginAccessTest(DocsViewsTestBase):
    def test_settings(self):
        self.assertEqual(views.DOCS_ROOT, TEST_DOCS_ROOT)
        self.assertEqual(views.DOCS_ACCESS, 'login_required')

    def test_index_html(self):
        request = self.rf.request()
        request.user = self.user
        response = views.serve_docs(request, 'index.html')
        self.assertEqual(response.status_code, 200)
