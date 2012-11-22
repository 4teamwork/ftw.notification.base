from Acquisition import aq_base, aq_parent, aq_inner
from ftw.notification.base.utils import NotificationUtils
from plone.principalsource.term import PrincipalTerm
from Products.CMFCore.utils import getToolByName
from zope import schema, component
from zope.app.component.hooks import getSite
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class EmailPrincipalTerm(PrincipalTerm):
    """Simple tokenized term used by SimpleVocabulary.
    Extended by email.
    """
    def __init__(self, value, type_, token=None, title=None, email=None):
        super(EmailPrincipalTerm,
              self).__init__(value, type_, token, title)
        if email is None:
            email = str(token)
        self.email = email


class PrincipalVocabulary(SimpleVocabulary):

    def __init__(self, userids, groupids):
        self.userids = userids
        self.groupids = groupids
        super(PrincipalVocabulary, self).__init__(tuple(self._get_terms()))

    def _get_terms(self):
        portal = getSite()
        acl_users = getToolByName(portal, 'acl_users')

        for userid in self.userids:
            user = acl_users.getUserById(userid)
            if user:
                fullname = user.getProperty('fullname', userid)
                if not fullname:
                    fullname = userid
                email = user.getProperty('email', '')
                if email:
                    yield EmailPrincipalTerm(userid,
                                             'user',
                                             token=userid,
                                             title=fullname,
                                             email=email)

        for groupid in self.groupids:
            group = acl_users.getGroupById(groupid)
            if group:
                title = group.getProperty('title')
                if not title:
                    title = groupid
                yield EmailPrincipalTerm(groupid,
                                    'group',
                                    token=groupid,
                                    title=title)

    def search(self, query_string):
        """search method for `z3c.formwidget.autocomplete` support. Returns
        all matching contacts.
        """

        query_string = isinstance(query_string, str) and \
            query_string.decode('utf8') or query_string
        query = query_string.lower().split(' ')
        for i, word in enumerate(query):
            query[i] = word.strip()

        for v in self:
            to_search = "%s %s" % (v.title, v.email)
            if self._compare(query, to_search):
                yield v

    def _compare(self, query, value):
        """ Compares each word in the query string seperate.
        Example:
        Given value: Zaphod Beeblebrox
        Query "za be" matches
        Query "be za" matches
        Query "phodbee" doesnt match (its not fuzzy matching yet)
        """
        if not value:
            return False
        value = isinstance(value, str) and \
            value.decode('utf8').lower() or value.lower()
        for word in query:
            lword = word.lower()
            if len(word) > 0 and lword not in value:
                return False
        return True


class NotificationUsersVocabulary(object):

    implements(IVocabularyFactory)

    def __init__(self):
        self.context = None

    def use_plone_principal_user_source(self):

        return bool(self.utils.has_anonymous_role()
                or self.utils.has_authenticaded_role())

    def __call__(self, context):
        self.context = context
        self.utils = NotificationUtils(self.context)

        gtool = getToolByName(self.context, 'portal_groups')
        allowed_roles_to_view = self.utils.roles_of_permission('View')

        if self.use_plone_principal_user_source():

            factory = component.getUtility(
                schema.interfaces.IVocabularyFactory,
                name='plone.principalsource.Principals',
                context=self.context)
            return factory(self.context)

        else:

            context = self.context

            users = set([])
            groups = set([])

            # Walk upwards until reach portal root or role acquire check fails
            portal = getToolByName(
                self.context, 'portal_url').getPortalObject()
            cont = True
            while cont:
                if context == portal:
                    break

                userroles = portal.acl_users._getLocalRolesForDisplay(context)

                # Use dict's to auto. prevent duplicated entries
                for user, roles, role_type, name in userroles:
                    if set(roles) & set(allowed_roles_to_view):
                        if role_type == u'group':
                            if user not in groups:
                                groups.add(name)
                        else:
                            if name not in users:
                                users.add(name)

                if getattr(aq_base(context), '__ac_local_roles_block__', None):
                    cont = False
                else:
                    context = aq_parent(aq_inner(context))

            # Go throught groups an add their containing users to the user list
            for groupid in groups:
                group = gtool.getGroupById(groupid)
                if group:
                    members = set(group.getGroupMemberIds())
                else:
                    continue
                # Put together
                users = users.union(members)

            return PrincipalVocabulary(users, groups)

NotificationUsersVocabularyFactory = NotificationUsersVocabulary()
