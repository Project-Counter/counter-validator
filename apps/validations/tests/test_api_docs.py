"""
Verify that API paths in the documentation match the real API.

These tests parse ``docs/*.rst`` so new examples are checked automatically.
They would have caught the original bug where the COUNTER API endpoint was
documented as ``/api/v1/validations/validation/counter-api/`` (POST not
allowed) while the working path is ``/api/v1/validations/counter-api-validation/``.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import Resolver404, resolve

from validations.fake_data import ValidationFactory, ValidationMessageFactory

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = REPO_ROOT / "docs"
SAMPLE_REPORT = REPO_ROOT / "test_data" / "reports" / "50-Sample-TR.csv"

ENDPOINT_RE = re.compile(
    r"^Endpoint:\s+``(?P<path>/[^`]+)``\s*\n+"
    r"Method:\s+``(?P<method>[A-Z]+)``",
    re.MULTILINE,
)
BASH_BLOCK_RE = re.compile(
    r"^[ \t]*\.\. code-block:: bash\n\n(?P<body>(?:[ \t]+.*\n)+)",
    re.MULTILINE,
)
API_URL_RE = re.compile(r"https?://[^/\s\"']+(/api/v1/[^\"'\s]+)")
BACKTICK_API_PATH_RE = re.compile(r"``(/api/v1/[^`]+)``")
FORM_FIELD_RE = re.compile(r'-F\s+"([^=]+)=([^"]*)"')


@dataclass(frozen=True)
class DocumentedEndpoint:
    path: str
    method: str
    source: str
    line: int


@dataclass(frozen=True)
class CurlExample:
    method: str
    path: str
    json_body: dict | None
    form_fields: dict[str, str]
    source: str
    line: int


def _line_number(text: str, index: int) -> int:
    return text[:index].count("\n") + 1


def _rst_files() -> list[Path]:
    return sorted(DOCS_DIR.glob("*.rst"))


def extract_documented_endpoints(text: str, source: str = "docs") -> list[DocumentedEndpoint]:
    endpoints = []
    for match in ENDPOINT_RE.finditer(text):
        endpoints.append(
            DocumentedEndpoint(
                path=match.group("path"),
                method=match.group("method"),
                source=source,
                line=_line_number(text, match.start()),
            )
        )
    return endpoints


def _extract_json_body(body: str) -> dict | None:
    match = re.search(r"""-d\s+(['\"])""", body)
    if not match:
        return None
    quote = match.group(1)
    start = match.end()
    end = body.find(quote, start)
    if end == -1:
        raise ValueError("Unterminated -d body in curl example")
    return json.loads(body[start:end])


def _extract_form_fields(body: str) -> dict[str, str]:
    return dict(FORM_FIELD_RE.findall(body))


def parse_curl_block(body: str, source: str, line: int) -> CurlExample | None:
    if "curl" not in body:
        return None
    url_match = API_URL_RE.search(body)
    if not url_match:
        return None
    method_match = re.search(r"-X\s+([A-Za-z]+)", body)
    method = method_match.group(1).upper() if method_match else "GET"
    path = urlsplit(url_match.group(0)).path
    if url_match.group(0).endswith("/") and not path.endswith("/"):
        path += "/"
    return CurlExample(
        method=method,
        path=path,
        json_body=_extract_json_body(body),
        form_fields=_extract_form_fields(body),
        source=source,
        line=line,
    )


def extract_curl_examples(text: str, source: str = "docs") -> list[CurlExample]:
    examples = []
    for match in BASH_BLOCK_RE.finditer(text):
        example = parse_curl_block(match.group("body"), source, _line_number(text, match.start()))
        if example:
            examples.append(example)
    return examples


def pair_endpoints_with_curl_examples(
    endpoints: list[DocumentedEndpoint], examples: list[CurlExample]
) -> list[tuple[DocumentedEndpoint, CurlExample]]:
    pairs = []
    for index, endpoint in enumerate(endpoints):
        next_line = endpoints[index + 1].line if index + 1 < len(endpoints) else float("inf")
        following = [ex for ex in examples if endpoint.line < ex.line < next_line]
        if following:
            pairs.append((endpoint, following[0]))
    return pairs


def documented_endpoints() -> list[DocumentedEndpoint]:
    endpoints = []
    for path in _rst_files():
        endpoints.extend(extract_documented_endpoints(path.read_text(), path.name))
    return endpoints


def curl_examples() -> list[CurlExample]:
    examples = []
    for path in _rst_files():
        examples.extend(extract_curl_examples(path.read_text(), path.name))
    return examples


def backtick_api_paths() -> list[tuple[str, str, int]]:
    found = []
    for path in _rst_files():
        text = path.read_text()
        for match in BACKTICK_API_PATH_RE.finditer(text):
            found.append((match.group(1), path.name, _line_number(text, match.start())))
    return found


def concrete_path(path: str, validation_id) -> str:
    path = path.replace("<id>", str(validation_id))
    path = re.sub(r"<[^>]+>", str(validation_id), path)
    return urlsplit(path).path


def _endpoint_id(endpoint: DocumentedEndpoint) -> str:
    return f"{endpoint.method} {endpoint.path}"


def _curl_id(example: CurlExample) -> str:
    return f"{example.method} {example.path}"


def _pair_id(pair: tuple[DocumentedEndpoint, CurlExample]) -> str:
    endpoint, example = pair
    return f"{endpoint.source}:{endpoint.line} {endpoint.method} {endpoint.path}"


DOCUMENTED_ENDPOINTS = documented_endpoints()
CURL_EXAMPLES = curl_examples()
ENDPOINT_CURL_PAIRS = pair_endpoints_with_curl_examples(DOCUMENTED_ENDPOINTS, CURL_EXAMPLES)
BACKTICK_API_PATHS = backtick_api_paths()


MISMATCHED_DOCS = """
Endpoint: ``/api/v1/validations/validation/counter-api/``

Method: ``POST``

.. code-block:: bash

   curl \\
   -X POST \\
   "https://validator.countermetrics.org/api/v1/validations/counter-api-validation/"
"""


class TestApiDocsParser:
    def test_extracts_endpoint_and_matching_curl(self):
        rst = """
Endpoint: ``/api/v1/validations/validation/file/``

Method: ``POST``

.. code-block:: bash

   curl \\
   -X POST \\
   -F "file=@TR.csv" \\
   "https://validator.countermetrics.org/api/v1/validations/validation/file/"
"""
        endpoints = extract_documented_endpoints(rst, "sample.rst")
        examples = extract_curl_examples(rst, "sample.rst")
        assert len(endpoints) == 1
        assert endpoints[0].path == "/api/v1/validations/validation/file/"
        assert endpoints[0].method == "POST"
        assert len(examples) == 1
        assert examples[0].path == "/api/v1/validations/validation/file/"
        assert examples[0].method == "POST"
        assert examples[0].form_fields == {"file": "@TR.csv"}

    def test_detects_endpoint_curl_path_mismatch(self):
        endpoints = extract_documented_endpoints(MISMATCHED_DOCS, "bad.rst")
        examples = extract_curl_examples(MISMATCHED_DOCS, "bad.rst")
        pairs = pair_endpoints_with_curl_examples(endpoints, examples)
        assert len(pairs) == 1
        endpoint, example = pairs[0]
        assert endpoint.path != example.path

    def test_parses_json_body_from_curl_example(self):
        rst = """
.. code-block:: bash

   curl \\
   -X POST \\
   -d '{
     "url": "https://example.com/sushi",
     "credentials": {"customer_id": "abc"}
   }' \\
   "https://validator.countermetrics.org/api/v1/validations/counter-api-validation/"
"""
        examples = extract_curl_examples(rst, "sample.rst")
        assert len(examples) == 1
        assert examples[0].json_body == {
            "url": "https://example.com/sushi",
            "credentials": {"customer_id": "abc"},
        }

    def test_docs_contain_endpoints_and_curl_examples(self):
        assert DOCUMENTED_ENDPOINTS, "No 'Endpoint:' + 'Method:' pairs found in docs/"
        assert CURL_EXAMPLES, "No curl examples with /api/v1/ paths found in docs/"
        assert ENDPOINT_CURL_PAIRS, "No Endpoint/curl pairs found in docs/"


@pytest.mark.parametrize("pair", ENDPOINT_CURL_PAIRS, ids=_pair_id)
def test_documented_endpoint_matches_following_curl_example(pair):
    endpoint, example = pair
    assert endpoint.path == example.path, (
        f"{endpoint.source}:{endpoint.line} documents {endpoint.path}, "
        f"but the following curl example uses {example.path}"
    )
    assert endpoint.method == example.method, (
        f"{endpoint.source}:{endpoint.line} documents {endpoint.method}, "
        f"but the following curl example uses {example.method}"
    )


@pytest.mark.parametrize(
    "path,source,line",
    BACKTICK_API_PATHS,
    ids=[f"{source}:{line} {path}" for path, source, line in BACKTICK_API_PATHS],
)
def test_backtick_api_paths_resolve(path, source, line):
    resolved_path = concrete_path(path, "00000000-0000-0000-0000-000000000001")
    try:
        resolve(resolved_path)
    except Resolver404:
        pytest.fail(f"{source}:{line} documents unresolvable path {path}")


@pytest.mark.django_db
@pytest.mark.parametrize("endpoint", DOCUMENTED_ENDPOINTS, ids=_endpoint_id)
def test_documented_method_is_allowed(endpoint, client_with_api_key, normal_user):
    """
    Hitting a documented path with the documented method must not return
    404 or 405. 400 is acceptable here: it means the route exists and the
    method is allowed, but the request body was empty.
    """
    validation = ValidationFactory(core__user=normal_user)
    path = concrete_path(endpoint.path, validation.pk)
    method = endpoint.method.lower()
    if method in {"post", "put", "patch"}:
        response = getattr(client_with_api_key, method)(path, data={}, format="json")
    else:
        response = getattr(client_with_api_key, method)(path)
    assert response.status_code != 404, f"{endpoint.method} {path} was not found"
    assert response.status_code != 405, (
        f"{endpoint.method} is not allowed on {path}: "
        f"{response.json().get('detail', response.content)}"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("example", CURL_EXAMPLES, ids=_curl_id)
def test_curl_example_succeeds(example, client_with_api_key, normal_user):
    """Replay each documented curl example against the live API."""
    validation = ValidationFactory(core__user=normal_user)
    ValidationMessageFactory.create_batch(3, validation=validation)
    path = concrete_path(example.path, validation.pk)
    method = example.method.lower()

    with (
        patch("validations.tasks.validate_file.delay_on_commit"),
        patch("validations.tasks.validate_counter_api.delay_on_commit"),
    ):
        if example.form_fields:
            data = {}
            for key, value in example.form_fields.items():
                if value.startswith("@"):
                    data[key] = SimpleUploadedFile(
                        Path(value[1:]).name,
                        SAMPLE_REPORT.read_bytes(),
                        content_type="text/csv",
                    )
                else:
                    data[key] = value
            response = getattr(client_with_api_key, method)(path, data=data, format="multipart")
        elif example.json_body is not None:
            response = getattr(client_with_api_key, method)(
                path, data=example.json_body, format="json"
            )
        else:
            response = getattr(client_with_api_key, method)(path)

    assert 200 <= response.status_code < 300, (
        f"{example.source}:{example.line} {example.method} {path} "
        f"returned {response.status_code}: {getattr(response, 'data', response.content)}"
    )
