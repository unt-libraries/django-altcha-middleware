# Django Altcha Middleware

[![Build Status](https://github.com/unt-libraries/django-altcha-middleware/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/unt-libraries/django-altcha-middleware/actions)


## About
Django-altcha-middleware (dam) is meant to be a proof-of-work deterrent for bots.
This Django app uses Altcha to create a challenge for protected pages that is solved
by using cryptographic functions to find a hidden number. Once a user successfully
solves a challenge (done automatically by the browser, no user input required), they
will not be challenged again for a period defined by ALTCHA_AUTH_EXPIRE_MINUTES. This app
may be used to protect an entire site by using the provided middleware, or only certain
views by using the provided decorator.

![django-altcha-middleware challenge view screenshot](https://github.com/user-attachments/assets/341c9941-87c6-46ae-aea6-89a4426b5a71)

## Requirements

* Python 3.9-3.14
* Django 4.2-6.1

## Installation

To install this app into your existing Django project:
1. Install the django-altcha-middleware package into your Python installation
   (if using a virtual environment, for instance, activate it first):
    ```sh
    $ pip install git+https://github.com/unt-libraries/django-altcha-middleware
    ```
2. Within your project's settings file, add `dam` to your Django project's INSTALLED_APPS list and
   define `ALTCHA_HMAC_KEY`, `ALTCHA_HMAC_KEY_SECRET`, and `ALTCHA_COST`, as well as the other settings
   if you'd like to override their default values (shown below):
    ```python
    INSTALLED_APPS = [
        ...,
        'dam',
    ]
    ALTCHA_HMAC_KEY = 'something'                   # REQUIRED: Secret string used for challenges.
	ALTCHA_HMAC_KEY_SECRET = 'something-else'       # REQUIRED: Enables fast server-side verification without re-deriving the key.
    ALTCHA_COST = 2_500                             # REQUIRED: The exact amount of key derivations required by the client. Determines how much time/effort is required.
    ALTCHA_AUTO = 'onload'                          # Determines when the client's browser starts solving the challenge. Value should be one of the following strings: 'off', 'onfocus', 'onload', or 'onsubmit'.
    ALTCHA_AUTH_EXPIRE_MINUTES = 480                # Minutes the user is authorized for after solving a challenge.
    ALTCHA_CHALLENGE_EXPIRE_MINUTES = 2             # Minutes before a given challenge expires.
    ALTCHA_SESSION_KEY = 'altcha_verified'          # Session key name that tracks successful challenges.
    ALTCHA_SITE_ICON_URL = ''                       # Where to find the site icon for use on the challenge page.
    ALTCHA_JS_URL = (f'{STATIC_URL}altcha/'         # Where to find the altcha widget JS.
                     'altcha.min.js')
    ALTCHA_CSS_URL = f'{STATIC_URL}dam/dam.css'     # Where to find the altcha widget CSS.
    ALTCHA_MESSAGE = ('Gauging your humanity...'    # Message to present to users on the challenge page.
                      'This may take some seconds.')
    ALTCHA_HELP_MESSAGE = ''                        # Message shown on challenge page and in errors indicating how to seek help on challenge failure/error.
    ALTCHA_FAIL_MESSAGE = ('Challenge failed or no' # Message to show users when their challenge response is unsuccessful.
                           ' longer valid.')
    ALTCHA_EXCLUDE_PATHS = []                       # List of regular expressions (as raw strings) used to exempt URL paths from challenge.
                                                    # Example: [r'^/api/.*', r'secret', r'\.json$']
                                                    # Above would exempt paths starting with '/api/', any with 'secret' in the path, and any ending in '.json'
    ALTCHA_EXCLUDE_IPS = []                         # List of strings representing CIDRs or IPs to never challenge.
    ALTCHA_EXCLUDE_HEADERS = {}                     # Dict of HTTP header keys (case insensitive) with values to exempt from challenge.
                                                    # Values should be given as raw strings as the middleware converts them to case-insensitive regex patterns.
                                                    # Example: {'User-Agent': r'Googlebot|Siteimprove\.com'}
    ```
3. Add the challenge URL to your project's urls.py module:
    ```python
    urlpatterns = [
        ...,
        path('', include('dam.urls')),
    ]
    ```
4. Decide whether you'd like to protect individual views or your whole site.
    - If you'd like to protect your whole site with `dam`, then add it to your MIDDLEWARE list in
      your settings file:
        ```python
        MIDDLEWARE = [
            ...,
            'dam.middleware.AltchaMiddleware',
        ]
        ```
    - Or, if you'd like to only protect certain views, then use the `@dam` decorator on them:
        ```python
        from dam.decorators import dam
        ...
        @dam
        def my_precious_view(request):
            """I don't want bots crawling this page."""
            ...
            return HttpResponse("Can't touch this!")
        ```

## Development

### Setup

Follow the steps below to set up a development environment for if you'd like to be able to test out
the project without setting up your own Django project, run the unit tests, or make changes.
1. Clone this repo and then navigate inside of it:
    ```sh
    $ git clone git@github.com:unt-libraries/django-altcha-middleware.git && cd django-altcha-middleware
    ```
2. Set up a Python virtual environment and then activate it:
    ```sh
    $ python3 -m venv env && source env/bin/activate
    ```
3. Install the main and test requirements:
    ```sh
    $ pip install -e .
    $ pip install -e .[test]
    ```

### Running the test project

1. Start the Django test server:
    ```sh
    $ python3 manage.py runserver
    ```
2. While that is running, open your browser and you can experience the challenge page by visiting
http://localhost:8000/protected. The test project is set up to protect the `/protected` page
(redirecting to the `/` challenge page until the challenge is solved, then redirecting again to
`/protected` after completing the challenge) while leaving the `/open` page available with no
challenge.
3. When you are done viewing the pages, you can stop the test server with CTRL-C.

### Running the tests

* Install tox and run the unit tests against all available versions of Python from 3.9 - 3.14, as well as the
   Ruff lint/style checks and coverage report:
    ```sh
	$ pip install tox
    $ tox
    ```
* Or, to just run the tests against your current versions of Python and Django, along with viewing the coverage report:
    ```sh
	$ coverage run -m pytest
    $ coverage report -m
    ```

## License

See LICENSE.txt

## Contributors

* [Lauren Ko](https://github.com/ldko)
* [Gio Gottardi](https://github.com/somexpert)
