from datetime import datetime, timedelta

import pytest

from surety.sdk.fakeable import Fakeable, fake_string_attr

from surety.diff import compare
from surety.diff.rules import (
    dates_equal_with_delta_3s, equal_with_accuracy_4,
    formatted_dates_equal_with_delta, has_new_value, has_some_value,
    is_valid_uuid, sorted_lists_equal, timestamp_equal_with_delta_5s
)


def test_compare_with_rule():
    compare(
        expected={'test': fake_string_attr(Fakeable.Uuid)},
        actual={'test': fake_string_attr(Fakeable.Uuid)},
        rules={'test': is_valid_uuid}
    )


def test_compare_with_rule_failed():
    with pytest.raises(AssertionError, match='is_valid_uuid'):
        compare(
            expected={'test': 1},
            actual={'test': 2},
            rules={'test': is_valid_uuid}
        )


def test_rule_has_some_value():
    with pytest.raises(AssertionError, match='has_some_value'):
        compare(
            expected={'test': 1},
            actual={'test': None},
            rules={'test': has_some_value}
        )


def test_rule_has_new_value():
    with pytest.raises(AssertionError, match='has_new_value'):
        compare(
            expected={'test': 1},
            actual={'test': 1},
            rules={'test': has_new_value}
        )


def test_rule_timestamp_equal_with_delta():
    with pytest.raises(AssertionError, match='timestamp_equal_with_delta_5s'):
        compare(
            expected={'test': datetime.utcnow()},
            actual={'test': datetime.utcnow() + timedelta(seconds=6)},
            rules={'test': timestamp_equal_with_delta_5s}
        )


def test_rule_sorted_list_equal():
    compare(
        expected={'test': [1, 2, 3]},
        actual={'test': [3, 1, 2]},
        rules={'test': sorted_lists_equal}
    )


def test_rule_dates_equal_with_delta():
    with pytest.raises(AssertionError, match='dates_equal_with_delta_3s'):
        compare(
            expected={'test': datetime.utcnow().isoformat()},
            actual={'test': (
                    datetime.utcnow() + timedelta(seconds=4)
            ).isoformat()},
            rules={'test': dates_equal_with_delta_3s}
        )


def test_rule_equal_with_accuracy():
    compare(
        expected={'test': 1.0212435},
        actual={'test': 1.021298},
        rules={'test': equal_with_accuracy_4}
    )


def test_rule_formatted_dates_equal_with_delta():
    with pytest.raises(AssertionError, match='formatted_dates_equal_with_delta'):
        compare(
            expected={'test': '2021-10-22T01:01:45Z'},
            actual={'test': '2021-10-22T01:01:41Z'},
            rules={'test': formatted_dates_equal_with_delta}
        )


def test_rule_not_applied():
    with pytest.raises(AssertionError, match='rules_unapplied'):
        compare(
            expected={'test': 1},
            actual={'test': 1},
            rules={'missing': has_some_value}
        )


def test_compare_free_text():
    free_text = '\n'.join([
        fake_string_attr(Fakeable.Sentence) for _ in range(4)
    ])
    compare(
        expected={'test': free_text},
        actual={'test': free_text}
    )


def test_compare_free_text_mismatch():
    free_text = '\n'.join([
        fake_string_attr(Fakeable.Sentence) for _ in range(4)
    ])
    another_text = '\n'.join([
        fake_string_attr(Fakeable.Sentence) for _ in range(3)
    ])

    with pytest.raises(AssertionError, match='value_changed'):
        compare(
            expected={'test': free_text},
            actual={'test': another_text}
        )


def test_compare_rules_unapplied_structure_mismatch():
    with pytest.raises(AssertionError, match='rules_unapplied'):
        compare(
            expected='test1',
            actual='test1',
            rules={'test': has_new_value}
        )


def test_rules_unapplied_structure_mismatch_and_value_changed():
    with pytest.raises(AssertionError, match='rules_unapplied'):
        compare(
            expected='test1',
            actual='test2',
            rules={'test': has_new_value}
        )


def test_rules_unapplied_numbers():
    with pytest.raises(AssertionError, match='rules_unapplied'):
        compare(
            expected=23,
            actual=51,
            rules={'test': has_new_value}
        )


def test_unprocessed_objects():
    class Item:
        """ class for checking comparasing """

    with pytest.raises(AssertionError, match='test_unprocessed_objects'):
        compare(
            expected=Item(),
            actual=Item(),
        )
