from setuptools import setup

setup(
    name='tutubo',
    version='0.0.1a1',
    packages=['tutubo'],
    url='https://github.com/OpenJarbas/tutubo',
    license='Apache',
    author='jarbasAI',
    install_requires=["bs4", "requests", "pytube"],
    author_email='jarbasai@mailfence.com',
    description='wrapper around pytube with some new functionality'
)
