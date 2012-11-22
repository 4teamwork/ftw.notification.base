from AccessControl.interfaces import IRoleManager
from ftw.notification.base.testing import FTW_NOTIFICATION_INTEGRATION_TESTING
from ftw.notification.base.utils import NotificationUtils
from unittest2 import TestCase


class TestUtils(TestCase):

    layer = FTW_NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestUtils, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder'))
        self.utils = NotificationUtils(self.folder)

    def test_has_anonymous_role(self):

        self.assertFalse(self.utils.has_anonymous_role())

        manager = IRoleManager(self.folder)
        manager.manage_role('Anonymous', permissions=['View'])

        self.assertTrue(self.utils.has_anonymous_role())

    def test_has_authenticated_role(self):

        self.assertFalse(self.utils.has_authenticaded_role())

        manager = IRoleManager(self.folder)
        manager.manage_role('Authenticated', permissions=['View'])

        self.assertTrue(self.utils.has_authenticaded_role())

    def tearDown(self):
        super(TestUtils, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['folder'])
