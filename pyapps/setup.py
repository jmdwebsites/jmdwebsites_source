#from distutils.core import setup
from setuptools import setup, find_packages

setup(name='jmdwebsites',
      version='0.1.0',
      description='Click based command line application',
      author='jmdwebsites',
      author_email='jmdwebsites@gmail.com',
      install_requires=[
        'click', 'pytest'
        ],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      entry_points={
          'console_scripts': [
              'jmdwebsites = jmdwebsites.cli:main'
          ]
      },
      )

