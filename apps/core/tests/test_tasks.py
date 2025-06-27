from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils.timezone import now
from freezegun import freeze_time
from validations.fake_data import ValidationCoreFactory

from core.fake_data import UserFactory
from core.tasks import daily_validation_report


@pytest.mark.django_db
class TestDailyValidationReport:
    def test_daily_validation_report_no_validations(self):
        """Test daily validation report when no validations exist."""
        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            subject = call_args[0][0]
            body = call_args[0][1]

            # Check subject contains today's date
            today = now().strftime("%Y-%m-%d")
            assert today in subject
            assert "Daily Validation Report" in subject

            # Check body contains correct information
            assert "Total Validations: 0" in body
            assert "Daily Validation Report" in body
            assert "No user activity in the reported period" in body

    def test_daily_validation_report_with_validations(self):
        """Test daily validation report with validations in the last 24 hours."""
        # Create a validation from 12 hours ago
        with freeze_time(now() - timedelta(hours=12)):
            ValidationCoreFactory()

        # Create a validation from 25 hours ago (should not be counted)
        with freeze_time(now() - timedelta(hours=25)):
            ValidationCoreFactory()

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            subject = call_args[0][0]
            body = call_args[0][1]

            # Check subject contains today's date
            today = now().strftime("%Y-%m-%d")
            assert today in subject
            assert "Daily Validation Report" in subject

            # Check body contains correct information
            assert "Total Validations: 1" in body
            assert "Daily Validation Report" in body
            assert "Validations by user:" in body

    def test_daily_validation_report_multiple_validations(self):
        """Test daily validation report with multiple validations."""
        # Create multiple validations from 6 hours ago
        with freeze_time(now() - timedelta(hours=6)):
            for _ in range(5):
                ValidationCoreFactory()

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            body = call_args[0][1]

            # Check body contains correct information
            assert "Total Validations: 5" in body

    def test_daily_validation_report_user_table(self):
        """Test daily validation report includes user table with correct data."""
        # Create users
        user1 = UserFactory(first_name="John", last_name="Doe", email="john@example.com")
        user2 = UserFactory(first_name="Jane", last_name="Smith", email="jane@example.com")

        # Create validations for different users
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(user=user1)  # 1 validation for user1
            ValidationCoreFactory(user=user1)  # 2nd validation for user1
            ValidationCoreFactory(user=user2)  # 1 validation for user2

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            body = call_args[0][1]

            # Check body contains correct information
            assert "Total Validations: 3" in body
            assert "Validations by user:" in body
            assert "John Doe (john@example.com)" in body
            assert "Jane Smith (jane@example.com)" in body
            # Check that user1 appears first (more validations)
            user1_index = body.find("John Doe (john@example.com)")
            user2_index = body.find("Jane Smith (jane@example.com)")
            assert user1_index < user2_index

    def test_daily_validation_report_user_without_name(self):
        """Test daily validation report handles users without names."""
        # Create user without name
        user = UserFactory(first_name="", last_name="", email="anonymous@example.com")

        # Create validation
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(user=user)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            body = call_args[0][1]

            # Check body contains correct information
            assert "Total Validations: 1" in body
            assert "Validations by user:" in body
            assert "anonymous@example.com" in body
            # Should not contain empty parentheses
            assert "(anonymous@example.com)" not in body

    def test_daily_validation_report_cop_version_table(self):
        """Test daily validation report includes CoP version table with correct data."""
        # Create validations with different CoP versions
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(cop_version="5.1")  # 1 validation for CoP 5.1
            ValidationCoreFactory(cop_version="5.1")  # 2nd validation for CoP 5.1
            ValidationCoreFactory(cop_version="5.0")  # 1 validation for CoP 5.0
            ValidationCoreFactory(cop_version="")  # 1 validation with no CoP version

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            body = call_args[0][1]

            # Check body contains correct information
            assert "Total Validations: 4" in body
            assert "Validations by CoP version:" in body
            assert "5.1" in body
            assert "5.0" in body
            assert "Unknown" in body  # For empty cop_version
            # Check that CoP 5.1 appears first (more validations)
            cop51_index = body.find("5.1")
            cop50_index = body.find("5.0")
            assert cop51_index < cop50_index

    def test_daily_validation_report_no_cop_version_data(self):
        """Test daily validation report handles case with no CoP version data."""
        # Create validations without CoP version data
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(cop_version="")
            ValidationCoreFactory(cop_version="")

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            body = call_args[0][1]

            # Check body contains correct information
            assert "Total Validations: 2" in body
            assert "Validations by CoP version:" in body
            assert "Unknown" in body
            assert "No CoP version data in the reported period" not in body
