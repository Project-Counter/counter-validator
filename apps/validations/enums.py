from enum import Enum

from django.db import models


class SeverityLevel(models.IntegerChoices):
    UNKNOWN = 0, ""
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
