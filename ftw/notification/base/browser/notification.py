from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.utils import NotificationUtils
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


def to_utf8(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return value


class NotificationForm(BrowserView):
    """ Notification system
    """

    template = ViewPageTemplateFile('notification.pt')

    def __init__(self, context, request):
        super(NotificationForm, self).__init__(context, request)
        self.pre_select = []
        self.vocabulary = None

    def __call__(self):
        self.vocabulary = getVocabularyRegistry().get(
            self.context,
            'ftw.notification.base.users')

        if self.request.get('form.submitted', False):
            recipients = extract_email(self.request.get('users-to', ''))
            cc = extract_email(self.request.get('users-cc', ''))
            if not self._validate(recipients, cc):
                return self.template()

            self.request.set('to_list', recipients)
            self.request.set('cc_list', cc)
            self.send_notification()

        return self.template()

    def _validate(self, recipients, cc):
        if len(recipients) == 0:
            IStatusMessage(self.request).addStatusMessage(
                _(u'statusmessage_no_recipients',
                  default=u"You have to select at least one recipient"),
                type='error')
            return False

        if len(validmails(recipients + cc)) != len(recipients + cc):
            IStatusMessage(self.request).addStatusMessage(
                _(u'statusmessage_invalid_mail',
                  default=u"You entered one or more invalid recipient(s)"),
                type='error')
            return False

        # XXX Add Server side check, if email addr is allowed

        return True

    def allow_email_not_in_vocab(self):
        utils = NotificationUtils(self.context)
        return utils.has_anonymous_role()

    def json_source(self):
        """Returns the filtered result as json
        """
        mtool = getToolByName(self.context, 'portal_membership')
        vocabulary = getVocabularyRegistry().get(
            self.context,
            'ftw.notification.base.users')

        search_term = self.request.get('q', '')
        # Decode to utf-8 because the plone.principal users vocab
        # needs a unicode to search

        terms = vocabulary.search(search_term.decode('utf-8'))
        result = []
        for term in terms:
            token = to_utf8(term.token)
            title = to_utf8(term.title)
            if term.type == 'group':
                name = title
                _id = 'group:%s' % token

            elif getattr(term, 'email', None):
                # term.email is utf8 encoded
                name = "%s [%s]" % (title, term.email)
                _id = term.email

            else:
                member = mtool.getMemberById(token)
                email = member.getProperty('email', '')
                name = "%s [%s]" % (title, email)
                _id = email

            result.append({'id': _id, 'text': name})

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
            name = "%s [%s]" % (
                member.getProperty('fullname', member.getId()),
                member.getProperty('email', ''))
            result.append({'id': member.getId(),
                           'text': name})
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
                name = "%s [%s]" % (title, email)
                _id = email

                result.append({'id': _id, 'text': name})
        return json.dumps(result)

    def send_notification(self):
        """Manual call the event"""

        # set sendNotification in REQUEST
        self.request.set('sendNotification', 1)
        object_edited(self.context, None)
