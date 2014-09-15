from distutils.core import setup
import subprocess

git_version = str(subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD'])).strip()

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

