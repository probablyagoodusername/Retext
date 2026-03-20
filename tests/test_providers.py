import pytest

from rewrite.providers.base import BaseProvider
from rewrite.providers.gemini import GeminiProvider


def test_base_is_abstract():
    with pytest.raises(TypeError):
        BaseProvider()


def test_gemini_provider_init():
    provider = GeminiProvider(api_key="test-key", model="gemini-2.5-flash")
    assert provider.model == "gemini-2.5-flash"
    assert isinstance(provider, BaseProvider)
