import datetime
import difflib

from collections.abc import Iterable, MutableMapping
from decimal import Decimal
from itertools import zip_longest

from surety.process.common import is_callable_with_strict_args


strings = (str, bytes)
numbers = (int, float, complex, datetime.datetime, datetime.date, Decimal)


class Default:
    """Class of conditions to be checked"""


class DiffType:
    TypeChanged = 'type_changed'
    DictItemAdded = 'dict_item_added'
    DictItemRemoved = 'dict_item_removed'
    ValueChanged = 'value_changed'
    IterableItemAdded = 'iterable_item_added'
    IterableItemRemoved = 'iterable_item_removed'
    RulesViolated = 'rules_violated'
    RulesUnapplied = 'rules_unapplied'
    Unprocessed = 'unprocessed'


class Diff(dict):
    """
    Importing
        >>> from pprint import pprint

    Same object returns empty
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = t1
        >>> print(Diff(t1, t2))
        {}

    Item type has has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:"2", 3:3}
        >>> pprint(Diff(t1, t2), indent=2)
        { 'type_changed': { 'root[2]': { 'actual type': <class 'str'>,
                                         'actual value': '2',
                                         'expected type': <class 'int'>,
                                         'expected value': 2}}}

    Value of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:4, 3:3}
        >>> pprint(Diff(t1, t2), indent=2)
        {'value_changed': {'root[2]': {'actual value': 4, 'expected value': 2}}}

    Item added and/or removed
        >>> t1 = {1:1, 2:2, 3:3, 4:4}
        >>> t2 = {1:1, 2:4, 3:3, 5:5, 6:6}
        >>> ddiff = Diff(t1, t2)
        >>> pprint (ddiff)
        {'dict_item_added': ['root[5]', 'root[6]'],
         'dict_item_removed': ['root[4]'],
         'value_changed': {'root[2]': {'actual value': 4, 'expected value': 2}}}

    String difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
        >>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
        >>> ddiff = Diff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'value_changed': { 'root[2]': {'actual value': 4, 'expected value': 2},
                             'root[4][b]': { 'actual value': 'world!',
                                             'expected value': 'world'}}}

    List difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
        >>> ddiff = Diff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {'iterable_item_removed': {'root[4][b][2]': 3, 'root[4][b][3]': 4}}

    List difference 2:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
        >>> ddiff = Diff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {'iterable_item_added': {'root[4][b][3]': 4}}

    List that contains dictionary:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
        >>> ddiff = Diff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'dict_item_removed': ['root[4][b][2][2]'],
          'value_changed': { 'root[4][b][2][1]': { 'actual value': 3,
                                                   'expected value': 1}}}


    Dictionary extended:
        >>> t1 = {1:1, 2:2}
        >>> t2 = {1:1, 2:2, 3:3}
        >>> ddiff = Diff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {'dict_item_added': ['root[3]']}
    """

    def __init__(self, expected, actual, rules=None,
                 forbid_unapplied_rules=True):
        super().__init__()
        self.forbid_unapplied_rules = forbid_unapplied_rules
        self.update({
            DiffType.TypeChanged: {},
            DiffType.DictItemAdded: [],
            DiffType.DictItemRemoved: [],
            DiffType.ValueChanged: {},
            DiffType.IterableItemAdded: {},
            DiffType.IterableItemRemoved: {},
            DiffType.RulesViolated: {},
            DiffType.RulesUnapplied: {},
            DiffType.Unprocessed: []
        })

        self.__diff(expected, actual, parents_ids=frozenset({id(expected)}),
                    rules=rules)
        empty_keys = [k for k, v in getattr(self, 'items')() if not v]

        for k in empty_keys:
            del self[k]

    def __diff_dict(self, expected, actual, parent, parents_ids=frozenset({}),
                    rules=None):
        rules = rules or {}
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())

        keys_intersect = actual_keys.intersection(expected_keys)

        keys_added = actual_keys - keys_intersect
        keys_removed = expected_keys - keys_intersect

        if self.forbid_unapplied_rules:
            for key, rule in rules.items():
                if key not in expected_keys and key not in actual_keys:
                    self[DiffType.RulesUnapplied][
                        f"{parent}['{key}']"
                    ] = str(rule)

        if keys_added:
            self[DiffType.DictItemAdded].extend(
                [f'{parent}[{key}]' for key in keys_added]
            )

        if keys_removed:
            self[DiffType.DictItemRemoved].extend(
                [f'{parent}[{key}]' for key in keys_removed]
            )

        self.__diff_common_children(
            expected, actual, keys_intersect, parents_ids, parent, rules=rules
        )

    def __diff_common_children(self, expected, actual, keys_intersect,
                               parents_ids, parent, rules=None):
        for item_key in keys_intersect:
            expected_child = expected[item_key]
            actual_child = actual[item_key]
            rules_child = rules.get(item_key)
            item_id = id(expected_child)

            parents_added = set(parents_ids)
            parents_added.add(item_id)
            parents_added = frozenset(parents_added)

            self.__diff(expected_child, actual_child, rules=rules_child,
                        parent=f'{parent}[{item_key}]',
                        parents_ids=parents_added)

    def __diff_iterable(self, expected, actual, parent='root',
                        parents_ids=frozenset({}), rules=None):
        rules = rules or [None]

        for i, (expected_item, actual_item) in enumerate(zip_longest(
                expected, actual, fillvalue=Default)):
            key = f'{parent}[{i}]'

            if actual_item is Default:
                self[DiffType.IterableItemRemoved][key] = expected_item
            elif expected_item is Default:
                self[DiffType.IterableItemAdded][key] = actual_item
            else:
                self.__diff(expected_item, actual_item, key, parents_ids,
                            rules=rules[0])

    def __diff_str(self, expected, actual, parent):
        if '\n' in expected or '\n' in actual:
            diff = list(difflib.unified_diff(
                expected.splitlines(), actual.splitlines(), lineterm=''
            ))

            if diff:
                self[DiffType.ValueChanged][parent] = {
                    'expected value': expected,
                    'actual value': actual,
                    'found diff': '\n'.join(diff)
                }
        elif expected != actual:
            self[DiffType.ValueChanged][parent] = {
                'expected value': expected,
                'actual value': actual
            }

    def __diff(self, expected, actual, parent='root',
               parents_ids=frozenset({}), rules=None):
        if is_callable_with_strict_args(rules, args_count=2):
            if not rules(expected, actual):
                self[DiffType.RulesViolated][parent] = {
                    'rule': str(rules),
                    'expected value': expected,
                    'actual value': actual
                }
        elif expected is actual:
            if rules is not None:
                self[DiffType.RulesUnapplied][parent] = str(rules)

            return
        elif not isinstance(expected, type(actual)):
            self[DiffType.TypeChanged][parent] = {
                'expected value': expected,
                'actual value': actual,
                'expected type': type(expected),
                'actual type': type(actual)
            }
        elif isinstance(expected, strings):
            if rules is not None:
                self[DiffType.RulesUnapplied][parent] = str(rules)
            else:
                self.__diff_str(expected, actual, parent)
        elif isinstance(expected, numbers):
            if rules is not None:
                self[DiffType.RulesUnapplied][parent] = str(rules)
            elif expected != actual:
                self[DiffType.ValueChanged][parent] = {
                    'expected value': expected,
                    'actual value': actual
                }
        elif isinstance(expected, MutableMapping):
            self.__diff_dict(
                expected, actual, parent, parents_ids, rules=rules
            )
        elif isinstance(expected, Iterable):
            self.__diff_iterable(
                expected, actual, parent, parents_ids, rules=rules
            )
        else:
            self[DiffType.Unprocessed].append(
                f'{parent}: {expected} and {actual}'
            )

        return
