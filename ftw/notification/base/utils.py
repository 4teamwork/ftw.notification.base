from Products.CMFPlone.utils import getFSVersionTuple

IS_PLONE_4 = (4,) <= getFSVersionTuple() < (5,)
