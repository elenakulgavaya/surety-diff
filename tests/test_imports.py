def test_compare_import():
    from surety.diff import compare
    assert callable(compare)


def test_compare_rule_import():
    from surety.diff import compare_rule
    assert callable(compare_rule)

