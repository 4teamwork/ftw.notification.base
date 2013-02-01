from Products.CMFCore.utils import getToolByName
from zope import schema, component
from zope.component.hooks import getSite
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
import AccessControl


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
