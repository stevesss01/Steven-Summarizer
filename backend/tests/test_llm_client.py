"""Retry, key-rotation and model-fallback behaviour of the LLM client."""

import asyncio
from types import SimpleNamespace

import pytest

from app.core import config
from app.services import llm_client as mod


class StatusError(Exception):
    def __init__(self, status, msg="error"):
        super().__init__(msg)
        self.status_code = status
        self.response = SimpleNamespace(headers={"retry-after": "0"})


def make_client(script, keys=("k1", "k2")):
    """script: list of exceptions or strings returned in order across calls."""
    used = []
    client = mod.LLMClient(list(keys))
    queue = list(script)

    for i, c in enumerate(client._clients):

        async def create(_i=i, **params):
            used.append((_i, params["model"]))
            item = queue.pop(0)
            if isinstance(item, Exception):
                raise item
            msg = SimpleNamespace(content=item)
            return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

        c.chat = SimpleNamespace(completions=SimpleNamespace(create=create))
    return client, used


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr(mod.asyncio, "sleep", no_sleep)


def test_rotates_keys_and_retries_rate_limit():
    client, used = make_client([StatusError(429), "ok"])
    result = asyncio.run(client.complete([{"role": "user", "content": "hi"}]))
    assert result.text == "ok"
    assert used[0][0] != used[1][0]  # second attempt used the other key


def test_falls_back_to_next_model_after_retries():
    retries = config.settings.max_retries
    client, used = make_client([StatusError(503)] * retries + ["fallback ok"])
    result = asyncio.run(client.complete([{"role": "user", "content": "hi"}]))
    assert result.text == "fallback ok"
    assert result.model == config.settings.models[1]


def test_context_error_is_raised_immediately():
    client, _ = make_client([StatusError(413, "context length exceeded")])
    with pytest.raises(mod.ContextTooLongError):
        asyncio.run(client.complete([{"role": "user", "content": "hi"}]))


def test_gives_clean_error_when_everything_fails():
    total = config.settings.max_retries * len(config.settings.models)
    client, _ = make_client([StatusError(500)] * total)
    with pytest.raises(mod.LLMServiceError):
        asyncio.run(client.complete([{"role": "user", "content": "hi"}]))


def test_missing_key_is_reported():
    with pytest.raises(mod.LLMServiceError):
        mod.LLMClient([])
