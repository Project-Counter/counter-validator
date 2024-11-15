from urllib.parse import parse_qs, urlparse

import pytest

from validations.fake_data import CounterAPIValidationFactory, ValidationFactory
from validations.models import Validation, ValidationCore


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
        assert parts_query["key"] == ["value"]
        assert parts_query["requestor_id"] == [params["requestor_id"]]
        assert parts_query["customer_id"] == [params["customer_id"]]
