"""
Simple CLI client to upload a file for validation to the COUNTER validator.
It relies on the API Key access to the COUNTER validator and requires an API key
to be set in the environment variable COUNTER_VALIDATION_API_KEY.
"""

from utils import create_arg_parser, make_request, validate_args

if __name__ == "__main__":
    parser = create_arg_parser(__doc__)
    parser.add_argument("filename", help="Name of the file to upload for validation")
    parser.add_argument("--note", "-n", help="Free text note to attach to the validation")

    args = parser.parse_args()
    # common validation of the arguments
    validate_args(args)

    print(f"Uploading {args.filename} for validation to {args.validator_url}...")

    with open(args.filename, "rb") as f:
        data = {"user_note": args.note or ""}
        response = make_request(
            args.validator_url,
            "/api/v1/validations/validation/file/",
            args.validator_api_key,
            data,
            files={"file": f},
            wait=args.wait,
        )
