
from setuptools import setup, find_packages
from kspy.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='kspy',
    version=VERSION,
    description='Generates Kickstart files for automated vSphere builds',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Andy Clure',
    author_email='Andrew@asc-solutions.co.uk',
    url='https://github.com/andrewCluey/ksPy.git',
    license='GNU GPL3',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'kspy': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        kspy = kspy.main:main
    """,
)
