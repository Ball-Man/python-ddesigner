from setuptools import setup

# README = open('README.md').read()
REQUIREMENTS = open('requirements.txt').read().splitlines()

setup(name='python-ddesigner',
      classifiers=['Programming Language :: Python :: 3 :: Only',
                   'License :: OSI Approved :: MIT License'],
      version='1.0',
      description='An importer library for Dialogue Designer.',
      long_description='An importer library for Dialogue Designer from radmatt.',
      url='https://github.com/Ball-Man/python-ddesigner',
      author='Francesco Mistri',
      author_email='franc.mistri@gmail.com',
      license='MIT',
      packages=['ddesigner'],
      install_requires=REQUIREMENTS
      )
