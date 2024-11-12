"""
Simple CLI client to upload a file for validation to the COUNTER validation tool.
It relies on the API Key access to the COUNTER validation tool and requires an API key
to be set in the environment variable COUNTER_VALIDATION_API_KEY.
"""

from time import sleep

import requests
from decouple import config
from termcolor import colored


def pprint_response(response_data):
    for key, value in response_data.items():
        if key in ["result_data"]:
            continue
        extra = ["underline"] if key == "id" else []
        color = "yellow" if key == "validation_result" else "light_grey"
        print(" ", colored(f"{key}: {value}", color, attrs=extra))


COUNTER_VALIDATION_API_URL = "https://api.sushi-counter.org/validate"
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", help="Name of the file to upload for validation")
    parser.add_argument(
        "--api-url",
        default=COUNTER_VALIDATION_API_URL,
        help="URL of the COUNTER validation API",
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="API key for the COUNTER validation API. If not set, the value from the environment "
        "variable COUNTER_VALIDATION_API_KEY is used",
    )
    parser.add_argument("--platform-name", "-p", help="Name of the platform to store in the record")
    parser.add_argument(
        "--platform-id",
        "-i",
        help="ID of the platform to store in the record - should be a UUID string from the COUNTER "
        "registry",
    )
    parser.add_argument(
        "-w", "--wait", action="store_true", help="Wait for the validation to finish"
    )

    args = parser.parse_args()
    api_key = args.api_key or config("COUNTER_VALIDATION_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not set - please use the --api-key option, add a COUNTER_VALIDATION_API_KEY "
            "variable into an .env file, or set the COUNTER_VALIDATION_API_KEY environment "
            "variable"
        )
    if args.platform_name and args.platform_id:
        raise ValueError("Please provide either --platform-name or --platform-id, not both")

    print(
        f"Uploading {args.filename} "
        f"with platform {args.platform_name} "
        f"for validation to {args.api_url}..."
    )
    with open(args.filename, "rb") as f:
        files = {"file": f}
        data = {"platform_name": args.platform_name, "platform": args.platform_id}
        headers = {"Authorization": f"Api-Key {api_key}"}
        response = requests.post(
            args.api_url.rstrip("/") + "/api/v1/validations/validation/file/",
            data=data,
            files=files,
            headers=headers,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(colored(f"Error: {e}", "red"))
            print(colored(response.text, "yellow"))
            exit(1)

    print(colored("Validation uploaded successfully. API response:\n", "green"))
    pprint_response(response.json())

    validation_id = response.json()["id"]

    if args.wait:
        print(f"Waiting for validation '{validation_id}' to finish...")
        while response.json()["status"] <= 1:
            sleep(1)
            response = requests.get(
                args.api_url.rstrip("/") + f"/api/v1/validations/validation/{validation_id}/",
                headers=headers,
            )
            response.raise_for_status()

        print(colored("Validation finished. API response:\n", "green"))
        pprint_response(response.json())

    print(
        f"You can see the validation results at: "
        f"{args.api_url.rstrip('/')}/validation/{validation_id}/"
    )
