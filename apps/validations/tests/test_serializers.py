import pytest

from validations.serializers import FileValidationCreateSerializer


class TestFileValidationCreateSerializer:
    @pytest.mark.parametrize(
        ["filetype", "filename"],
        [
            ("csv", "50-Sample-TR.csv"),
            ("json", "50-Sample-TR.json"),
            ("xlsx", "50-Sample-TR.xlsx"),
            ("csv", "50-Sample-TR.tsv"),
        ],
    )
    def test_file_type_detection(self, filetype, filename):
        with open(f"test_data/reports/{filename}", "rb") as f:
            assert FileValidationCreateSerializer.file_to_type(f) == filetype
