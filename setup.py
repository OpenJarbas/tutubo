from setuptools import setup
import os

PKG_NAME = 'tutubo'

def get_version():
    """ Find the version of this skill"""
    version_file = os.path.join(os.path.dirname(__file__), PKG_NAME, 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version


setup(
    name=PKG_NAME,
    version=get_version(),
    packages=[PKG_NAME],
    url='https://github.com/OpenJarbas/tutubo',
    license='Apache',
    author='jarbasAI',
    install_requires=["bs4", "requests", "pytube", "ytmusicapi"],
    author_email='jarbasai@mailfence.com',
    description='wrapper around pytube with some new functionality'
)
