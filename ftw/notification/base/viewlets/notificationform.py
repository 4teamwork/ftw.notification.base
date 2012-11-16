from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


class NotificationForm(common.ViewletBase):
    index = ViewPageTemplateFile('notificationform.pt')

    def available(self):
        """Checks if viewlet should be available or not """

        tools = queryMultiAdapter(
            (self.context, self.request),
            name="plone_tools")

        # pp = portal_properties
        pp = tools.properties()
        # notification properties
        np = getattr(pp, 'ftw.notification-properties', [])
        if not np:
            return False

        return self.context.portal_type in np.show_notification

    def render(self):
        """Renders viewlet only if it's available"""
        if self.available():
            return super(NotificationForm, self).render()
        else:
            return ""
