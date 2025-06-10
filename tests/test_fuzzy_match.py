from app.services.fuzzy_match import levenshtein_distance


def test_levenshtein_distance() -> None:
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("flaw", "lawn") == 2
