import argparse
from time import sleep
from urllib.parse import urljoin

import requests
from decouple import config
from termcolor import colored

COUNTER_VALIDATOR_API_URL = "http://localhost:8028"


def pprint_response(response_data):
    for key, value in response_data.items():
        if key in ["result_data"]:
            continue
        extra = ["underline"] if key == "id" else []
        color = "yellow" if key == "validation_result" else "light_grey"
        print(" ", colored(f"{key}: {value}", color, attrs=extra))


def make_request(
    validator_url: str, path: str, api_key: str, data: dict, files: dict = None, wait: bool = False
):
    headers = {"Authorization": f"Api-Key {api_key}"}
    attrs = {"json": data}
    if files:
        attrs["files"] = files
    response = requests.post(urljoin(validator_url, path), headers=headers, **attrs)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(colored(f"Error: {e}", "red"))
        print(colored(response.text, "yellow"))
        exit(1)

    print(colored("Validation uploaded successfully. API response:\n", "green"))
    pprint_response(response.json())

    validation_id = response.json()["id"]

    if wait:
        print(f"Waiting for validation '{validation_id}' to finish...")
        while response.json()["status"] <= 1:
            sleep(1)
            response = requests.get(
                urljoin(validator_url, f"/api/v1/validations/validation/{validation_id}/"),
                headers=headers,
            )
            response.raise_for_status()

        print(colored("Validation finished. API response:\n", "green"))
        pprint_response(response.json())

    print(
        f"You can see the validation results at: "
        f"{validator_url.rstrip('/')}/validation/{validation_id}/"
    )


def create_arg_parser(desc: str):
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        "--validator-url",
        default=COUNTER_VALIDATOR_API_URL,
        help="URL of the COUNTER validation API",
    )
    parser.add_argument(
        "--validator-api-key",
        default=config("COUNTER_VALIDATOR_API_KEY"),
        help="API key for the COUNTER validation API. If not set, the value from the environment "
        "variable COUNTER_VALIDATOR_API_KEY is used",
    )
    parser.add_argument(
        "-w", "--wait", action="store_true", help="Wait for the validation to finish"
    )

    return parser


def validate_args(args):
    if not args.validator_api_key:
        raise ValueError(
            "Validator API key not set - please use the --validator-api-key option,"
            " add a COUNTER_VALIDATOR_API_KEY variable into an .env file, or set the "
            "COUNTER_VALIDATOR_API_KEY environment variable"
        )
