from unittest.mock import patch

import pytest
from django_celery_results.models import TaskResult

from validations.celery_queue import get_number_of_running_validations, get_validation_queue_length


class TestCeleryQueue:
    def test_get_validation_queue_length(self):
        with patch("validations.celery_queue.Redis") as redis_mock:
            redis_mock.return_value.llen.return_value = 0
            assert get_validation_queue_length() == 0
            redis_mock.return_value.llen.assert_called_with("validation")

            redis_mock.return_value.llen.return_value = 1
            assert get_validation_queue_length() == 1
            redis_mock.return_value.llen.assert_called_with("validation")

    @pytest.mark.django_db
    def test_get_number_of_running_validations(self):
        assert get_number_of_running_validations() == 0
        # create a task result with status "STARTED"
        TaskResult.objects.create(task_id="123", status="STARTED")
        assert get_number_of_running_validations() == 1
