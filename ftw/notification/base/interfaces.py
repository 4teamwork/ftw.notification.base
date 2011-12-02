# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface, Attribute


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
