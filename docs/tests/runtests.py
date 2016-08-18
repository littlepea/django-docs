#!/usr/bin/env python
"""
This script is a trick to setup a fake Django environment, since this reusable
app will be developed and tested outside any specifiv Django project.

Via ``settings.configure`` you will be able to set all necessary settings
for your app and run the tests as if you were calling ``./manage.py test``.

"""
import os
import sys

from django.conf import settings

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
]
INTERNAL_APPS = [
    'django_nose',
    'docs',
]
INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]
COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

if not settings.configured:
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=INSTALLED_APPS,
        ROOT_URLCONF='docs.tests.urls',
        TEMPLATE_DIRS=(
            os.path.join(os.path.dirname(__file__), '../../templates'),
        ),
        COVERAGE_MODULE_EXCLUDES=COVERAGE_MODULE_EXCLUDES,
        COVERAGE_REPORT_HTML_OUTPUT_DIR=os.path.join(
            os.path.dirname(__file__), 'coverage'),
        USE_TZ=True,
        PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',),
    )


from django_nose import NoseTestSuiteRunner


class NoseCoverageTestRunner(NoseTestSuiteRunner):
    """Custom test runner that uses nose and coverage"""
    pass


def runtests(*test_args):
    failures = NoseCoverageTestRunner(verbosity=2, interactive=True).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
