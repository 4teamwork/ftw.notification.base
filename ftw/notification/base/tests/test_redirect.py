from ftw.builder import Builder
from ftw.builder import create
from ftw.notification.base.testing import FTW_N_BASE_FUNCTIONAL_TESTING
from unittest2 import TestCase
from Products.Five import BrowserView
from ftw.testbrowser.tests.helpers import register_view
from ftw.testbrowser import browsing
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class RedirectView(BrowserView):

    def __call__(self):
        contents = self.context.getFolderContents()
        obj = contents[0].getObject()
        if 'notification_form' not in self.request.get('HTTP_REFERER'):
            return self.request.response.redirect(obj.absolute_url() +
                                                  '/notification_form')
        else:
            return 'success'


class TestRedirect(TestCase):

    layer = FTW_N_BASE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        self.folder = create(Builder('folder'))
        self.file = create(Builder('file').within(self.folder))
        self.user1 = create(Builder('user').named('User', 'Nr1'))

    @browsing
    def test_redirect(self, browser):
        with register_view(RedirectView, 'redirect_view'):
            browser.login().visit(self.folder, view="redirect_view")
            browser.fill({"to_list:list": 'user.nr1',
                          "comment": "blabla"}).submit()

            self.assertEquals('success', browser.contents)
            self.assertEquals('http://nohost/plone/folder/redirect_view',
                              browser.url)

    @browsing
    def test_no_referer(self, browser):
        with register_view(RedirectView, 'redirect_view'):
            browser.login().visit(self.file, view="notification_form")
            browser.fill({"to_list:list": 'user.nr1',
                          "comment": "blabla"}).submit()
            self.assertEquals(
                'http://nohost/plone/folder/file/notification_form',
                browser.url)
