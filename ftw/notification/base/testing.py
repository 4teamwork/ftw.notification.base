from ftw.builder.testing import BUILDER_LAYER
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class FtwNotificationBaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.notification.base
        import ftw.table

        xmlconfig.file('configure.zcml', ftw.notification.base,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', ftw.table,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.notification.base:default')


FTW_NOTIFICATION_BASE_FIXTURE = FtwNotificationBaseLayer()
FTW_N_BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_NOTIFICATION_BASE_FIXTURE, ),
    name="FtwNofificationBase:Integration")

FTW_N_BASE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_NOTIFICATION_BASE_FIXTURE, ),
    name="FtwNofificationBase:Functional")
