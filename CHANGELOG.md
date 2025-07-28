# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.1] - 2025-07-28

- fix: fix error when clearing text filter in validation core table

## [0.12.0] - 2025-07-25

- feat: add date filter to validation and validation core tables
- feat: add tooltip with user email to user name in validation core table
- chore: update backend and frontend dependencies

## [0.11.0] - 2025-07-11

- feat: use the original filename as basis for the exported validation report

## [0.10.0] - 2025-07-03

- fix: use data from `reportinfo` attribute to display extracted information both in UI and in exports
- feat: make it possible to send operator emails to validator admins via new `receive_operator_emails` user field
- feat: enhance daily validation report to include validation results breakdown with severity levels
- feat: add email notifications to admins for validation failures

## [0.9.0] - 2025-06-27

- feat: rename project from "COUNTER Validation Tool" to "COUNTER Validator"
- update the code to use the new validation module interface with `reportinfo` attribute
- feat: add daily validation report functionality with email notifications to operators (see `OPERATORS` in settings)

## [0.8.1] - 2025-06-05

- fix: hide sensitive information in public validation views
- fix: update CoP5 documentation link to countermetrics.org
- feat: add API usage to features list on homepage

## [0.8.0] - 2025-06-05

- fix: limit pagination to maximum 100 items per page - both frontend and backend
- fix: update the upstream domain from bigdigdata.com to countermetrics.org
- feat: improve login page with redirect to validations for logged-in users
- feat: add GitHub issues link to about page
- fix: fix validation messages not being shown to admins

## [0.7.1] - 2025-05-27

- fix: fix export of COUNTER API validations without credentials (`/status/` in CoP 5.1)

## [0.7.0] - 2025-05-19

- fix: ensure all attributes to show are selected by default when CoP version and credentials are changed
- add granularity selection to the validation wizard
- change header label from "Switches" to "Report attributes" in NewCounterAPIValidation component

## [0.6.5] - 2025-05-15

- add Apache License Version 2.0 to the project
- update documentation with licensing information and copyright details
- standardize "COUNTER" capitalization in user-facing content
- add legacy browser support with @vitejs/plugin-legacy
- remove Data_Type from attributes to show for C5.1 reports
- improve validation table display with conditional tooltips and fallback severity level chips

## [0.6.4] - 2025-05-14

- fix platform attribute not being copied when repeating a validation
- fix end date being the first day of the month instead of the last day
- fix autofocus on the signup page

## [0.6.3] - 2025-05-09

- fix error causing COUNTER API paths being stripped of path before being used for validation

## [0.6.2] - 2025-05-07

- make the messages API endpoint available using API-Key
- add rudimentary documentation of the public API

## [0.6.1] - 2025-04-26

- make sure user email is not used for filtering of own validations for admins
- make it possible for the validation module to return data with empty `report_id`

## [0.6.0] - 2025-03-27

- use COUNTER Registry information to highlight required fields when entering credentials
- add back button to validation detail page
- force page reload when a chunk cannot be loaded (should prevent freezes in production when new
  version is published)

## [0.5.0] - 2025-03-25

- make it possible to validate CoP 5.1 /status without credentials
- do not show extracted info for API endpoints which do contain any such data
- implement a simple DRF serializer based validation of data returned by the
  validation module and use it to parse and validate incoming data
- automatically reload running validations in the detail view
- only show the export button and validation statistics when validation has successfully finished
- add platform name abbreviations to the list of platforms when starting API validation
- select Include_Parent_Details for IR reports by default
- add forgotten Data_Type filter to C5.1 reports
- reset page in validation table when an action (filter, deleting of items) would lead
  to a non-existant page
- show the complete validated URL to the user and let her try it in the browser
- allow validator admins access to the validation queue API
- fix Django admin for users not to expect `username`
- add link to the GitHub repository and upstream server to the About page
- add info about the open source license and GitHub repo to the main page
- automatically reload frontend when version difference between backend and frontend is detected
- update README.md with project overview, technologies used, and development setup instructions
- remove test COUNTER API server URL as default value from the validation wizard
- add dates to the changelog
- add link to the changelog to the About page and to the footer

## [0.4.0] - 2025-03-18

- add changelog + related backend and frontend functions
