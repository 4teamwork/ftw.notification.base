from ftw.notification.base.testing import FTW_NOTIFICATION_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.schema.vocabulary import getVocabularyRegistry
from Products.CMFCore.utils import getToolByName


class TestVocabulary(TestCase):

    layer = FTW_NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestVocabulary, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        # Set up a site structure
        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder'))
        self.subfolder = self.folder.get(
            self.folder.invokeFactory('Folder', 'subfolder'))

        self.folder2 = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder2'))
        self.subfolder2 = self.folder2.get(
            self.folder2.invokeFactory('Folder', 'subfolder2'))

        # Set up some user an groups
        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember('user1', 'user1',
                          properties={'username': 'user1',
                                      'fullname': 'fullname1',
                                      'email': 'user1@email.com'})
        regtool.addMember('user2', 'user2',
                          properties={'username': 'user2',
                                      'fullname': 'fullname2',
                                      'email': 'user2@email.com'})
        regtool.addMember('user3', 'user3',
                          properties={'username': 'user3',
                                      'fullname': 'fullname3',
                                      'email': 'user3@email.com'})
        regtool.addMember('user4', 'user4',
                          properties={'username': 'user4',
                                      'fullname': 'fullname4',
                                      'email': 'user4@email.com'})
        # Set up groups
        self.groups_tool = getToolByName(self.portal, 'portal_groups')
        self.groups_tool.addGroup('group1')
        self.groups_tool.addGroup('group2')

    def test_utility_registered(self):
        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')
        self.assertIsNotNone(vocabulary)

    def test_local_roles(self):
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Manager",
            reindex=True)

        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2']),
                          set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.folder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_inherited_roles(self):
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Manager",
            reindex=True)

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2']),
                          set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.folder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_inherited_and_local_roles(self):
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Manager",
            reindex=True)
        self.portal.portal_membership.setLocalRoles(
            obj=self.subfolder,
            member_ids=['user3', 'user4'],
            member_role="Manager",
            reindex=True)

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2', 'user3', 'user4']),
                          set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.subfolder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_group_local_roles(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")
        self.groups_tool.addPrincipalToGroup('user2', "group1")

        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2', 'group:group1']),
                      set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_group_inherited_roles(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")
        self.groups_tool.addPrincipalToGroup('user2', "group1")

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2', 'group:group1']),
                      set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.subfolder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_group_inherited_and_local_roles(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")
        self.groups_tool.addPrincipalToGroup('user2', "group1")

        self.subfolder.manage_addLocalRoles('group2', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user3', "group2")
        self.groups_tool.addPrincipalToGroup('user4', "group2")

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2', 'user3', 'user4',
                               'group:group1', 'group:group2']),
                      set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.subfolder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_mixed_compination(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")

        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user2'],
            member_role="Manager",
            reindex=True)

        self.subfolder.manage_addLocalRoles('group2', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user3', "group2")

        self.portal.portal_membership.setLocalRoles(
            obj=self.subfolder,
            member_ids=['user4'],
            member_role="Manager",
            reindex=True)

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')

        self.assertEquals(set(['user1', 'user2', 'user3', 'user4',
                       'group:group1', 'group:group2']),
              set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.subfolder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def tearDown(self):
        super(TestVocabulary, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['folder', 'folder2'])
