from setuptools import setup, find_packages

setup(name='pixutils',
      version='0.1.5',
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
      zip_safe=False)
