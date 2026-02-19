from io import StringIO

from pprint import pprint

from surety.diff.diff import Diff


def compare(actual, expected, rules=None, forbid_unapplied_rules=True,
            target_name='data'):
    deep_diff = Diff(expected, actual, rules=rules,
                     forbid_unapplied_rules=forbid_unapplied_rules)
    printed_deep_diff = StringIO()
    pprint(deep_diff, indent=2, stream=printed_deep_diff)

    assert not deep_diff, (
        f'\nUnexpected {target_name} received'
        f'\n\tActual: {actual}'
        f'\n\tExpected: {expected},'
        f'\n\tDiff: \n{printed_deep_diff.getvalue()}'
    )
