from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NotificationForm(common.ViewletBase):
    index = ViewPageTemplateFile('notificationform.pt')