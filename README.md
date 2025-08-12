# Django Altcha Middleware

## About
Django-altcha-middleware (dam) is meant to be a proof-of-work deterrent for bots.
This Django app uses Altcha to create a challenge for protected pages that is solved
by using cryptographic functions to find a hidden number. Once a user successfully
solves a challenge (done automatically by the browser, no user input required), they
will not be challenged again for a period defined by ALTCHA_AUTH_EXPIRE_MINUTES. This app
may be used to protect an entire site by using the provided middleware, or only certain
views by using the provided decorator.

## Requirements

* Python 3.9-3.12
* Django 4.2-5.2

## Installation

To install this app into your existing Django project:
1. Install the django-altcha-middleware package into your Python installation
   (if using a virtual environment, for instance, activate it first):
    ```sh
    $ pip install git+https://github.com/unt-libraries/django-altcha-middleware
    ```
2. Within your project's settings file, add `dam` to your Django project's INSTALLED_APPS list and
   define `ALTCHA_HMAC_KEY` and `ALTCHA_MAX_NUMBER`, as well as the other settings if you'd like to
   override their default values (shown below):
    ```python
    INSTALLED_APPS = [
        ...,
        'dam',
    ]
    ALTCHA_HMAC_KEY = 'something'                   # REQUIRED: Secret string used for challenges.
    ALTCHA_MAX_NUMBER = 50000                       # REQUIRED: Altcha challenge difficulty.
    ALTCHA_AUTH_EXPIRE_MINUTES = 480                # Minutes the user is authorized for after solving a challenge.
    ALTCHA_CHALLENGE_EXPIRE_MINUTES = 2             # Minutes before a given challenge expires.
    ALTCHA_SALT_PARAMS = {}                         # Additional query parameters to append to the challenge salt.
    ALTCHA_SESSION_KEY = 'altcha_verified'          # Session key name that tracks successful challenges.
    ALTCHA_JS_URL = '/static/altcha/altcha.min.js'	# Where to find the altcha widget JS.
    ALTCHA_EXCLUDE_PATHS = set()                    # Set of paths to exclude from challenges.
    ALTCHA_EXCLUDE_IPS = []                         # List of strings representing CIDRs or IPs to never challenge.
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
    $ pip install -rrequirements.txt -rrequirements-test.txt
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

* To run the unit tests against all available versions of Python from 3.9 - 3.12, as well as the
   flake8 lint checks and coverage report:
    ```sh
    $ tox
    ```

## License

See LICENSE.txt

## Contributors

* [Lauren Ko](https://github.com/ldko)
* [Gio Gottardi](https://github.com/somexpert)
