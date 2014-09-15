from distutils.core import setup
import subprocess

git_version = 'UNKNOWN'
try:
    git_version = str(subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD'])).strip()
except subprocess.CalledProcessError,e:
    print "Got error when trying to read git version: %s" % e

setup(
    name='stresstester',
    version='0.2.1dev-%s' % git_version,
    author='Eero "rambo" af Heurlin',
    author_email='rambo@iki.fi',
    packages=['stresstester',],
    license='GNU LGPL',
    long_description=open('README.md').read(),
    description='Massively parallel stress-testing with Selenium',
    install_requires=open('requirements.txt').readlines(),
    url='https://github.com/rambo/stresser',
)

