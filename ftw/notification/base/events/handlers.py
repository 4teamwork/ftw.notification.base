from zope.component import getMultiAdapter

from DateTime import DateTime

from ftw.notification.base.interfaces import INotifier
from ftw.notification.base import notification_base_factory as _


def NotificationHandler(event):
    """
    """
    obj = event.obj
    comment = event.comment
    try:
        notifier = INotifier(obj)
    except:
        return
    
    if event.action is None:
        action = _(u"label_send_notification", default=u"Send Notification")
    else:
        action = event.action

    if event.actor is None:
        portal_state = getMultiAdapter((obj, obj.REQUEST), name=u'plone_portal_state')
        actor = portal_state.member().getId()
    else:
        actor = event.actor
 
    if event.time is None:
        time = DateTime()
    else:
        time = event.time
    
    notifier(kwargs=dict(action=action, comment=comment, actor=actor, time=time))
