from urllib.parse import parse_qs, urlparse

import pytest

from validations.enums import SeverityLevel
from validations.fake_data import CounterAPIValidationFactory, ValidationFactory
from validations.models import Validation, ValidationCore, ValidationMessage


@pytest.mark.django_db
class TestValidation:
    def test_deleting_validation_preserves_core(self):
        validation = ValidationFactory()
        core = validation.core
        assert core is not None

        validation.delete()

        assert ValidationCore.objects.filter(pk=core.pk).exists()
        assert not Validation.objects.filter(pk=validation.pk).exists()

    def test_deleting_core_deletes_validation(self):
        validation = ValidationFactory()
        core = validation.core
        assert core is not None

        core.delete()

        assert not ValidationCore.objects.filter(pk=core.pk).exists()
        assert not Validation.objects.filter(pk=validation.pk).exists()

    def test_str(self):
        """
        Test that the __str__ method does not raise an exception
        """
        validation = ValidationFactory()
        str(validation)
        str(validation.core)


@pytest.mark.django_db
class TestCounterAPIValidation:
    @pytest.mark.parametrize(
        ["cop_version", "path_prefix"],
        [
            ("5.1", "/r51/reports"),
            ("5", "/reports"),
        ],
    )
    def test_get_url(self, cop_version, path_prefix):
        """
        Test that the get_url method returns the correct URL
        """
        report_code = "TR"
        params = {
            "url": "http://example.com",
            "cop_version": cop_version,
            "report_code": "TR",
            "begin_date": "2021-01-01",
            "end_date": "2021-12-31",
            "extra_attributes": {"key": "value"},
            "customer_id": "cid",
            "requestor_id": "rid",
            "api_key": "key",
        }

        validation = CounterAPIValidationFactory(
            credentials__requestor_id=params["requestor_id"],
            credentials__customer_id=params["customer_id"],
            credentials__api_key=params["api_key"],
            url=params["url"],
            requested_cop_version=params["cop_version"],
            core__api_endpoint="/reports/[id]",
            requested_report_code=params["report_code"],
            requested_begin_date=params["begin_date"],
            requested_end_date=params["end_date"],
            requested_extra_attributes=params["extra_attributes"],
        )
        request_url = validation.get_url()
        # split url
        parts = urlparse(request_url)
        assert parts.scheme == "http"
        assert parts.netloc == "example.com"
        assert parts.path == f"{path_prefix}/{report_code.lower()}"
        # check query params
        parts_query = parse_qs(parts.query)
        assert parts_query["begin_date"] == [params["begin_date"]]
        assert parts_query["end_date"] == [params["end_date"]]
        assert parts_query["key"] == ["value"], "Extra attributes should be included"
        assert parts_query["requestor_id"] == [params["requestor_id"]]
        assert parts_query["customer_id"] == [params["customer_id"]]
        assert parts_query["api_key"] == [params["api_key"]]

    @pytest.mark.parametrize("cop_version", ["5", "5.1"])
    def test_get_url_with_path(self, cop_version):
        """
        Test that the get_url method returns the correct URL with a path
        """
        validation = CounterAPIValidationFactory(
            url="http://example.com/path",
            requested_cop_version=cop_version,
        )
        assert validation.get_url().startswith("http://example.com/path")

    @pytest.mark.parametrize("endpoint", ["/members", "/status", "/reports"])
    def test_get_url_for_non_report_endpoints(self, endpoint):
        """
        Test that the get_url method returns the correct URL for non-report endpoints
        """
        validation = CounterAPIValidationFactory(
            core__api_endpoint=endpoint,
            url="http://example.com",
            requested_cop_version="5",
            requested_report_code="",
            requested_begin_date=None,
            requested_end_date=None,
            requested_extra_attributes={},
            credentials__requestor_id="rid",
            credentials__customer_id="cid",
            credentials__api_key="key",
        )
        request_url = validation.get_url()
        # split url
        parts = urlparse(request_url)
        assert parts.scheme == "http"
        assert parts.netloc == "example.com"
        assert parts.path == endpoint
        # check query params
        parts_query = parse_qs(parts.query)
        assert parts_query["requestor_id"] == ["rid"]
        assert parts_query["customer_id"] == ["cid"]
        assert "begin_date" not in parts_query
        assert "end_date" not in parts_query


@pytest.mark.django_db
class TestValidationMessage:
    @pytest.mark.parametrize("null_key", ["d", "h", "p", "m", "s"])
    def test_from_dict(self, null_key):
        """
        Test that the from_dict method creates a ValidationMessage instance.
        We make sure that "null" values are handled correctly and converted to empty strings.
        """
        data = {
            "d": ":)",
            "l": "Warning",
            "h": "You should do something about it",
            "p": "element.Report_Header",
            "m": "Report header is messed up :)",
            "s": "Report header is messed up",
            null_key: None,
        }
        validation = ValidationFactory()
        message = ValidationMessage.from_dict(validation, 1, data)
        assert message.severity == SeverityLevel.WARNING
        assert message.hint == (data["h"] or "")
        assert message.location == (data["p"] or "")
        assert message.message == (data["m"] or "")
        assert message.summary == (data["s"] or "")
        assert message.data == (data["d"] or "")
        assert not ValidationMessage.objects.filter(pk=message.pk).exists(), (
            "The message should not be saved to the database"
        )
        # test saving
        message.save()
