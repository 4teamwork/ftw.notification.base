from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.events.events import NotificationEvent
from ftw.notification.base.validators import AddressesValidator
from ftw.notification.base.validators import CcAddressesValidator
from plone.formwidget.autocomplete.widget import AutocompleteMultiFieldWidget
from plone.z3cform.layout import wrap_form
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
# from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.validator import WidgetValidatorDiscriminators
from zope import schema
from zope.component import provideAdapter
from zope.event import notify
from zope.interface import Interface


class INotifacationSchema(Interface):

    users = schema.List(
        title=_(u'label_users', default=u'Users'),
        description=_(u'help_users',
                      default=u'Select users to notificate.'),
        value_type=schema.Choice(
            vocabulary=u'ftw.notification.base.users'),
        required=False
        )

    cc_users = schema.List(
        title=_(u'label_cc_users', default=u'CC Users'),
        description=_(u'help_cc_users',
                      default=u'Select users to notificate per cc.'),
        value_type=schema.Choice(vocabulary=u'ftw.notification.base.users'),
        required=False
        )

    addresses = schema.List(
        title=_(u'label_addresses', default=u'E-Mail Addresses'),
        description=_(u'help_addresses',
                      default=u'Enter one e-mail address per line'),
        value_type=schema.TextLine(),
        required=False
        )

    cc_addresses = schema.List(
        title=_(u'label_cc_addresses', default=u'CC E-Mail Addresses'),
        description=_(u'help_cc_addresses',
                      default=u'Enter one e-mail address per line'),
        value_type=schema.TextLine(),
        required=False
        )

    comment = schema.Text(
    title=_(u'label_comment', default=u'Comment'),
    description=_(u'help_comment',
                  default=u'Enter a comment which will be contained '
                  'in the notification E-Mail'),
    required=True,
    )

WidgetValidatorDiscriminators(
    AddressesValidator, field=INotifacationSchema['addresses'])
WidgetValidatorDiscriminators(
    CcAddressesValidator, field=INotifacationSchema['cc_addresses'])

provideAdapter(AddressesValidator)


class NotificationForm(Form):
    label = _(u'label_notificte', default=u'Notificate')
    ignoreContext = True
    fields = Fields(INotifacationSchema)
    fields['users'].widgetFactory = AutocompleteMultiFieldWidget
    fields['cc_users'].widgetFactory = AutocompleteMultiFieldWidget
    fields['addresses'].widgetFactory = TextLinesFieldWidget
    fields['cc_addresses'].widgetFactory = TextLinesFieldWidget

    def updateWidgets(self):
        super(NotificationForm, self).updateWidgets()

        allowed_roles_to_view = []
        for role in self.context.rolesOfPermission('View'):
            if role.get('selected') == 'SELECTED':
                allowed_roles_to_view.append(role.get('name'))

        # XXX IMPLEMENTS HIDDEN MODE FOR LIST FIELDS
        # if 'Anonymous' not in allowed_roles_to_view:
        #     self.widgets['addresses'].mode = HIDDEN_MODE
        #     self.widgets['cc_addresses'].mode = HIDDEN_MODE

    @buttonAndHandler(_(u'button_send', default=u'Send'))
    def handle_send(self, action):
        data, errors = self.extractData()
        if len(errors) == 0:
            to_list = self.add_group_members(
                data.get('users', []))
            cc_list = self.add_group_members(
                data.get('cc_users', []))

            if data.get('addresses'):
                for address in data.get('addresses'):
                    to_list.append(address)

            if data.get('cc_addresses'):
                for address in data.get('cc_addresses'):
                    cc_list.append(address)

            self.request.set('to_list', to_list)
            self.request.set('cc_list', cc_list)

            comment = data.get('comment', u'')
            comment = safe_unicode(comment)
            notify(NotificationEvent(self.context, comment))

            # XXX TODO
            self.request.RESPONSE.redirect(
                '%s/view' % (self.context.absolute_url()))

    def add_group_members(self, userids):
        to_list = userids
        gtool = getToolByName(self.context, 'portal_groups')
        for id_ in userids:
            if id_.startswith('group:'):
                group = gtool.getGroupById(id_[6:])
                memberids = group.getAllGroupMemberIds()
                to_list += memberids
        return to_list

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(
            self.context.absolute_url())

NotificationFormView = wrap_form(NotificationForm)
