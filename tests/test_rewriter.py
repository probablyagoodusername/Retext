import pytest

from rewrite.providers.gemini import GeminiProvider
from rewrite.rewriter import SYSTEM_PROMPT, clean_response, get_provider


class TestCleanResponse:
    def test_strips_whitespace(self):
        assert clean_response("  hello  ") == "hello"

    def test_removes_markdown_code_block(self):
        text = '```\nHello world\n```'
        assert clean_response(text) == "Hello world"

    def test_removes_markdown_code_block_with_language(self):
        text = '```text\nHello world\n```'
        assert clean_response(text) == "Hello world"

    def test_removes_surrounding_double_quotes(self):
        assert clean_response('"Hello world"') == "Hello world"

    def test_removes_surrounding_single_quotes(self):
        assert clean_response("'Hello world'") == "Hello world"

    def test_removes_curly_quotes(self):
        assert clean_response('\u201cHello world\u201d') == "Hello world"

    def test_preserves_internal_quotes(self):
        result = clean_response('She said "hello" to me')
        assert result == 'She said "hello" to me'

    def test_empty_string(self):
        assert clean_response("") == ""

    def test_already_clean(self):
        assert clean_response("Hello world") == "Hello world"

    def test_multiline_preserved(self):
        text = "Line one\nLine two\nLine three"
        assert clean_response(text) == text


class TestGetProvider:
    def test_gemini_provider(self):
        config = {
            "gemini_api_key": "test-key",
            "gemini_model": "gemini-2.5-flash",
        }
        provider = get_provider(config)
        assert isinstance(provider, GeminiProvider)

    def test_gemini_missing_key_raises(self):
        config = {"gemini_api_key": ""}
        with pytest.raises(ValueError, match="Gemini API key"):
            get_provider(config)

    def test_system_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT) > 50
