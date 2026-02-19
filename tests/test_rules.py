from datetime import datetime, timedelta, timezone

import pytest

from surety.sdk.fakeable import Fakeable, fake_string_attr

from surety.diff.compare import compare
from surety.diff.rules import (
    has_some_value,
    has_new_value,
    is_valid_uuid,
    get_timestamp_equal_with_delta,
    timestamp_equal_with_delta_3s,
    timestamp_equal_with_delta_5s,
    timestamp_equal_with_delta_10s,
    sorted_lists_equal,
    dates_equal_with_delta_3s,
    equal_with_accuracy_4,
    get_fmt_date_with_delta,
    formatted_dates_equal_with_delta,
    precise_dates_equal_with_delta,
    check_is_valid_uuid,
)


def test_check_is_valid_uuid4():
    assert check_is_valid_uuid('550e8400-e29b-41d4-a716-446655440000')


@pytest.mark.parametrize('value', argvalues=[
    'not-a-uuid', None, 123454, ''
], ids=['string', 'none', 'integer', 'empty'])
def test_check_uuid_false_for(value):
    assert check_is_valid_uuid(value) is False



def test_has_some_value():
    assert has_some_value('a', 'b')


def test_has_some_value_not_none():
    assert has_some_value(0, '')


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    (None, 'b'), ('a', None), (None, None)
], ids=['v1_is_none', 'v2_is_none', 'both_are_none'])
def test_has_some_value_when(v1, v2):
    assert has_some_value(v1, v2) is False


def test_has_some_value_repr():
    assert repr(has_some_value) == 'has_some_value'


def test_has_new_value():
    assert has_new_value('old', 'new')


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    ('same', 'same'), (None, 'a'), ('a', None), (None, None)
], ids=['same', 'first_none', 'second_none', 'both_none'])
def test_has_new_value_when(v1, v2):
    assert has_new_value(v1, v2) is False


def test_has_new_value_repr():
    assert repr(has_new_value) == 'has_new_value'



VALID_UUID = '550e8400-e29b-41d4-a716-446655440000'
ANOTHER_UUID = '6ba7b810-9dad-11d1-80b4-00c04fd430c8'

def test_both_valid():
    assert is_valid_uuid(VALID_UUID, ANOTHER_UUID)


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    ('bad_uuid', VALID_UUID), (VALID_UUID, 'bad_uuid'), ('first', 'second')
], ids=['first_not_valid', 'second_not_valid', 'both_not_valid'])
def test_uuid_not_valid(v1, v2):
    assert is_valid_uuid(v1, v2) is False


def test_is_valid_uuid_repr():
    assert repr(is_valid_uuid) == 'is_valid_uuid'


def _dt(offset_seconds=0):
    """Return a timezone-aware datetime offset by N seconds from a fixed base."""
    base = datetime(2024, 1, 1, 12, 0, 0,
                    tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


def test_3s_within_delta():
    assert timestamp_equal_with_delta_3s(_dt(0), _dt(2))


def test_3s_exactly_on_boundary():
    assert timestamp_equal_with_delta_3s(_dt(0), _dt(3))


def test_3s_exceeds_delta():
    assert timestamp_equal_with_delta_3s(_dt(0), _dt(4)) is False


def test_5s_within_delta():
    assert timestamp_equal_with_delta_5s(_dt(0), _dt(5))


def test_5s_exceeds_delta():
    assert timestamp_equal_with_delta_5s(_dt(0), _dt(6)) is False


def test_10s_within_delta():
    assert timestamp_equal_with_delta_10s(_dt(0), _dt(10))


def test_10s_exceeds_delta():
    assert timestamp_equal_with_delta_10s(_dt(0), _dt(11)) is False


def test_negative_diff_still_valid():
    assert timestamp_equal_with_delta_3s(_dt(2), _dt(0))


def test_custom_delta_repr():
    custom = get_timestamp_equal_with_delta(seconds=7)
    assert repr(custom) == 'timestamp_equal_with_delta_7s'


def test_3s_repr():
    assert repr(timestamp_equal_with_delta_3s) == 'timestamp_equal_with_delta_3s'


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    ([1, 2, 3], [1, 2, 3]),
    ([1, 2, 3], [3, 1, 2]),
    ([], []),
    (['a', 'b'], ['b', 'a'])
], ids=['same_order', 'different_order', 'empty_lists', 'strings'])
def test_sorted_list(v1, v2):
    assert sorted_lists_equal(v1, v2)


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    ([1, 2, 3], [1, 2, 4]), ([1, 2], [1, 2, 3]),
], ids=['different_values', 'different_len'])
def test_sorted_list_not_equal(v1, v2):
    assert sorted_lists_equal(v1, v2) is False


def test_sorted_lists_equal_repr():
    assert repr(sorted_lists_equal) == 'sorted_lists_equal'


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    ('2024-01-01T12:00:00', '2024-01-01T12:00:02'),
    ('2024-01-01T12:00:00', '2024-01-01T12:00:03'),
    ('2024-01-01T12:00:00', '2024-01-01T12:00:00'),
], ids=['within_delta', 'boundary', 'same'])
def test_dates_equal_with_delta_3s(v1, v2):
    assert dates_equal_with_delta_3s(v1, v2)


def test_exceeds_delta():
    assert dates_equal_with_delta_3s(
        '2024-01-01T12:00:00',
        '2024-01-01T12:00:04'
    ) is False


def test_dates_equal_with_delta_3s_repr():
    assert repr(dates_equal_with_delta_3s) == 'dates_equal_with_delta_3s'


@pytest.mark.parametrize(argnames=['v1', 'v2'], argvalues=[
    ('1.0', '1.0'), ('1.00000', '1.00009'), (5, 5), ('1.0', '1.0001')
],ids=['same', 'within_tolerance', 'integers', 'boundary'])
def test_equal_with_accuracy_4(v1, v2):
    assert equal_with_accuracy_4(v1, v2)


def test_not_equal_with_accuracy_4():
    assert equal_with_accuracy_4('1.0', '1.001') is False


def test_repr():
    assert repr(equal_with_accuracy_4) == 'equal_with_accuracy_4'


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
