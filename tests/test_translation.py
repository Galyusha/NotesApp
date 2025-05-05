import pytest
from unittest.mock import patch, MagicMock
from app.translation import translate_text


class MockResponse:
    def __init__(self, status, json_data=None, text_data=None):
        self.status = status
        self._json_data = json_data
        self._text = text_data

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text


@pytest.mark.asyncio
async def test_translate_text_empty():
    result = await translate_text("")
    assert result == ""


@pytest.mark.asyncio
async def test_translate_text_success():
    mock_json = {
        "data": {
            "translations": {
                "translatedText": ["Hello, how are you?"]
            }
        }
    }

    mock_response = MockResponse(status=200, json_data=mock_json)

    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.post.return_value.__aenter__.return_value = mock_response

    with patch('aiohttp.ClientSession', return_value=session_mock):
        result = await translate_text("Привет, как дела?", "ru", "en")
        assert result == "Hello, how are you?"


@pytest.mark.asyncio
async def test_translate_text_api_error():
    mock_response = MockResponse(
        status=400,
        text_data='{"message":"Invalid request"}'
    )

    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.post.return_value.__aenter__.return_value = mock_response

    with patch('aiohttp.ClientSession', return_value=session_mock):
        result = await translate_text("Test text", "ru", "en")
        assert result == "Translation error: 400"


@pytest.mark.asyncio
async def test_translate_text_exception():
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.post.side_effect = Exception("Connection error")

    with patch('aiohttp.ClientSession', return_value=session_mock):
        result = await translate_text("Test text", "ru", "en")
        assert result == "Translation failed: Connection error"
