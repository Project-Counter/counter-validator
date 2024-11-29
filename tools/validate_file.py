"""
Simple CLI client to upload a file for validation to the COUNTER validation tool.
It relies on the API Key access to the COUNTER validation tool and requires an API key
to be set in the environment variable COUNTER_VALIDATION_API_KEY.
"""

from utils import create_arg_parser, make_request, validate_args

if __name__ == "__main__":
    parser = create_arg_parser(__doc__)
    parser.add_argument("filename", help="Name of the file to upload for validation")
    parser.add_argument("--platform-name", "-p", help="Name of the platform to store in the record")
    parser.add_argument(
        "--platform-id",
        "-i",
        help="ID of the platform to store in the record - should be a UUID string from the COUNTER "
        "registry",
    )

    args = parser.parse_args()
    # common validation of the arguments
    validate_args(args)

    # validations specific to this script
    if args.platform_name and args.platform_id:
        raise ValueError("Please provide either --platform-name or --platform-id, not both")

    print(
        f"Uploading {args.filename} "
        f"with platform {args.platform_name} "
        f"for validation to {args.validator_url}..."
    )

    with open(args.filename, "rb") as f:
        data = {"platform_name": args.platform_name, "platform": args.platform_id}
        response = make_request(
            args.validator_url,
            "/api/v1/validations/validation/file/",
            args.validator_api_key,
            data,
            files={"file": f},
            wait=args.wait,
        )
