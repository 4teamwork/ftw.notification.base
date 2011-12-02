from zope.interface import implements
from ftw.notification.base.interfaces import INotifier


class BaseNotifier(object):
    implements(INotifier)
