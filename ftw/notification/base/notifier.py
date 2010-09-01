from zope.interface import implements
from interfaces import INotifier


class BaseNotifier(object):
    implements(INotifier)
