from setuptools import setup, find_packages

setup(name='pixutils',
      version='0.1.11',
      description='Pixalytics python utilities package',
      url='http://github.com/pixalytics-ltd/pixutils',
      author='Pixalytics Ltd',
      author_email='enquiries@pixalytics.com',
      license='MIT',
      packages=['pixutils', 'pixutils.gdl'],
      #packages=find_packages(),
      #namespace_packages=['pixutils'],
      install_requires=[
          'cdsapi',
      ],
      #     some scripts can be run directly from the command line.  These will be copied to the 'bin' directory in the
      #     target environment
      scripts=["pixutils/era_download.py"],
      zip_safe=False)
