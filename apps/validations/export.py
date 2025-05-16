import tempfile
from datetime import datetime

import xlsxwriter
from django.contrib.sites.shortcuts import get_current_site
from django.utils.timezone import now
from xlsxwriter.worksheet import Worksheet

from validations.enums import SeverityLevel, severity_to_color
from validations.models import Validation, ValidationMessage

XSLX_COL_WIDTH_ADJ_RATIO = 0.75  # how to scale column width compared to the computed value
XSLX_COL_WIDTH_ADJ_CONST = 2  # what to add to the scaled column width


def xslx_scale_column_width(width, max_col_width=60):
    return min(int(width * XSLX_COL_WIDTH_ADJ_RATIO) + XSLX_COL_WIDTH_ADJ_CONST, max_col_width)


def format_date(d: datetime):
    return d.strftime("%Y-%m-%d %H:%M:%S%z")


class XlsxListWriter:
    MAX_COL_WIDTH = 60

    def __init__(self, sheet: Worksheet, default_fmt):
        self.sheet: Worksheet = sheet
        self.default_fmt = default_fmt
        self._current_row = 0
        self._widths = 100 * [0]

    def writerow(self, values: list, fmt=None):
        self.sheet.write_row(
            row=self._current_row, col=0, data=values, cell_format=fmt or self.default_fmt
        )

        self._current_row += 1
        for i, cell in enumerate(values[:100]):
            self._widths[i] = max(self._widths[i], len(str(cell)))

    def finalize(self):
        for col, width in enumerate(self._widths):
            if width:
                width = xslx_scale_column_width(width)
                # first column has header_format, other have cell_format
                self.sheet.set_column(col, col, width)


class ValidationXlsxExporter:
    def __init__(self, validation: Validation):
        self.validation = validation
        self.base_fmt_dict = {"font_name": "Arial", "font_size": 9}
        self.workbook = None
        self.base_fmt = None
        self.header_fmt = None
        self.title_fmt = None
        self.severity_fmts = {}
        self._row_num = 0

    def export(self) -> bytes:
        with tempfile.NamedTemporaryFile("wb") as tmp_file:
            workbook = xlsxwriter.Workbook(tmp_file.name, {"constant_memory": True})
            # store reference to workbook - we may need it in the methods called later
            self.workbook = workbook
            self.base_fmt = workbook.add_format(self.base_fmt_dict)
            self.header_fmt = workbook.add_format({"bold": True, **self.base_fmt_dict})
            self.title_fmt = workbook.add_format(
                {**self.base_fmt_dict, "bold": True, "font_size": 24}
            )

            # create formats for different severity levels
            for level in SeverityLevel:
                self.severity_fmts[level] = workbook.add_format(
                    {
                        "font_color": severity_to_color[level],
                        **self.base_fmt_dict,
                    }
                )

            # add metadata sheet
            self.create_metadata_sheet()
            # add messages sheet
            self.create_messages_sheet()

            workbook.close()
            with open(tmp_file.name, "rb") as infile:
                infile.seek(0)
                return infile.read()

    def create_metadata_sheet(self):
        sheet = self.workbook.add_worksheet("metadata")
        sheet.insert_image(
            0,
            2,
            "frontend/public/counter-logo-new.png",
            {
                "x_offset": 30,
                "y_offset": 20,
                "x_scale": 0.8,
                "y_scale": 0.8,
                "decorative": True,
            },
        )
        writer = XlsxListWriter(sheet, self.base_fmt)
        writer.writerow(["COUNTER Validation Report"], fmt=self.title_fmt)
        writer.writerow(["Note", self.validation.user_note])
        writer.writerow(["Validation date", format_date(self.validation.core.created)])
        writer.writerow(["Exported", format_date(now())])
        host = get_current_site(None)
        writer.writerow(["Validation URL", f"https://{host}/validation/{self.validation.id}/"])
        writer.writerow([])
        api_validation = hasattr(self.validation, "counterapivalidation")
        writer.writerow(["Validation details"], fmt=self.header_fmt)
        writer.writerow(["Data source", "COUNTER API" if api_validation else "File"])
        if not api_validation:
            writer.writerow(["File name", self.validation.filename])
        writer.writerow(["Validation result", self.validation.core.get_validation_result_display()])
        writer.writerow([])

        writer.writerow(["Extracted data"], fmt=self.header_fmt)
        header = (
            self.validation.result_data.get("header", {}) if self.validation.result_data else {}
        )
        writer.writerow(["CoP version", self.validation.core.cop_version])
        writer.writerow(["Report code", self.validation.core.report_code])
        writer.writerow(["Begin date", header.get("begin_date", "-")])
        writer.writerow(["End date", header.get("end_date", "-")])
        writer.writerow(["Institution name", header.get("institution_name", "-")])
        writer.writerow(["Created by", header.get("created_by", "-")])
        writer.writerow(["Created", header.get("created", "-")])
        writer.writerow([])

        if api_validation:
            api_data = self.validation.counterapivalidation
            writer.writerow(["COUNTER API details"], fmt=self.header_fmt)
            writer.writerow(["URL", api_data.url])
            writer.writerow(["API endpoint", self.validation.core.api_endpoint])
            writer.writerow(["Requested CoP version", api_data.requested_cop_version])
            writer.writerow(["Requested report code", api_data.requested_report_code])
            writer.writerow(["Requested begin date", str(api_data.requested_begin_date)])
            writer.writerow(["Requested end date", str(api_data.requested_end_date)])
            writer.writerow(["Use short dates", api_data.use_short_dates and "Yes" or "No"])
            writer.writerow(["Credentials"], fmt=self.header_fmt)
            for key, value in api_data.credentials.items():
                writer.writerow([key, value])
            writer.writerow(["Extra attributes"], fmt=self.header_fmt)
            for key, value in api_data.requested_extra_attributes.items():
                writer.writerow([key, value])
            writer.writerow([])

        writer.writerow(["Result statistics"], fmt=self.header_fmt)
        for level, count in self.validation.core.stats.items():
            writer.writerow([level, count], self.severity_fmts[SeverityLevel.by_any_value(level)])

        writer.finalize()

    def create_messages_sheet(self):
        sheet = self.workbook.add_worksheet("messages")
        writer = XlsxListWriter(sheet, self.base_fmt)
        rows = ["Severity", "Code", "Location", "Summary", "Message", "Hint", "Data"]
        writer.writerow(rows, fmt=self.header_fmt)

        for msg in self.validation.messages.all().iterator():
            self.write_message(writer, msg)

        writer.finalize()
        sheet.autofilter(0, 0, self._row_num, len(rows) - 1)

    def write_message(self, writer: XlsxListWriter, msg: ValidationMessage):
        writer.writerow(
            [
                msg.get_severity_display(),
                msg.code,
                msg.location,
                msg.summary,
                msg.message,
                msg.hint,
                msg.data,
            ],
            fmt=self.severity_fmts[msg.severity],
        )
