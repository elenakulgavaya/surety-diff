import uuid
import datetime

from surety.sdk.dates import Pattern, str_to_date

from surety.diff import compare_rule


def check_is_valid_uuid(uuid_string, version=4):
    try:
        uuid.UUID(uuid_string, version=version)
    except (AttributeError, ValueError, TypeError):
        # If it's either a value error or a type error, then the string
        # is not a valid hex code for a UUID.
        return False

    return True


@compare_rule
def has_some_value(v1, v2):
    return v1 is not None and v2 is not None


@compare_rule()
def has_new_value(v1, v2):
    return (v1 is not None and v2 is not None) and v1 != v2


@compare_rule()
def is_valid_uuid(v1, v2):
    return check_is_valid_uuid(v1) and check_is_valid_uuid(v2)


def get_timestamp_equal_with_delta(seconds):
    @compare_rule(name=f'timestamp_equal_with_delta_{seconds}s')
    def timestamp_equal_with_delta(v1, v2):
        diff = v1.replace(tzinfo=None) - v2.replace(tzinfo=None)
        return abs(diff.total_seconds()) <= seconds

    return timestamp_equal_with_delta


timestamp_equal_with_delta_3s = get_timestamp_equal_with_delta(seconds=3)
timestamp_equal_with_delta_5s = get_timestamp_equal_with_delta(seconds=5)
timestamp_equal_with_delta_10s = get_timestamp_equal_with_delta(seconds=10)


@compare_rule
def sorted_lists_equal(v1, v2):
    return sorted(v1) == sorted(v2)


@compare_rule
def dates_equal_with_delta_3s(v1, v2):
    def to_date(str_date):
        return datetime.datetime.fromisoformat(str_date).replace(tzinfo=None)

    diff = to_date(v1) - to_date(v2)
    return abs(diff.total_seconds()) <= 3


@compare_rule
def equal_with_accuracy_4(v1, v2):
    result = abs(float(v1) - float(v2))
    return result < 0.1 ** 4


def get_fmt_date_with_delta(date_format):
    @compare_rule(name=f'formatted_dates_equal_with_delta:{date_format}')
    def dates_equal_with_delta(v1, v2):
        diff = (str_to_date(v1, pattern=date_format) -
                str_to_date(v2, pattern=date_format))
        return abs(diff.total_seconds()) <= 3

    return dates_equal_with_delta


formatted_dates_equal_with_delta = get_fmt_date_with_delta(
    Pattern.DATETIME_DELIM_T_WITH_ZONE
)
precise_dates_equal_with_delta = get_fmt_date_with_delta(
    Pattern.DATETIME_DELIM_T_WITH_ZONE_PRECISED
)
