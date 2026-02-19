import re

import pytest

from surety.diff import compare


def test_compare_matching():
    compare(expected={'test': 1}, actual={'test': 1})


def test_compare_not_matching():
    expected_exception = re.escape(
        "\nUnexpected data received\n\t"
        "Actual: {'test': 2}\n\t"
        "Expected: {'test': 1},\n\t"
        "Diff: \n{\'value_changed\': "
        "{\'root[test]\': {\'actual value\': 2, \'expected value\': 1}}}\n"
    )
    with pytest.raises(AssertionError, match=expected_exception):
        compare(expected={'test': 1}, actual={'test': 2})
