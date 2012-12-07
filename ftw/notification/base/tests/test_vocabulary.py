from AccessControl.interfaces import IRoleManager
from ftw.notification.base.testing import FTW_NOTIFICATION_INTEGRATION_TESTING
from ftw.notification.base.vocabularies import PrincipalVocabulary
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.schema.vocabulary import getVocabularyRegistry


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
                                      'fullname': 'f\xc3\xbcllname1',
                                      'email': 'user1@email.com'})
        regtool.addMember('user2', 'user2',
                          properties={'username': 'user2',
                                      'fullname': 'f\xc3\xbcllname2',
                                      'email': 'user2@email.com'})
        regtool.addMember('user3', 'user3',
                          properties={'username': 'user3',
                                      'fullname': 'f\xc3\xbcllname3',
                                      'email': 'user3@email.com'})
        regtool.addMember('user4', 'user4',
                          properties={'username': 'user4',
                                      'fullname': 'f\xc3\xbcllname4',
                                      'email': 'user4@email.com'})
        regtool.addMember('user5', 'user5')

        # Set up groups
        self.groups_tool = getToolByName(self.portal, 'portal_groups')
        self.groups_tool.addGroup('group1')
        self.groups_tool.editGroup('group1', title=u'Group 1')
        self.groups_tool.addGroup('group2')

    def test_utility_registered(self):
        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')
        self.assertIsNotNone(vocabulary)

    def test_principal_vocabulary_get_terms(self):
        # User
        terms = tuple(PrincipalVocabulary(['user1'], [])._get_terms())
        self.assertEquals(terms[0].token, 'user1')
        self.assertEquals(terms[0].title, 'f\xc3\xbcllname1')
        self.assertEquals(terms[0].type, 'user')
        self.assertEquals(terms[0].value, 'user1')
        self.assertEquals(terms[0].email, 'user1@email.com')

        # Group
        terms = tuple(PrincipalVocabulary([],
                                          ['group1', 'group2'])._get_terms())
        self.assertEquals(terms[0].token, 'group1')
        self.assertEquals(terms[0].title, 'Group 1')
        self.assertEquals(terms[0].type, 'group')
        self.assertEquals(terms[0].value, 'group1')

        # Test fallback if there is no title on the group
        self.assertEquals(terms[1].title, 'group2')

    def test_invalid_user(self):
        # User without fullname and email
        terms = tuple(PrincipalVocabulary(['user5'], [])._get_terms())
        self.assertEquals(len(terms), 0)

    def test_user_group_not_exist(self):
        terms = tuple(PrincipalVocabulary(
            ['dummy'],
            ['dummy'])._get_terms())
        self.assertEquals(len(terms), 0)

    def test_principal_vocabulary_search(self):
        # Search for fullname
        terms = tuple(PrincipalVocabulary(
            ['user1', 'user2'], []).search('f\xc3\xbcllname1'))
        self.assertEquals(len(terms), 1)
        self.assertEquals(terms[0].token, 'user1')

        # Search for email
        terms = tuple(PrincipalVocabulary(
            ['user1', 'user2'], []).search('@email.com'))
        self.assertEquals(len(terms), 2)
        self.assertEquals(terms[0].token, 'user1')
        self.assertEquals(terms[1].token, 'user2')

        # no result
        terms = tuple(PrincipalVocabulary([], []).search('f\xc3\xbcllname1'))
        self.assertEquals(len(terms), 0)

    def test_principal_vocabulary_compair(self):
        func = PrincipalVocabulary([], [])._compare
        value = "Zaphod Beeblebrox"

        # Some working cases
        self.assertTrue(func(['Za', 'Be'], value))
        self.assertTrue(func(['za', 'be'], value))
        self.assertTrue(func(['Be', 'Za'], value))
        self.assertTrue(func(['Zaphod'], value))
        self.assertTrue(func(['Zap'], value))
        self.assertTrue(func(['Beeblebrox'], value))
        self.assertTrue(func(['Beeb'], value))

        # No fuzzy matching
        self.assertFalse(func(['odbee'], value))

        # Does not match
        self.assertFalse(func(['dummy'], value))

        #Empty
        self.assertTrue(func([], value))

        # No value
        self.assertFalse(func(['dummy'], ''))

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
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Owner",
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

    def test_block_local_roles(self):
        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1', 'user2'],
            member_role="Manager",
            reindex=True)
        setattr(self.subfolder, '__ac_local_roles_block__', True)
        self.portal.portal_membership.setLocalRoles(
            obj=self.subfolder,
            member_ids=['user3', 'user4'],
            member_role="Manager",
            reindex=True)

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user3', 'user4']),
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
        self.assertEquals(set(['user1', 'user2', 'group1']),
                      set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.folder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_group_inherited_roles(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")
        self.groups_tool.addPrincipalToGroup('user2', "group1")

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')
        self.assertEquals(set(['user1', 'user2', 'group1']),
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
                               'group1', 'group2']),
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
                       'group1', 'group2']),
              set([item.token for item in vocabulary]))

        # Control
        vocabulary = getVocabularyRegistry().get(
            self.subfolder2,
            'ftw.notification.base.users')
        self.assertEquals([], [item.token for item in vocabulary])

    def test_inextisting_user_and_group(self):
        self.folder.manage_addLocalRoles('dummy_id', ['Manager'])

        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')

        self.assertEquals(set([]),
              set([item.token for item in vocabulary]))

    def test_duplicate_local_roles(self):
        self.folder.manage_addLocalRoles('group1', ['Manager'])
        self.groups_tool.addPrincipalToGroup('user1', "group1")

        self.portal.portal_membership.setLocalRoles(
            obj=self.folder,
            member_ids=['user1'],
            member_role="Manager",
            reindex=True)

        self.subfolder.manage_addLocalRoles('group1', ['Manager'])
        self.portal.portal_membership.setLocalRoles(
            obj=self.subfolder,
            member_ids=['user1'],
            member_role="Manager",
            reindex=True)

        vocabulary = getVocabularyRegistry().get(
            self.subfolder,
            'ftw.notification.base.users')

        self.assertEquals(set(['user1', 'group1']),
              set([item.token for item in vocabulary]))

    def test_anonym_accessable_content(self):
        manager = IRoleManager(self.folder)
        manager.manage_role('Anonymous', permissions=['View'])

        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')

        self.assertEquals(set(['user1', 'user2', 'user3', 'user4',
                               'test_user_1_', 'user5', 'group1', 'group2',
                               'Reviewers', 'Site Administrators',
                               'Administrators', 'AuthenticatedUsers']),
                      set([item.token for item in vocabulary]))

    def test_authenticated_accessable_content(self):
        manager = IRoleManager(self.folder)
        manager.manage_role('Authenticated', permissions=['View'])

        vocabulary = getVocabularyRegistry().get(
            self.folder,
            'ftw.notification.base.users')

        self.assertEquals(set(['user1', 'user2', 'user3', 'user4',
                               'test_user_1_', 'user5', 'group1', 'group2',
                               'Reviewers', 'Site Administrators',
                               'Administrators', 'AuthenticatedUsers']),
                      set([item.token for item in vocabulary]))

    def tearDown(self):
        super(TestVocabulary, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['folder', 'folder2'])
