from ftw.notification.base.testing import FTW_NOTIFICATION_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import queryMultiAdapter


class TestAddressBlockCreation(TestCase):

    layer = FTW_NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestAddressBlockCreation, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder'))
        # Fire all necessary events
        self.folder.processForm()

    def test_view_registered(self):
        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_view")
        self.assertIsNotNone(view)
