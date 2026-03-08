from app.config import Settings


def test_parsed_chat_ids_filters_invalid_values():
    settings = Settings(telegram_chat_ids='1001, abc, , -2002,3.14,3003')

    assert settings.parsed_chat_ids == [1001, -2002, 3003]


def test_parsed_chat_ids_empty_when_not_set():
    settings = Settings(telegram_chat_ids='')

    assert settings.parsed_chat_ids == []
