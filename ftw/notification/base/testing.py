from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwNotificationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.notification.base

        xmlconfig.file('configure.zcml', ftw.notification.base,
                       context=configurationContext)

        # installProduct() is *only* necessary for packages outside
        # the Products.* namespace which are also declared as Zope 2
        # products, using <five:registerPackage /> in ZCML.
        z2.installProduct(app, 'ftw.notification.base')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.notification.base:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


FTW_NOTIFICATION_FIXTURE = FtwNotificationLayer()
FTW_NOTIFICATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_NOTIFICATION_FIXTURE, ), name="FtwNotification:Integration")
FTW_NOTIFICATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_NOTIFICATION_FIXTURE, ), name="FtwNotification:Functional")
