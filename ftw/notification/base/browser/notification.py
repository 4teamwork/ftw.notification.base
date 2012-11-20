from Products.Five.browser import BrowserView
import json
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema.vocabulary import getVocabularyRegistry
from Products.CMFCore.utils import getToolByName


class NotificationView(BrowserView):
    """ Notification system
    """

    template = ViewPageTemplateFile('notification.pt')

    def __init__(self, context, request):
        super(NotificationView, self).__init__(context, request)

    def __call__(self):
        return self.template()

    def json_source(self):
        """Returns the filtered result as json
        """
        vocabulary = getVocabularyRegistry().get(
            self.context,
            'ftw.notification.base.users')

        search_term = self.request.get('q', '')
        terms = vocabulary.search(search_term)
        result = []
        for term in terms:
            result.append({'id': term.token, 'name': "%s &lt;%s&gt;" %
                (term.title, term.value)})
        return json.dumps(result)

    def json_source_by_group(self):
        """Returns members of a group as json
        """
        groupid = self.request.get('groupid', '')
        if not groupid:
            return []
        result = []
        gtool = getToolByName(self.context, 'portal_groups')
        group = gtool.getGroupById(groupid)
        for member in group.getGroupMembers():
            result.append({'id': member.getId(),
                           'name': member.getProperty('email')})
        return json.dumps(result)
