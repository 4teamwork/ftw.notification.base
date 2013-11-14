from ftw.builder import Builder
from ftw.builder import create
from ftw.notification.base.events.handlers import add_group_members
from ftw.notification.base.testing import FTW_N_BASE_INTEGRATION_TESTING
from unittest2 import TestCase


class TestByline(TestCase):

    layer = FTW_N_BASE_INTEGRATION_TESTING

    def setUp(self):
        self.user1 = create(Builder('user'))
        self.user2 = create(Builder('user').named('User', 'Nr2'))

        self.group = create(Builder('group')
                            .titled('Group1')
                            .with_members(self.user1))

        self.group_nested = create(Builder('group')
                                   .titled('Group2 nested')
                                   .with_members(self.user2))

        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.gm = self.portal.acl_users.source_groups

    def test_resolve_group(self):
        key = 'to_list_group'
        self.request.set(key, [self.group.getId()])

        add_group_members(self.portal, 'to_list')

        self.assertEquals([self.user1.getId()], self.request.get('to_list'))

    def test_resolve_nested_groups(self):
        self.gm.addPrincipalToGroup(self.group_nested.getId(),
                                    self.group.getId())

        key = 'to_list_group'
        self.request.set(key, [self.group.getId(), ])

        add_group_members(self.portal, 'to_list')

        self.assertListEqual([self.user2.getId(), self.user1.getId()],
                          self.request.get('to_list'))
