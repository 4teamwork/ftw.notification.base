from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from ftw.notification.base.events.events import NotificationEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile



class NotificationForm(BrowserView):

    template = ViewPageTemplateFile('notification_form.pt')

    def __call__(self):
        if self.request.get('submit'):
            comment = self.request.get('comment', '')
            notify(NotificationEvent(self.context, comment))
            self.request.RESPONSE.redirect(self.context.absolute_url())
        if self.request.get('cancel'):
            self.request.RESPONSE.redirect(self.context.absolute_url())
        return self.template()

    def getAssignableUsers(self):
        """Collect users with a given role and return them in a list.
        """
        context = self.context.aq_inner
        role = 'Reader'
        results = []
        pas_tool = getToolByName(context, 'acl_users')
        utils_tool = getToolByName(context, 'plone_utils')

        inherited_and_local_roles = utils_tool.getInheritedLocalRoles(context) + pas_tool.getLocalRolesForDisplay(context)

        for user_id_and_roles in inherited_and_local_roles:
            if user_id_and_roles[2] == 'user':
                if role in user_id_and_roles[1]:
                    user = pas_tool.getUserById(user_id_and_roles[0])
                    if user:
                        results.append((user.getId(), '%s (%s)' % (user.getProperty('fullname', ''), user.getId())))
            if user_id_and_roles[2] == 'group':
                if role in user_id_and_roles[1]:
                    for user in pas_tool.getGroupById(user_id_and_roles[0]).getGroupMembers():
                        results.append((user.getId(), '%s (%s)' % (user.getProperty('fullname', ''), user.getId())))

        return results