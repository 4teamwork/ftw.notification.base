from Products.Five.browser import BrowserView
import json
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema.vocabulary import getVocabularyRegistry
from Products.CMFCore.utils import getToolByName
from ftw.notification.base.events.handlers import object_edited


class NotificationForm(BrowserView):
    """ Notification system
    """

    template = ViewPageTemplateFile('notification.pt')

    def __init__(self, context, request):
        super(NotificationForm, self).__init__(context, request)
        self.pre_select = []

    def __call__(self):
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
        self.request.set('to_list', self.request.get('users-to'))
        object_edited(self.context, None)
