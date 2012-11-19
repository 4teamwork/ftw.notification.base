from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.events.handlers import object_edited
from ftw.table.interfaces import ITableGenerator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.i18n import translate


def name_helper(item, value):
    title = safe_unicode(item['title'], 'utf-8')
    email = safe_unicode(item['email'], 'utf-8')
    val = u'%s (%s)' % (title, email)
    return val


def groupname_helper(item, value):
    title = safe_unicode(item['title'], 'utf-8')
    val = u'%s' % title
#   bei klick alle user anzeigen? js
#    val = u'<a href="#" class="showUsers" title="groupid">%s</a>' % title
    return val


def checkbox_to_selected_helper(item, value):
    if item['selected'] == True:
        return u"""<input type="checkbox"
                          name="to_list:list"
                          checked="checked"
                          value="%s"/>""" % item['value']

    return u"""<input type="checkbox"
                      name="to_list:list"
                      value="%s"/>""" % item['value']


def checkbox_cc_helper(item, value):
    return u"""<input type="checkbox"
                    name="cc_list:list"
                    value="%s"/>""" % item['value']


def checkbox_to_group_helper(item, value):
    return u"""<input type="checkbox"
                      name="to_list_group:list"
                      value="%s"/>""" % item['value']


def checkbox_cc_group_helper(item, value):
    return u"""<input type="checkbox"
                    name="cc_list_group:list"
                    value="%s"/>""" % item['value']


class NotificationForm(BrowserView):

    template = ViewPageTemplateFile('notification_form.pt')

    pre_select = None

    def __init__(self, context, request):
        super(NotificationForm, self).__init__(context, request)
        # TODO: pre_select should be filled by an adapter call
        self.pre_select = []

    def __call__(self):
        return self.template()

    @property
    def columns(self):
        return (
            {'column': 'to',
             'column_title': '<input type="checkbox" id="all-to"/>'
                             '<label for="all-to"> %s</label>' % (
                                 translate(u'label_to',
                                           default='TO',
                                           domain="ftw.notification.base",
                                           context=self.request)),
             'transform': checkbox_to_selected_helper},
            {'column': 'cc',
             'column_title': '<input type="checkbox" id="all-cc"/>'
             '<label for="all-cc"> %s</label>' % (
                 translate(u'label_cc',
                             default='CC',
                             domain="ftw.notification.base",
                             context=self.request)),
             'transform': checkbox_cc_helper},
            {'column': 'name',
             'column_title': _(u'label_name', default='Name'),
             'transform': name_helper})

    @property
    def columns_group(self):
        return (
            {'column': 'to',
             'column_title': '<input type="checkbox" id="all-group-to"/>'
                             '<label for="all-group-to"> %s</label>' % (
                                 translate(u'label_to',
                                           default='TO',
                           domain="ftw.notification.base",
                           context=self.request)),
             'transform': checkbox_to_group_helper},
            {'column': 'cc',
             'column_title': '<input type="checkbox" id="all-group-cc"/>'
                              '<label for="all-group-cc"> %s</label>' % (
                 translate(u'label_cc',
                           default='CC',
                           domain="ftw.notification.base",
                           context=self.request)),
             'transform': checkbox_cc_group_helper},
            {'column': 'name',
             'column_title': _(u'label_name', default='Name'),
             'transform': groupname_helper})

    @property
    def users(self):
        context = self.context
        memtool = getToolByName(context, 'portal_membership')
        vocabulary = queryUtility(schema.interfaces.IVocabularyFactory,
                                  name='ftw.notification.base.users',
                                  context=context)
        if vocabulary:
            users = vocabulary(context)

            finalized = []
            for t in users:
                userid = t.value
                member = memtool.getMemberById(userid)
                if member is None:
                    continue

                user = dict(title=t.title,
                            value=t.value,
                            email=member.getProperty("email", ""), 
                            selected=t.value in self.pre_select)
                finalized.append(user)

            finalized.sort(key=lambda user: user['title'].lower())
        return finalized

    def groups(self):
        context = self.context
        groups = []
        vocabulary = queryUtility(schema.interfaces.IVocabularyFactory,
                                  name='ftw.notification.base.groups',
                                  context=context)
        if vocabulary:
            groups = vocabulary(context)
            groups = [dict(title=g['title'], value=g['id']) for g in groups]
            groups.sort(key=lambda user: user['title'].lower())
        return groups

    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.users, self.columns, sortable=('name'))

    def render_listing_group(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.groups(), self.columns_group,
                                  sortable=('name'))

    def send_notification(self):
        """Manual call the event"""

        # set sendNotification in REQUEST
        self.request.set('sendNotification', 1)
        object_edited(self.context, None)
