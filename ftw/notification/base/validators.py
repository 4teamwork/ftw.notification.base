from ftw.notification.base import notification_base_factory as _
from z3c.form.validator import SimpleFieldValidator
from zope.interface import Invalid
import re


class AddressesValidator(SimpleFieldValidator):
    """Validator for validating the e-mail addresses field
    """

    MAIL_EXPRESSION = r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=" +\
        "?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?" +\
        "\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$"

    def __init__(self, *args, **kwargs):
        super(AddressesValidator, self).__init__(*args, **kwargs)
        self.email_expression = re.compile(AddressesValidator.MAIL_EXPRESSION,
                                           re.IGNORECASE)

    def validate(self, value):
        """Validates the `value`, expects a list of carriage-return-separated
        email addresses. """
        super(AddressesValidator, self).validate(value)
        if value:
            self._validate_addresses(value)

    def _validate_addresses(self, addresses):
        """E-Mail address validation
        """

        for addr in addresses:
            addr = addr.strip()
            if not self.email_expression.match(addr):
                msg = _(u'error_invalid_addresses',
                        default=u'At least one of the defined addresses '
                        'are not valid.')
                raise Invalid(msg)


class CcAddressesValidator(AddressesValidator):
    """subclass for the cc_addreses field
    """
