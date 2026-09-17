2.0.0
-----

* Upgraded Altcha widget to v3
* Upgraded Altcha challenges to v2
* Removed unused ALTCHA_SALT_PARAMS setting
* Added optional ALTCHA_AUTO setting to determine when client's browser should start solving the challenge. Defaults to 'onload'.
* Added required ALTCHA_HMAC_KEY_SECRET to settings. This should be a separate HMAC key that is used to speed up server-side solution validation.
* Changed the ALTCHA_MAX_NUMBER challenge difficulty setting to ALTCHA_COST, which defines exactly how many key derivations must be performed by the client.
* Added support for Python 3.14
* Added support for Django 6.0 and 6.1

1.0.0
-----

* Initial release
