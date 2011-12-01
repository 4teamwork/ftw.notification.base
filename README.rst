ftw.notification.base
=====================

This package provides a notification system for plone for sending
notifications when a content is changed.

Every edit-form is extended with a checkbox for sending a notification after
the modification on the content is done. When checked, the user will see a
form after submitting the changes, where he can select multiple persons to
be notified and add a comment.

This package does not contain the actual implementation of sending the
notification. It is designed so that the type of notification can be
replaced. Any type of notification can be implemented like this (e.g. email,
jabber, irc, physical letter).


Notification implementation packages
------------------------------------

- `ftw.notification.email`_: Sends the notification by email.


Usage
-----

- Add ``ftw.notification.base`` and your the implementation package to your
  buildout configuration:

::

    [instance]
    eggs +=
        ftw.notification.base
        ftw.notification.email

- Install the generic setup profiles of those packages.

- Edit any content: on the bottom of the form there is new checkbox "Send
  notification".


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.notification.base
- Issue tracker: https://github.com/4teamwork/ftw.notification.base/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.notification.base


Maintainer
==========

This package is produced and maintained by `4teamwork <http://www.4teamwork.ch/>`_ company.




.. _ftw.notification.email: https://github.com/4teamwork/ftw.notification.email
