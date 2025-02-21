from enum import Enum

from django.db import models


class SeverityLevel(models.IntegerChoices):
    UNKNOWN = 0, "Unknown"
    PASSED = 10, "Passed"
    NOTICE = 20, "Notice"
    WARNING = 30, "Warning"
    ERROR = 40, "Error"
    CRITICAL_ERROR = 50, "Critical error"
    FATAL_ERROR = 60, "Fatal error"

    @classmethod
    def by_label(cls, label):
        for member in cls:
            if member.label == label:
                return member
        return cls.UNKNOWN

    @classmethod
    def by_any_value(cls, value) -> "SeverityLevel | None":
        for member in cls:
            if member.value == value or member.label == value or member.name == value:
                return member
        return None


class ValidationStatus(models.IntegerChoices):
    WAITING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILURE = 3


class MessageKeys(Enum):
    level = "l"


severity_to_color = {
    SeverityLevel.UNKNOWN: "#aaaaaa",
    SeverityLevel.PASSED: "#0fa40f",
    SeverityLevel.NOTICE: "#0267b4",
    SeverityLevel.WARNING: "#fc6100",
    SeverityLevel.ERROR: "#dd0000",
    SeverityLevel.CRITICAL_ERROR: "#aa0000",
    SeverityLevel.FATAL_ERROR: "#8f0026",
}
