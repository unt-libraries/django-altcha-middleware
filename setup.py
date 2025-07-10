from setuptools import setup, find_packages

setup(
    name='dam',
    version='1.0.0',
    packages=find_packages(exclude=['tests*']),
    description='Django app for adding altcha proof-of-work challenges to views.',
    long_description='See the home page for more information.',
    include_package_data=True,
    install_requires=[
        'django >=4.2, <=5.2',
        'altcha ~= 0.2.0',
    ],
    url='https://github.com/unt-libraries/django-altcha-middleware',
    author='University of North Texas Libraries',
    author_email='mark.phillips@unt.edu',
    license='BSD',
    keywords=['django', 'altcha', 'bots', 'proof-of-work', 'middleware', 'decorator'],
    classifiers=[
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ]
)
