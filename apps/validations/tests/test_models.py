import pytest

from validations.fake_data import ValidationFactory
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
