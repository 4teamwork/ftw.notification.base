from setuptools import setup, find_packages
import os

version = '1.2'
maintainer = 'Jonas Baumann'

setup(name='ftw.notification.base',
      version=version,
      description='Send notifications when editing a plone content.',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw notification base plone',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.notification.base',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.notification'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'ftw.table',
        ],

      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
