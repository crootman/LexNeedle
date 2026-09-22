from lexneedle.compat.flashtext import KeywordProcessor


def test_common_flashtext_migration_operations() -> None:
    processor = KeywordProcessor()
    processor.add_keywords_from_dict({"Java": ["java", "j2ee"]})
    processor.add_keywords_from_list(["Python"])

    assert processor.extract_keywords("java and Python") == ["Java", "Python"]
    assert processor.extract_keywords("java", span_info=True) == [("Java", 0, 4)]
    assert processor.replace_keywords("j2ee") == "Java"
    assert processor.get_keyword("java") == "Java"
    assert processor.remove_keyword("java")
    assert processor.extract_keywords("java") == []


def test_compatibility_options_enable_substrings_and_overlaps() -> None:
    processor = KeywordProcessor(boundary="none", strategy="all")
    processor.add_keyword("北京")
    processor.add_keyword("京城")

    assert processor.extract_keywords("我爱北京城") == ["北京", "京城"]


def test_compatibility_option_enables_whitespace_equivalence() -> None:
    processor = KeywordProcessor(boundary="none", whitespace_equivalent=True)
    processor.add_keyword("New York", "NY")

    assert processor.extract_keywords("New\tYork") == ["NY"]
    assert processor.replace_keywords("New\tYork") == "NY"
