from ftw.builder import Builder
from ftw.builder import create
from ftw.notification.base.browser.views import NotificationForm
from ftw.notification.base.testing import FTW_N_BASE_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import getAdapter


class TestNotificationForm(TestCase):

    layer = FTW_N_BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.user1 = create(Builder('user').named('User', 'Nr1'))
        self.user2 = create(Builder('user').named('User', 'Nr2'))
        self.user3 = create(Builder('user').named('User', 'Nr3'))

        self.group1 = create(Builder('group')
            .with_groupid('group1')
            .titled('Group1')
            .with_members(self.user1, self.user2))

        self.group2 = create(Builder('group')
            .with_groupid('group2')
            .titled('Group2')
            .with_members(self.user2, self.user3))

    def test_get_users_of_group(self):
        view = NotificationForm(self.portal, self.portal.REQUEST)
        self.assertEquals('Nr1 User, Nr2 User',
                          view.get_users_for_group('group1'))
        self.assertEquals('Nr2 User, Nr3 User',
                          view.get_users_for_group('group2'))
