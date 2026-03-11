from app.ai.json_response import parse_json_object


def test_parse_json_object_success():
    parsed, error = parse_json_object('{"a": 1, "b": "x"}')

    assert error is None
    assert parsed == {"a": 1, "b": "x"}


def test_parse_json_object_returns_error_on_empty():
    parsed, error = parse_json_object("")

    assert parsed is None
    assert error == "Gemini 빈 응답"


def test_parse_json_object_returns_error_on_invalid_json():
    parsed, error = parse_json_object("{bad")

    assert parsed is None
    assert error is not None
    assert "JSON 파싱 실패" in error


def test_parse_json_object_returns_error_when_not_object():
    parsed, error = parse_json_object("[1,2,3]")

    assert parsed is None
    assert error == "JSON 응답 형식이 올바르지 않습니다."
