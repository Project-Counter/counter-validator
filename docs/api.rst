===========================
COUNTER Validation Tool API
===========================

API access
==========

To access the API, you need to have a valid API key. Each user can create API keys in their user profile
under ``Settings`` -> ``API keys``. The number of API keys is unlimited.

The API key needs to be provided in the HTTP Authorization header of every request in the following format:

.. code-block::

   Authorization: Api-Key <api-key>


API endpoints
=============


Create a new file validation
----------------------------

Endpoint: ``/api/v1/validations/validation/file/``

Method: ``POST``

Attributes:

- ``file``: File to validate
- ``user_note``: Optional note for the validation

Example:

.. code-block::

   curl \
   -X POST \
   -H "Authorization: Api-Key <api-key>" \
   -F "file=TR.csv" \
   -F "user_note=This is a test validation" \
   "https://validator.bigdigdata.com/api/v1/validations/validation/file/"

Sample response:

.. code-block::

    {
        "api_endpoint" : "",
        "api_key_prefix" : "xxxxxxx",
        "cop_version" : "",
        "created" : "2025-04-22T18:10:44.048197Z",
        "credentials" : null,
        "data_source" : "file",
        "error_message" : "",
        "expiration_date" : "2025-04-29T18:10:44.047820Z",
        "file_size" : 3674,
        "file_url" : "/media/file_validations/xxxxxxx.csv",
        "filename" : "TR.csv",
        "id" : "01965eb1-f8d1-779d-8034-85925df22b80",
        "public_id" : null,
        "report_code" : "",
        "requested_begin_date" : null,
        "requested_cop_version" : null,
        "requested_end_date" : null,
        "requested_extra_attributes" : null,
        "requested_report_code" : null,
        "stats" : {},
        "status" : 0,
        "url" : null,
        "use_short_dates" : null,
        "user_note" : "Test validation",
        "validation_result" : "Unknown"
    }

The most important fields are:

- ``id``: The ID of the validation - this can be used to retrieve the validation results later
- ``status``: The status of the validation:
  - ``0``: Waiting
  - ``1``: Running
  - ``2``: Success
  - ``3``: Failure
- ``validation_result``: The result of the validation

Immediately after the validation is created, the status is ``0`` (Waiting). It is then picked
up by a worker and the status is updated to ``1`` (Running). When the validation is finished,
the status is updated to ``2`` (Success) or ``3`` (Failure).

The status of the validation can be checked at any time using the
``/api/v1/validations/validation/<id>/`` endpoint described below.


Retrieve details of a validation
--------------------------------

Endpoint: ``/api/v1/validations/validation/<id>/``

Method: ``GET``


Example:

.. code-block::

   curl \
   -X GET \
   -H "Authorization: Api-Key <api-key>" \
   "https://validator.bigdigdata.com/api/v1/validations/validation/<id>/"

Sample response (using the ``id`` from the previous example):

.. code-block::

    {
        "api_endpoint" : "",
        "api_key_prefix" : "xxxxxxx",
        "cop_version" : "",
        "created" : "2025-04-22T18:10:44.048197Z",
        "credentials" : null,
        "data_source" : "file",
        "error_message" : "",
        "expiration_date" : "2025-04-29T18:10:44.047820Z",
        "file_size" : 3674,
        "file_url" : "/media/file_validations/xxxxxxx.csv",
        "filename" : "TR.csv",
        "full_url" : "",
        "id" : "01965eb1-f8d1-779d-8034-85925df22b80",
        "public_id" : null,
        "report_code" : "TR",
        "requested_begin_date" : null,
        "requested_cop_version" : null,
        "requested_end_date" : null,
        "requested_extra_attributes" : null,
        "requested_report_code" : null,
        "result_data" : {
            "datetime" : "2025-04-22 18:10:44",
            "header" : {
                "begin_date" : "2016-01-01",
                "cop_version" : "5",
                "created" : "2019-04-25T11:39:56Z",
                "created_by" : "Publisher Platform Delta",
                "end_date" : "2016-03-31",
                "format" : "tabular",
                "institution_name" : "Client Demo Site",
                "report" : {
                    "A1" : "Report_Name",
                    "A10" : "Reporting_Period",
                    "A11" : "Created",
                    "A12" : "Created_By",
                    "A2" : "Report_ID",
                    "A3" : "Release",
                    "A4" : "Institution_Name",
                    "A5" : "Institution_ID",
                    "A6" : "Metric_Types",
                    "A7" : "Report_Filters",
                    "A8" : "Report_Attributes",
                    "A9" : "Exceptions",
                    "B1" : "Title Master Report",
                    "B10" : "Begin_Date=2016-01-01; End_Date=2016-03-31",
                    "B11" : "2019-04-25T11:39:56Z",
                    "B12" : "Publisher Platform Delta",
                    "B2" : "TR",
                    "B3" : "5",
                    "B4" : "Client Demo Site",
                    "B5" : "ISNI:1234123412341234",
                    "B8" : "Attributes_To_Show=Data_Type|Section_Type|YOP|Access_Type|Access_Method"
                },
                "report_id" : "TR",
                "result" : [
                    "Validation Result for COUNTER Release 5 Report",
                    "",
                    "Title Master Report (TR)",
                    "for Client Demo Site",
                    "created 2019-04-25T11:39:56Z by Publisher Platform Delta",
                    "covering 2016-01-01 to 2016-03-31",
                    "(please see the Report Header sheet for details)"
                ]
            },
            "result" : "Passed"
        },
        "stats" : {},
        "status" : 2,
        "url" : null,
        "use_short_dates" : null,
        "user" : {
            "email" : "foo@bar.baz",
            "first_name" : "Foo",
            "has_admin_role" : false,
            "id" : 7,
            "is_active" : true,
            "is_superuser" : false,
            "is_validator_admin" : false,
            "last_name" : "Bar"
        },
        "user_note" : "Test validation",
        "validation_result" : "Passed"
    }

As you can see, the status is ``2`` (``Success``) and there is some extra information in the response.
In this case the validation was successful and the result is ``Passed``. In case of some errors,
the ``stats`` field will contain a histogram of the errors.
