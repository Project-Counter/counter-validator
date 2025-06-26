"""
Simple CLI client to start a validation of a COUNTER API using the COUNTER validator.
It relies on the API Key access to the COUNTER validator and requires an API key
to be set in the environment variable COUNTER_VALIDATOR_API_KEY.
"""

from calendar import monthrange
from datetime import date, timedelta

from utils import create_arg_parser, make_request, validate_args

REPORTS = [
    "TR",
    "TR_J1",
    "TR_J2",
    "TR_J3",
    "TR_J4",
    "TR_B1",
    "TR_B2",
    "TR_B3",
    "PR",
    "PR_P1",
    "IR",
    "IR_A1",
    "IR_M1",
    "DR",
    "DR_D1",
    "DR_D2",
]


def last_month_start() -> str:
    today = date.today()
    first_day = today.replace(day=1)
    last_month = first_day - timedelta(days=1)
    return last_month.replace(day=1).isoformat()


def month_end(start_date: date | str) -> str:
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    return start_date.replace(day=monthrange(start_date.year, start_date.month)[1]).isoformat()


if __name__ == "__main__":
    parser = create_arg_parser(__doc__)

    # COUNTER API specific arguments
    parser.add_argument("--url", "-u", help="URL of the tested COUNTER API", required=True)
    parser.add_argument(
        "--customer-id", "-c", help="Customer ID for the COUNTER API", required=True
    )
    parser.add_argument("--requestor-id", "-r", help="Requestor ID for the COUNTER API")
    parser.add_argument("--api-key", "-k", help="API key for the COUNTER API")
    parser.add_argument(
        "--platform-filter",
        "-p",
        help="Value of the Platform attribute to be passed to the COUNTER API",
    )
    parser.add_argument(
        "--cop-version",
        "-s",
        help="CoP version to be used for the validation",
        default="5",
        choices=["5", "5.1"],
    )
    parser.add_argument(
        "--report",
        "-t",
        help="Report to be requested from the COUNTER API",
        default="TR",
        choices=REPORTS,
    )
    parser.add_argument(
        "--begin-date",
        "-b",
        help="Begin date for the report. Default is the first day of the last finished month",
        default=last_month_start(),
    )
    parser.add_argument(
        "--end-date",
        "-e",
        help="End date for the report. Default is the end of the month of the begin date",
    )

    args = parser.parse_args()
    validate_args(args)

    credentials = {
        "customer_id": args.customer_id,
    }
    if args.requestor_id:
        credentials["requestor_id"] = args.requestor_id
    if args.platform_filter:
        credentials["platform"] = args.platform_filter
    if args.api_key:
        credentials["api_key"] = args.api_key

    end_date = args.end_date or month_end(args.begin_date)

    data = {
        "credentials": credentials,
        "cop_version": args.cop_version,
        "begin_date": args.begin_date,
        "end_date": end_date,
        "url": args.url,
        "report_code": args.report,
    }

    print(
        f"Sending request for validation of '{args.url}' for validation to {args.validator_url}..."
    )

    response = make_request(
        args.validator_url,
        "/api/v1/validations/counter-api-validation/",
        args.validator_api_key,
        data,
        wait=args.wait,
    )
