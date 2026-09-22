from lexneedle import Matcher


def test_casefolding_handles_sharp_s_and_never_returns_partial_expansion() -> None:
    matcher = Matcher(boundary="none")
    matcher.add("STRASSE")

    [match] = matcher.find("Straße")
    assert (match.text, match.start, match.end) == ("Straße", 0, 6)

    matcher = Matcher(boundary="none")
    matcher.add("s")
    assert matcher.find("ß") == []


def test_length_changing_casefold_does_not_shift_later_matches() -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many(["strasse", "next"])
    text = "Straße next"

    assert [(match.text, match.start, match.end) for match in matcher.find(text)] == [
        ("Straße", 0, 6),
        ("next", 7, 11),
    ]


def test_combining_character_substring_and_overlapping_extraction() -> None:
    matcher = Matcher(boundary="none", unicode_normalization="NFC")
    matcher.add("é")

    assert [
        (match.text, match.start, match.end) for match in matcher.find("e\u0301é", strategy="all")
    ] == [
        ("e\u0301", 0, 2),
        ("é", 2, 3),
    ]


def test_casefolding_handles_greek_cyrillic_arabic_hebrew_and_devanagari() -> None:
    matcher = Matcher()
    matcher.add_many(["ΜΆΙΟΣ", "\u041c\u041e\u0421\u041a\u0412\u0410", "مرحبا", "שלום", "नमस्ते"])

    assert [
        match.text
        for match in matcher.find("μάιος \u041c\u041e\u0421\u041a\u0412\u0410 مرحبا שלום नमस्ते")
    ] == [
        "μάιος",
        "\u041c\u041e\u0421\u041a\u0412\u0410",
        "مرحبا",
        "שלום",
        "नमस्ते",
    ]


def test_cjk_is_word_like_under_default_boundary_policy() -> None:
    matcher = Matcher()
    matcher.add("北京")

    assert matcher.find("我爱北京城") == []
    assert [match.text for match in Matcher(boundary="none").find("我爱北京城")] == []
    substring_matcher = Matcher(boundary="none")
    substring_matcher.add("北京")
    assert [match.text for match in substring_matcher.find("我爱北京城")] == ["北京"]


def test_emoji_and_non_breaking_space_are_safe_boundaries() -> None:
    matcher = Matcher()
    matcher.add("hello")

    assert [match.text for match in matcher.find("👋hello\u00a0hello")] == ["hello", "hello"]


def test_case_sensitive_and_turkic_casefolding_rules_are_explicit() -> None:
    sensitive = Matcher(case_sensitive=True)
    sensitive.add("Panadol")
    assert sensitive.find("panadol") == []

    insensitive = Matcher(boundary="none")
    insensitive.add("I")
    assert [match.text for match in insensitive.find("i")] == ["i"]
    assert insensitive.find("\u0131") == []
    dotted = Matcher(boundary="none")
    dotted.add("İ")
    assert [match.text for match in dotted.find("i\u0307")] == ["i\u0307"]


def test_matches_do_not_split_zwj_sequences() -> None:
    matcher = Matcher(boundary="none")
    matcher.add("👩")
    assert matcher.find("👨\u200d👩") == []
