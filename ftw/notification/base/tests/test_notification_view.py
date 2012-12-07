from AccessControl.interfaces import IRoleManager
from ftw.notification.base.browser.notification import extract_email
from ftw.notification.base.browser.notification import validmails
from ftw.notification.base.browser.notification import to_utf8
from ftw.notification.base.testing import FTW_NOTIFICATION_FUNCTIONAL_TESTING
from ftw.notification.base.testing import FTW_NOTIFICATION_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import queryMultiAdapter
import transaction
import json


class TestNotificationViewUnit(TestCase):

    def test_extract_email(self):
        data = 'user1@email.com,user2@email.com,user3@email.com'
        self.assertEquals(
            extract_email(data),
            ['user1@email.com', 'user2@email.com', 'user3@email.com'])
        self.assertEquals(extract_email(''), [])

    def test_validmails(self):
        data = ['user1@email.com', 'user2@email.com', 'user3@email.com']
        self.assertEquals(data, validmails(data))

        data = ['@email.com', 'user2@email.com', 'user3@email.com']
        self.assertEquals(['user2@email.com', 'user3@email.com'],
                          validmails(data))

        data = ['@email.com', 'user2@email', 'user3']
        self.assertEquals([],
                          validmails(data))

    def test_to_utf8(self):
        # UTF8
        data = 'f\xc3\xbcllname'
        self.assertEquals(data, to_utf8(data))

        # Unicode
        data = u'f\xfcllname'
        self.assertNotEquals(data, to_utf8(data))
        self.assertEquals('f\xc3\xbcllname', to_utf8(data))


class TestNotificationViewIntegration(TestCase):

    layer = FTW_NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestNotificationViewIntegration, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder'))
        # Fire all necessary events
        self.folder.processForm()

        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember('user1', 'user1',
                          properties={'username': 'user1',
                                      'fullname': 'f\xc3\xbcllname1',
                                      'email': 'user1@email.com'})
        regtool.addMember('user2', 'user2',
                          properties={'username': 'user2',
                                      'fullname': 'f\xc3\xbcllname2',
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
            json.loads('{"id": "user1@email.com", "text": "f\xc3\xbcllname1 '
            '[user1@email.com]"}'),
            json.loads(view.json_source()))
        self.assertIn(
            json.loads('{"id": "user2@email.com", "text": "f\xc3\xbcllname2 '
            '[user2@email.com]"}'),
            json.loads(view.json_source()))

    def test_json_source_groups(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.folder.manage_addLocalRoles('group2', ['Manager'])

        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            json.loads('{"id": "group:group1", "text": "Group 1"}'),
            json.loads(view.json_source()))
        self.assertIn(
            json.loads('{"id": "group:group2", "text": "Group 2"}'),
            json.loads(view.json_source()))

    def test_json_source_users_plone_principal(self):
        manager = IRoleManager(self.folder)
        manager.manage_role('Anonymous', permissions=['View'])

        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            json.loads('{"id": "user1@email.com", "text": "f\xc3\xbcllname1 '
            '[user1@email.com]"}'),
            json.loads(view.json_source()))
        self.assertIn(
            json.loads('{"id": "user2@email.com", "text": "f\xc3\xbcllname2 '
            '[user2@email.com]"}'),
            json.loads(view.json_source()))
        self.assertIn(
            json.loads('{"id": "group:group1", "text": "Group 1"}'),
            json.loads(view.json_source()))
        self.assertIn(
            json.loads('{"id": "group:group2", "text": "Group 2"}'),
            json.loads(view.json_source()))

    def test_json_source_users_plone_principal_search(self):
        manager = IRoleManager(self.folder)
        manager.manage_role('Anonymous', permissions=['View'])
        self.folder.REQUEST.set('q', 'f\xc3\xbcllname1')
        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")

        self.assertIn(
            json.loads('{"id": "user1@email.com", "text": "f\xc3\xbcllname1 '
            '[user1@email.com]"}'),
            json.loads(view.json_source()))

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
            json.loads('{"id": "user1", "text": "f\xc3\xbcllname1 '
                       '[user1@email.com]"}'),
            json.loads(view.json_source_by_group()))
        self.assertIn(
            json.loads('{"id": "user2", "text": "f\xc3\xbcllname2 '
                       '[user2@email.com]"}'),
            json.loads(view.json_source_by_group()))

    def test_json_pre_select(self):
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Manager",
            reindex=True)

        view = queryMultiAdapter((self.folder, self.folder.REQUEST),
                                 name="notification_form")
        view.pre_select = ['user1', 'user2', 'user3']
        self.assertIn(
            json.loads('{"id": "user1@email.com", "text": "f\xc3\xbcllname1 '
            '[user1@email.com]"}'),
            json.loads(view.json_pre_select()))
        self.assertIn(
            json.loads('{"id": "user2@email.com", "text": "f\xc3\xbcllname2 '
            '[user2@email.com]"}'),
            json.loads(view.json_pre_select()))
        # user3 is not in vocabulary
        self.assertNotIn('user3', view.json_pre_select())

    def tearDown(self):
        super(TestNotificationViewIntegration, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['folder'])


class TestNotificationViewFunctional(TestCase):

    layer = FTW_NOTIFICATION_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNotificationViewFunctional, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder'))
        # Fire all necessary events
        self.folder.processForm()

        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember('user1', 'user1',
                          properties={'username': 'user1',
                                      'fullname': 'f\xc3\xbcllname1',
                                      'email': 'user1@email.com'})
        regtool.addMember('user2', 'user2',
                          properties={'username': 'user2',
                                      'fullname': 'f\xc3\xbcllname2',
                                      'email': 'user2@email.com'})

        transaction.commit()

        # Browser setup
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

    def test_form(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD, ))

        url = self.folder.absolute_url() + '/notification_form'
        self.browser.open(url)

        # Sent empty form
        self.browser.getControl('Send').click()
        # Stay on form
        self.assertEquals(self.browser.url, url)

        # Send only cc
        self.browser.getControl(
            name='users-cc').value = "user1@email.com,user2@email.com"
        self.browser.getControl('Send').click()
        # Stay on form
        self.assertEquals(self.browser.url, url)

        # Invalid email
        self.browser.getControl(
            name='users-to').value = "user1@email.com,invalidaddr"
        self.browser.getControl('Send').click()
        # Stay on form
        self.assertEquals(self.browser.url, url)

        # Valid email addresses
        self.browser.getControl(
            name='users-to').value = "user1@email.com,user2@email.com"
        self.browser.getControl(
            name='users-cc').value = "user3@email.com,user4@email.com"
        self.browser.getControl('Send').click()
        # Redirect to content
        self.assertEquals(self.browser.url, self.folder.absolute_url())

    def tearDown(self):
        super(TestNotificationViewFunctional, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['folder'])
        transaction.commit()
