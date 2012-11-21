from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.events.handlers import object_edited
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.schema.vocabulary import getVocabularyRegistry
import json
import re


def extract_email(value):
    if value:
        return value.split(',')
    return []


def validmails(recipients):
    valid = []
    expr = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=" +
                      r"?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?" +
                      r"\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$",
                      re.IGNORECASE)

    for mail in recipients:
        if expr.match(mail):
            valid.append(mail)
    return valid


class NotificationForm(BrowserView):
    """ Notification system
    """

    template = ViewPageTemplateFile('notification.pt')

    def __init__(self, context, request):
        super(NotificationForm, self).__init__(context, request)
        self.pre_select = []

    def __call__(self):
        if self.request.get('form.submitted', False):
            recipients = extract_email(self.request.get('users-to', ''))
            import ipdb; ipdb.set_trace()
            if len(recipients) == 0:
                IStatusMessage(self.request).addStatusMessage(
                    _(u'statusmessage_no_recipients',
                      default=u"You have to select at least one recipient"),
                    type='error')
                return self.template()

            if len(validmails(recipients)) != len(recipients):
                IStatusMessage(self.request).addStatusMessage(
                    _(u'statusmessage_invalid_mail',
                      default=u"You entered one or more invalid recipient(s)"),
                    type='error')
                return self.template()

            self.request.set('to_list', recipients)
            self.send_notification()

        return self.template()

    def json_source(self):
        """Returns the filtered result as json
        """
        mtool = getToolByName(self.context, 'portal_membership')
        vocabulary = getVocabularyRegistry().get(
            self.context,
            'ftw.notification.base.users')

        search_term = self.request.get('q', '')
        terms = vocabulary.search(search_term)
        result = []
        for term in terms:
            if term.type == 'group':
                name = term.title
                _id = 'group:%s' % term.token

            elif getattr(term, 'email', None):
                name = "%s &lt;%s&gt;" % (term.title, term.email)
                _id = term.email

            else:
                member = mtool.getMemberById(term.token)
                email = member.getProperty('email', '')
                name = "%s &lt;%s&gt;" % (term.title, email)
                _id = email

            result.append({'id': _id, 'name': name})
        return json.dumps(result)

    def json_source_by_group(self):
        """Returns members of a group as json
        """
        groupid = self.request.get('groupid', '')
        if not groupid:
            return json.dumps([])
        result = []
        gtool = getToolByName(self.context, 'portal_groups')
        group = gtool.getGroupById(groupid)

        for member in group.getGroupMembers():
            name = "%s &lt;%s&gt;" % (
                member.getProperty('fullname', member.getId()),
                member.getProperty('email', ''))
            result.append({'id': member.getId(),
                           'name': name})
        return json.dumps(result)

    def json_pre_select(self):
        vocabulary = getVocabularyRegistry().get(
            self.context,
            'ftw.notification.base.users')
        result = []
        for userid in self.pre_select:
            if userid in vocabulary.userids:
                mtool = getToolByName(self.context, 'portal_membership')
                member = mtool.getMemberById(userid)
                email = member.getProperty('email', '')
                title = member.getProperty('fullname', member.getId())
                name = "%s &lt;%s&gt;" % (title, email)
                _id = email

                result.append({'id': _id, 'name': name})
        return json.dumps(result)

    def send_notification(self):
        """Manual call the event"""

        # set sendNotification in REQUEST
        self.request.set('sendNotification', 1)
        object_edited(self.context, None)
