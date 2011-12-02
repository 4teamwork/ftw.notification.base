from ftw.notification.base.interfaces import INotificationEvent
from zope.interface import implements


class NotificationEvent(object):
    """Event for journal entries"""
    implements(INotificationEvent)

    def __init__(self, obj, comment, action=None, actor=None, time=None):
        self.obj = obj
        self.action = action
        self.comment = comment
        self.actor = actor
        self.time = time
