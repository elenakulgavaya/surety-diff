def test_compare_import():
    from surety.diff import compare #pylint: disable=import-outside-toplevel
    assert callable(compare)


def test_compare_rule_import():
    from surety.diff import compare_rule #pylint: disable=import-outside-toplevel
    assert callable(compare_rule)
