from pathlib import Path

from dpdp_analyzer.rules import load_rules

RULES_PATH = Path(__file__).parent.parent / "rules" / "dpdp_v1.yaml"


def test_rule_pack_parses():
    rules = load_rules(RULES_PATH)
    assert len(rules) == 20


def test_every_rule_has_a_section_ref():
    rules = load_rules(RULES_PATH)
    assert all(r.section_ref.strip() for r in rules)


def test_all_five_categories_covered():
    rules = load_rules(RULES_PATH)
    categories = {r.category for r in rules}
    assert categories == {"consent", "notice", "rights", "breach", "sdf"}


def test_rule_ids_are_unique():
    rules = load_rules(RULES_PATH)
    ids = [r.id for r in rules]
    assert len(ids) == len(set(ids))
