from setuptools import setup, find_packages


setup(
    name='crawler_timberland',
    version='0.0.1',
    description='Timberland product crawler',
    author='Lu Yi',
    author_email='leo0650@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'dotenv',
        'pyquery',
        'pymongo',
    ],
)
