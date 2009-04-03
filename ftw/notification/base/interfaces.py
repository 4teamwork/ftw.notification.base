from zope import schema
from zope.interface import Interface, Attribute

from ftw.notification.base import notification_base_factory as _


class INotificationEvent(Interface):
    """An event that can be fired to send notifications
    """

    action = Attribute("")
    comment = Attribute("")
    actor = Attribute("")
    time = Attribute("")


class INotifier(Interface):
    """Interface for 
    """

    def send_notification():
        """Method to add send a notification
        """
