import re

import pytest

from surety.diff import compare
from surety.diff.rules import has_some_value, sorted_lists_equal


def test_compare_matching():
    compare(expected={'test': 1}, actual={'test': 1})


def test_compare_with_rules():
    compare(
        expected={'value': 1},
        actual={'value': 2},
        rules={'value': has_some_value}
    )


def test_compare_forbid_unapplied_rules_false():
    compare(
        expected={'test': 1},
        actual={'test': 1},
        rules={'no_key': has_some_value},
        forbid_unapplied_rules=False
    )


def test_compare_custom_target_name():
    expected_exception = re.escape('Unexpected response received')
    with pytest.raises(AssertionError, match=expected_exception):
        compare(
            expected={'test': 1},
            actual={'test': 2},
            target_name='response'
        )


def test_compare_nested_structures_with_rules():
    compare(
        expected={'items': [1, 2, 3]},
        actual={'items': [3, 2, 1]},
        rules={'items': sorted_lists_equal}
    )


def test_compare_complex_nested_with_multiple_rules():
    compare(
        expected={'name': 'test', 'items': [1, 2, 3]},
        actual={'name': 'test', 'items': [3, 2, 1]},
        rules={
            'name': has_some_value,
            'items': sorted_lists_equal
        }
    )


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
