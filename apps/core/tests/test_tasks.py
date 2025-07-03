from datetime import timedelta
from unittest.mock import patch

import pytest
from django.conf import settings
from django.utils.timezone import now
from freezegun import freeze_time
from validations.enums import SeverityLevel
from validations.fake_data import ValidationCoreFactory

from core.fake_data import UserFactory
from core.tasks import async_mail_operators, daily_validation_report


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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check subject contains today's date
            today = now().strftime("%Y-%m-%d")
            assert today in subject
            assert "Daily Validation Report" in subject

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 0" in html_body
            assert "Total Validations: 0" in text_body
            assert "Daily Validation Report" in html_body
            assert "Daily Validation Report" in text_body
            assert "No user activity in the reported period" in text_body
            assert "No user activity in the reported period" in html_body

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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check subject contains today's date
            today = now().strftime("%Y-%m-%d")
            assert today in subject
            assert "Daily Validation Report" in subject

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 1" in html_body
            assert "Total Validations: 1" in text_body
            assert "Daily Validation Report" in html_body
            assert "Daily Validation Report" in text_body
            assert "Validations by user:" in text_body
            assert "Validations by user:" in html_body

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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 5" in html_body
            assert "Total Validations: 5" in text_body

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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 3" in html_body
            assert "Total Validations: 3" in text_body
            assert "Validations by user:" in html_body
            assert "Validations by user:" in text_body
            assert "John Doe (john@example.com)" in html_body
            assert "John Doe (john@example.com)" in text_body
            assert "Jane Smith (jane@example.com)" in html_body
            assert "Jane Smith (jane@example.com)" in text_body
            # Check that user1 appears first (more validations)
            user1_index = html_body.find("John Doe (john@example.com)")
            user2_index = html_body.find("Jane Smith (jane@example.com)")
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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 1" in html_body
            assert "Total Validations: 1" in text_body
            assert "Validations by user:" in html_body
            assert "Validations by user:" in text_body
            assert "anonymous@example.com" in html_body
            assert "anonymous@example.com" in text_body
            # Should not contain empty parentheses
            assert "(anonymous@example.com)" not in html_body
            assert "(anonymous@example.com)" not in text_body

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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 4" in html_body
            assert "Total Validations: 4" in text_body
            assert "Validations by CoP version:" in html_body
            assert "Validations by CoP version:" in text_body
            assert "5.1" in html_body
            assert "5.1" in text_body
            assert "5.0" in html_body
            assert "5.0" in text_body
            assert "Unknown" in html_body  # For empty cop_version
            assert "Unknown" in text_body  # For empty cop_version
            # Check that CoP 5.1 appears first (more validations)
            cop51_index = html_body.find("5.1")
            cop50_index = html_body.find("5.0")
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
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 2" in html_body
            assert "Total Validations: 2" in text_body
            assert "Validations by CoP version:" in html_body
            assert "Validations by CoP version:" in text_body
            assert "Unknown" in html_body
            assert "Unknown" in text_body
            assert "No CoP version data in the reported period" not in html_body
            assert "No CoP version data in the reported period" not in text_body

    def test_daily_validation_report_validation_result_table(self):
        """Test daily validation report includes validation result table with correct data."""
        # Create validations with different validation results
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)  # 1 validation passed
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)  # 2nd validation passed
            ValidationCoreFactory(validation_result=SeverityLevel.WARNING)  # 1 validation warning
            ValidationCoreFactory(validation_result=SeverityLevel.ERROR)  # 1 validation error

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 4" in html_body
            assert "Total Validations: 4" in text_body
            assert "Validations by result:" in html_body
            assert "Validations by result:" in text_body
            assert "Passed" in html_body
            assert "Passed" in text_body
            assert "Warning" in html_body
            assert "Warning" in text_body
            assert "Error" in html_body
            assert "Error" in text_body
            # Check that Passed appears first (more validations)
            passed_index = html_body.find("Passed")
            warning_index = html_body.find("Warning")
            assert passed_index < warning_index

    def test_daily_validation_report_validation_result_ordering(self):
        """
        Test daily validation report validation result table is ordered by count then by
        result.
        """
        # Create validations with different validation results
        with freeze_time(now() - timedelta(hours=6)):
            # Create 3 warnings (should appear first due to count)
            for _ in range(3):
                ValidationCoreFactory(validation_result=SeverityLevel.WARNING)
            # Create 2 errors (should appear second)
            for _ in range(2):
                ValidationCoreFactory(validation_result=SeverityLevel.ERROR)
            # Create 1 passed (should appear third)
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 6" in html_body
            assert "Total Validations: 6" in text_body
            assert "Validations by result:" in html_body
            assert "Validations by result:" in text_body

            # Check ordering: Warning (3) should appear before Error (2), which should appear before
            # Passed (1)
            warning_index = html_body.find("Warning")
            error_index = html_body.find("Error")
            passed_index = html_body.find("Passed")

            assert warning_index < error_index
            assert error_index < passed_index

    def test_daily_validation_report_all_validation_results(self):
        """Test daily validation report includes all possible validation result types."""
        # Create validations with all possible validation results
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(validation_result=SeverityLevel.UNKNOWN)
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)
            ValidationCoreFactory(validation_result=SeverityLevel.NOTICE)
            ValidationCoreFactory(validation_result=SeverityLevel.WARNING)
            ValidationCoreFactory(validation_result=SeverityLevel.ERROR)
            ValidationCoreFactory(validation_result=SeverityLevel.CRITICAL_ERROR)
            ValidationCoreFactory(validation_result=SeverityLevel.FATAL_ERROR)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 7" in html_body
            assert "Total Validations: 7" in text_body
            assert "Validations by result:" in html_body
            assert "Validations by result:" in text_body

            # Check all validation result types are present
            assert "Unknown" in html_body
            assert "Unknown" in text_body
            assert "Passed" in html_body
            assert "Passed" in text_body
            assert "Notice" in html_body
            assert "Notice" in text_body
            assert "Warning" in html_body
            assert "Warning" in text_body
            assert "Error" in html_body
            assert "Error" in text_body
            assert "Critical error" in html_body
            assert "Critical error" in text_body
            assert "Fatal error" in html_body
            assert "Fatal error" in text_body

    def test_daily_validation_report_no_validation_result_data(self):
        """Test daily validation report handles case with no validation result data."""
        # Create validations outside the 24-hour window
        with freeze_time(now() - timedelta(hours=25)):
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)
            ValidationCoreFactory(validation_result=SeverityLevel.ERROR)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 0" in html_body
            assert "Total Validations: 0" in text_body
            assert "Validations by result:" in html_body
            assert "Validations by result:" in text_body
            assert "No validation result data in the reported period" in html_body
            assert "No validation result data in the reported period" in text_body

    def test_daily_validation_report_validation_result_with_unknown_value(self):
        """Test daily validation report handles unknown validation result values gracefully."""
        # Create a validation with an unknown validation result value
        with freeze_time(now() - timedelta(hours=6)):
            validation = ValidationCoreFactory()
            # Set an invalid validation result value
            validation.validation_result = 999
            validation.save()

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            text_body = call_args[0][1]
            html_body = call_args[0][2]

            # Check both HTML and text bodies contain correct information
            assert "<strong>Total Validations:</strong> 1" in html_body
            assert "Total Validations: 1" in text_body
            assert "Validations by result:" in html_body
            assert "Validations by result:" in text_body
            # Should display "Unknown" for invalid validation result values
            assert "Unknown" in html_body
            assert "Unknown" in text_body

    def test_daily_validation_report_validation_result_table_in_text_format(self):
        """Test daily validation report validation result table formatting in text version."""
        # Create validations with different validation results
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)
            ValidationCoreFactory(validation_result=SeverityLevel.WARNING)
            ValidationCoreFactory(validation_result=SeverityLevel.ERROR)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            text_body = call_args[0][1]

            # Check text formatting
            assert "Validations by result:" in text_body
            assert "Validation Result" in text_body
            assert "Validations" in text_body
            assert "Passed" in text_body
            assert "Warning" in text_body
            assert "Error" in text_body
            # Check for table formatting with dashes
            assert "-" * 50 in text_body

    def test_daily_validation_report_validation_result_colors_in_html(self):
        """Test daily validation report validation result colors are applied in HTML version."""
        # Create validations with different validation results
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)
            ValidationCoreFactory(validation_result=SeverityLevel.WARNING)
            ValidationCoreFactory(validation_result=SeverityLevel.ERROR)
            ValidationCoreFactory(validation_result=SeverityLevel.CRITICAL_ERROR)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            html_body = call_args[0][2]

            # Check that severity level colors are applied
            assert "severity-passed" in html_body
            assert "severity-warning" in html_body
            assert "severity-error" in html_body
            assert "severity-critical-error" in html_body

            # Check that CSS color definitions are included
            assert "color: #0fa40f" in html_body  # Passed color
            assert "color: #fc6100" in html_body  # Warning color
            assert "color: #dd0000" in html_body  # Error color
            assert "color: #aa0000" in html_body  # Critical error color

            # Check that the severity levels are wrapped in colored links with absolute URLs
            assert '<a href="https://' in html_body
            assert (
                '/validation/admin?severity=Passed" class="severity-link" '
                'style="color: #0fa40f;">Passed</a>' in html_body
            )
            assert (
                '/validation/admin?severity=Warning" class="severity-link" '
                'style="color: #fc6100;">Warning</a>' in html_body
            )
            assert (
                '/validation/admin?severity=Error" class="severity-link" '
                'style="color: #dd0000;">Error</a>' in html_body
            )
            assert (
                '/validation/admin?severity=Critical%20error" class="severity-link" '
                'style="color: #aa0000;">Critical error</a>' in html_body
            )

    def test_async_mail_operators_includes_validator_admins(self):
        """Test that validator admins are included in email recipients."""
        # Create a validator admin
        UserFactory(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            is_validator_admin=True,
            receive_operator_emails=True,
        )

        with patch("core.tasks.EmailMultiAlternatives") as mock_email:
            mock_email.return_value.send.return_value = None

            async_mail_operators("Test Subject", "Test body", "<html>Test</html>")

            # Check that EmailMultiAlternatives was called
            assert mock_email.called

            # Get the call arguments
            call_args = mock_email.call_args
            recipients = call_args[1]["to"]

            # Check that the validator admin is in the recipients
            assert "Admin User <admin@example.com>" in recipients

    def test_async_mail_operators_respects_receive_operator_emails(self, settings):
        """Test that users with receive_operator_emails=False are not included."""
        settings.OPERATORS = [("Foo", "foo@example.com")]  # make sure we have a recipient

        # Create a validator admin with receive_operator_emails=False
        UserFactory(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            is_validator_admin=True,
            receive_operator_emails=False,
        )

        with patch("core.tasks.EmailMultiAlternatives") as mock_email:
            mock_email.return_value.send.return_value = None

            async_mail_operators("Test Subject", "Test body", "<html>Test</html>")

            # Check that EmailMultiAlternatives was called
            assert mock_email.called

            # Get the call arguments
            call_args = mock_email.call_args
            recipients = call_args[1]["to"]

            # Check that the validator admin is NOT in the recipients
            assert "Admin User <admin@example.com>" not in recipients

    def test_async_mail_operators_deduplicates_recipients(self):
        """Test that duplicate recipients are removed."""
        # Create a validator admin with the same email as an operator
        UserFactory(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            is_validator_admin=True,
            receive_operator_emails=True,
        )

        with patch("core.tasks.settings") as mock_settings:
            # Mock the OPERATORS setting to include the same email
            mock_settings.OPERATORS = [("Admin User", "admin@example.com")]

            with patch("core.tasks.EmailMultiAlternatives") as mock_email:
                mock_email.return_value.send.return_value = None

                async_mail_operators("Test Subject", "Test body", "<html>Test</html>")

                # Check that EmailMultiAlternatives was called
                assert mock_email.called

                # Get the call arguments
                call_args = mock_email.call_args
                recipients = call_args[1]["to"]

                # Check that the email appears only once
                admin_emails = [r for r in recipients if "admin@example.com" in r]
                assert len(admin_emails) == 1

    def test_async_mail_operators_inactive_users_excluded(self, settings):
        """Test that inactive users are not included in recipients."""
        # Create an inactive validator admin
        UserFactory(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            is_validator_admin=True,
            receive_operator_emails=True,
            is_active=False,
        )

        settings.OPERATORS = [("Foo", "foo@example.com")]  # make sure we have a recipient

        with patch("core.tasks.EmailMultiAlternatives") as mock_email:
            mock_email.return_value.send.return_value = None

            async_mail_operators("Test Subject", "Test body", "<html>Test</html>")

            # Check that EmailMultiAlternatives was called
            assert mock_email.called

            # Get the call arguments
            call_args = mock_email.call_args
            recipients = call_args[1]["to"]

            # Check that the inactive validator admin is NOT in the recipients
            assert "Admin User <admin@example.com>" not in recipients

    def test_daily_validation_report_site_domain_in_context(self):
        """
        Test daily validation report includes site domain in template context for absolute URLs.
        """
        # Create a validation with a validation result
        with freeze_time(now() - timedelta(hours=6)):
            ValidationCoreFactory(validation_result=SeverityLevel.PASSED)

        with patch("core.tasks.async_mail_operators") as mock_mail_operators:
            daily_validation_report()

            # Check that the task was called
            assert mock_mail_operators.delay.called

            # Get the call arguments
            call_args = mock_mail_operators.delay.call_args
            html_body = call_args[0][2]

            # Check that the site domain is included in the HTML (should be in the links)
            # The default test site domain is "example.com"
            assert "example.com" in html_body
            assert "https://example.com/validation/admin?severity=Passed" in html_body


@pytest.mark.django_db
class TestAsyncMailOperators:
    """Test the async_mail_operators function."""

    subject = "Test Subject"
    text_body = "This is the text body."
    html_body = "<p>This is the <b>HTML</b> body.</p>"

    def test_async_mail_operators_with_html_body(self, monkeypatch):
        """Test that async_mail_operators sends multipart email when html_body is provided."""

        # Patch settings.OPERATORS to have a recipient
        monkeypatch.setattr("core.tasks.settings.OPERATORS", [("Test User", "test@example.com")])

        with patch("core.tasks.EmailMultiAlternatives") as mock_multi:
            mock_multi.return_value.send.return_value = None
            async_mail_operators(self.subject, self.text_body, self.html_body)

            # Check that EmailMultiAlternatives was called with correct kwargs
            assert mock_multi.called
            args, kwargs = mock_multi.call_args
            assert kwargs["subject"] == self.subject
            assert kwargs["body"] == self.text_body
            assert kwargs["from_email"] == settings.DEFAULT_FROM_EMAIL
            assert "test@example.com" in kwargs["to"][0]

            # Check that HTML alternative is attached
            mock_multi.return_value.attach_alternative.assert_called_once_with(
                self.html_body, "text/html"
            )
            mock_multi.return_value.send.assert_called_once_with(fail_silently=False)

    def test_async_mail_operators_without_html_body(self, monkeypatch):
        """Test that async_mail_operators sends plain text email when html_body is not provided."""

        # Patch settings.OPERATORS to have a recipient
        monkeypatch.setattr("core.tasks.settings.OPERATORS", [("Test User", "test@example.com")])

        with patch("core.tasks.send_mail") as mock_send_mail:
            async_mail_operators(self.subject, self.text_body)

            # Check that send_mail was called with correct kwargs
            assert mock_send_mail.called
            args, kwargs = mock_send_mail.call_args
            assert kwargs["subject"] == self.subject
            assert kwargs["message"] == self.text_body
            assert kwargs["from_email"] == settings.DEFAULT_FROM_EMAIL
            assert "test@example.com" in kwargs["recipient_list"][0]
            assert kwargs["fail_silently"] is False
