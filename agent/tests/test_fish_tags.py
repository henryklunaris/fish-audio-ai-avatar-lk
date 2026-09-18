"""Unit tests for the Fish Audio tag validator. No network needed."""

import pytest

from fish_tags import EMOTIONS, SOUNDS, normalize_stream
from fish_tags import normalize_markup as _normalize_markup


def normalize_markup(text: str) -> str:
    return _normalize_markup(text)[0]


def test_documented_labels_pass_through() -> None:
    text = '<expr type="expression" label="delighted"/> Hi! <expr type="sound" label="laughing"/>'
    assert normalize_markup(text) == text


def test_alias_is_rewritten() -> None:
    out = normalize_markup('<expr type="expression" label="joyful"/> Great news.')
    assert 'label="delighted"' in out
    out = normalize_markup('<expr type="sound" label="giggle"/> ha')
    assert 'label="chuckling"' in out


def test_unknown_marker_is_dropped_but_words_kept() -> None:
    out = normalize_markup('<expr type="expression" label="bamboozled"/> Well then.')
    assert "<expr" not in out
    assert "Well then." in out


def test_intensity_prefix_is_stripped() -> None:
    out = normalize_markup('<expr type="expression" label="very excited"/> Yes!')
    assert 'label="excited"' in out


def test_known_tone_wrap_is_kept() -> None:
    text = '<expr type="prosody" label="shouting">get out</expr>'
    assert normalize_markup(text) == text


def test_vocabulary_matches_fish_docs_counts() -> None:
    # 24 basic + 25 advanced + 4 intensity extras, 11 audio effects
    assert len(EMOTIONS) == 53
    assert len(SOUNDS) == 11


@pytest.mark.asyncio
async def test_stream_handles_tag_split_across_chunks() -> None:
    async def chunks():
        for c in ['<expr type="expr', 'ession" label="joy', 'ful"/> Hello ', "there."]:
            yield c

    out = "".join([c async for c in normalize_stream(chunks())])
    assert out == '<expr type="expression" label="delighted"/> Hello there.'


def test_blocked_labels_are_dropped() -> None:
    out = normalize_markup('<expr type="sound" label="groaning"/> Ugh.')
    assert "<expr" not in out and "Ugh." in out
    out = normalize_markup('<expr type="prosody" label="whispering">psst</expr>')
    assert "<expr " not in out and "psst" in out


def test_wrapped_emotion_becomes_self_closing() -> None:
    out = normalize_markup(
        '<expr type="expression" label="ecstatic">Oh my gosh!</expr> Next.'
    )
    assert out == '<expr type="expression" label="ecstatic"/>Oh my gosh! Next.'


def test_wrapped_tone_is_untouched() -> None:
    text = '<expr type="prosody" label="shouting">No way!</expr>'
    assert normalize_markup(text) == text


@pytest.mark.asyncio
async def test_wrap_closer_in_later_chunk_is_dropped() -> None:
    async def chunks():
        for c in ['<expr type="sound" label="laughing">', "ha ha", "</expr> ok"]:
            yield c

    out = "".join([c async for c in normalize_stream(chunks())])
    assert out == '<expr type="sound" label="laughing"/>ha ha ok'


@pytest.mark.asyncio
async def test_trailing_sound_marker_is_dropped() -> None:
    async def chunks():
        for c in ["Oh, whew! I was worried ", '<expr type="sound" label="laughing"/>']:
            yield c

    out = "".join([c async for c in normalize_stream(chunks())])
    assert out == "Oh, whew! I was worried "


@pytest.mark.asyncio
async def test_marker_followed_by_words_in_next_chunk_is_kept() -> None:
    async def chunks():
        for c in ["Okay. ", '<expr type="sound" label="laughing"/>', " Tell me more."]:
            yield c

    out = "".join([c async for c in normalize_stream(chunks())])
    assert out == 'Okay. <expr type="sound" label="laughing"/> Tell me more.'
