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
