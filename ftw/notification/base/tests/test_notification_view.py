from AccessControl.interfaces import IRoleManager
from ftw.notification.base.testing import FTW_NOTIFICATION_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import queryMultiAdapter


class TestNotificationView(TestCase):

    layer = FTW_NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestNotificationView, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder'))
        # Fire all necessary events
        self.folder.processForm()

        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember('user1', 'user1',
                          properties={'username': 'user1',
                                      'fullname': 'fullname1',
                                      'email': 'user1@email.com'})
        regtool.addMember('user2', 'user2',
                          properties={'username': 'user2',
                                      'fullname': 'fullname2',
                                      'email': 'user2@email.com'})

        self.groups_tool = getToolByName(self.portal, 'portal_groups')
        self.groups_tool.addGroup('group1')
        self.groups_tool.editGroup('group1', title=u'Group 1')
        self.groups_tool.addGroup('group2')
        self.groups_tool.editGroup('group2', title=u'Group 2')

    def test_view_registered(self):
        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")
        self.assertIsNotNone(view)

    def test_json_source_users(self):
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Manager",
            reindex=True)

        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            '{"id": "user1", "name": "fullname1 &lt;user1@email.com&gt;"}',
            view.json_source())
        self.assertIn(
            '{"id": "user2", "name": "fullname2 &lt;user2@email.com&gt;"}',
            view.json_source())

    def test_json_source_groups(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.folder.manage_addLocalRoles('group2', ['Manager'])

        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            '{"id": "group:group1", "name": "Group 1"}',
            view.json_source())
        self.assertIn(
            '{"id": "group:group2", "name": "Group 2"}',
            view.json_source())

    def test_json_source_users_plone_principal(self):
        manager = IRoleManager(self.folder)
        manager.manage_role('Anonymous', permissions=['View'])

        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            '{"id": "user1", "name": "fullname1 &lt;user1@email.com&gt;"}',
            view.json_source())
        self.assertIn(
            '{"id": "user2", "name": "fullname2 &lt;user2@email.com&gt;"}',
            view.json_source())
        self.assertIn(
            '{"id": "group:group1", "name": "Group 1"}',
            view.json_source())
        self.assertIn(
            '{"id": "group:group2", "name": "Group 2"}',
            view.json_source())

    def test_json_source_by_group_no_id(self):
        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")
        self.assertEquals("[]", view.json_source_by_group())

    def test_json_source_by_group(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")
        self.groups_tool.addPrincipalToGroup('user2', "group1")

        self.folder.REQUEST.set('groupid', 'group1')
        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            '{"id": "user1", "name": "fullname1 &lt;user1@email.com&gt;"}',
            view.json_source_by_group())
        self.assertIn(
            '{"id": "user2", "name": "fullname2 &lt;user2@email.com&gt;"}',
            view.json_source_by_group())

    def tearDown(self):
        super(TestNotificationView, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['folder'])
