from AccessControl.Permission import Permission
from AccessControl.interfaces import IRoleManager
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.workflow.interfaces import ISharingPageRole
from zope import schema, component
from zope.app.component.hooks import getSite
from zope.component import getUtilitiesFor
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl


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
                    yield self.__class__.createTerm(userid,
                                                    str(email),
                                                    fullname)

        for groupid in self.groupids:
            group = acl_users.getGroupById(groupid)
            if group:
                title = group.getProperty('title')
                if not title:
                    title = groupid
                groupid = 'group:%s' % (groupid)
                yield self.__class__.createTerm(groupid, str(groupid), title)

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
            if self._compare(query, v.title):
                yield v

    def _compare(self, query, value):
        """ Compares each word in the query string seperate.

        Example 1:
        Given value: Hugo Boss
        Query "hu bo" matches
        Query "bo hu" matches
        Query "boh" doesnt match (its not fuzzy matching yet)
        Query "hub" doesnt match

        Example 2:
        Given value: Eingangskorb Mandant 1
        Query "m 1" matches
        Query "m 1 eing" matches
        Query "m1" doesnt match
        """

        if not value:
            return False
        value = isinstance(value, str) and \
            value.decode('utf8').lower() or value.lower()
        for word in query:
            if len(word) > 0 and word not in value:
                return False
        return True


class NotificationUsersVocabulary(object):

    implements(IVocabularyFactory)

    def roles_of_permission(self, permission):
        """Return all roles wich have the given permission
        on the current context."""

        role_manager = IRoleManager(self.context)
        for p in role_manager.ac_inherited_permissions(1):
            name, value = p[:2]
            if name == permission:
                p = Permission(name, value, role_manager)
                roles = p.getRoles()
                return roles

    def __call__(self, context):
        self.context = context

        gtool = getToolByName(self.context, 'portal_groups')
        allowed_roles_to_view = self.roles_of_permission('View')

        if 'Anonymous' in allowed_roles_to_view \
                or 'Authenticated' in allowed_roles_to_view:

            factory = component.getUtility(
                schema.interfaces.IVocabularyFactory,
                name='plone.principalsource.Users',
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
                        if role_type == u'user':
                            if name not in users:
                                users.add(name)
                        elif role_type == u'group':
                            if user not in groups:
                                groups.add(name)

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


class AvailableUsersVocabulary(object):
    """
    lists all available users

    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        """this utility calls plone.principalsource.Users utility
        so we can overwrite this one if we want a diffrent source.
        """
        if context is None:
            context = getSite()
        factory = component.queryUtility(
            schema.interfaces.IVocabularyFactory,
            name='assignable_users',
            context=context)

        if factory is None:
            factory = component.getUtility(
                schema.interfaces.IVocabularyFactory,
                name='plone.principalsource.Users',
                context=context)
            items = factory(context)
        else:
            items = factory(context, membersonly=True)

        return items

AvailableUsersVocabularyFactory = AvailableUsersVocabulary()


class AvailableGroupsVocabulary(object):
    """
    lists all available groups

    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        """this utility calls plone.principalsource.Groups utility
        so we can overwrite this one if we want a diffrent source.
        """
        if context is None:
            context = getSite()

        factory = component.getUtility(
            schema.interfaces.IVocabularyFactory,
            name='plone.principalsource.Groups',
            context=context)
        items = factory(context)

        # check permission
        result = []

        gtool = getToolByName(context, 'portal_groups')

        items = []

        # Change SecurityManager - otherwise we dont receive all users form
        # existing_role_settings
        _old_security_manager = AccessControl.getSecurityManager()
        _new_user = AccessControl.SecurityManagement.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(
            context.REQUEST,
            _new_user)
        try:
            sharing = context.restrictedTraverse('@@sharing')
            items = sharing.existing_role_settings()
        except:
            AccessControl.SecurityManagement.setSecurityManager(
                _old_security_manager)
            raise
        else:
            AccessControl.SecurityManagement.setSecurityManager(
                _old_security_manager)

        for item in items:
            if item['type'] == 'group':
                gid = item['id']
                group = gtool.getGroupById(gid)
                if sum([group.has_role(r) for r in context.validRoles()]):
                    result.append(item)
        return result

AvailableGroupsVocabularyFactory = AvailableGroupsVocabulary()
