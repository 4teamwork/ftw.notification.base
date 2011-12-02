import unittest

from zope.testing import doctest
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import ftw.notification.base


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(ftw.notification.base)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        doctest.DocTestSuite('ftw.notification.base'),

        ztc.ZopeDocFileSuite(
            'notification.txt',
            test_class=ptc.PloneTestCase,
            ),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
