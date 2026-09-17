"""Fish Audio S2.1 tag vocabulary and a stream filter that keeps LLM markup inside it.

Source: https://docs.fish.audio/developer-guide/core-features/emotions
LiveKit's expressive mode has the LLM emit <expr type="..." label="..."/> markers and
converts them to Fish's [bracket] form inside the TTS. This module sits in between
(Agent.tts_node) and rewrites any label Fish does not document to the closest one it does.
"""

import re
from collections.abc import AsyncIterable

BASIC_EMOTIONS = [
    "happy", "sad", "angry", "excited", "calm", "nervous", "confident", "surprised",
    "satisfied", "delighted", "scared", "worried", "upset", "frustrated", "depressed",
    "empathetic", "embarrassed", "disgusted", "moved", "proud", "relaxed", "grateful",
    "curious", "sarcastic",
]  # fmt: skip
ADVANCED_EMOTIONS = [
    "disdainful", "unhappy", "anxious", "hysterical", "indifferent", "uncertain",
    "doubtful", "confused", "disappointed", "regretful", "guilty", "ashamed", "jealous",
    "envious", "hopeful", "optimistic", "pessimistic", "nostalgic", "lonely", "bored",
    "contemptuous", "sympathetic", "compassionate", "determined", "resigned",
]  # fmt: skip
# Extra levels from the intensity scale table
INTENSITY_EMOTIONS = ["furious", "terrified", "interested", "ecstatic"]
EMOTIONS = set(BASIC_EMOTIONS + ADVANCED_EMOTIONS + INTENSITY_EMOTIONS)

# These are a work in progress still for Fish

BLOCKED = {"groaning", "whispering"}
# Labels LiveKit's own expressive prompt already teaches the LLM
LIVEKIT_EMOTIONS = {
    "regretful", "hopeful", "happy", "excited", "curious", "surprised", "sad",
    "empathetic", "sarcastic", "calm", "angry", "worried", "nervous", "confident",
    "grateful", "delighted", "disappointed", "frustrated", "determined",
}  # fmt: skip
# Documented Fish emotions LiveKit does not mention, offered to the LLM as extras
EXTRA_EMOTIONS = EMOTIONS - LIVEKIT_EMOTIONS

SOUNDS = {
    "laughing", "chuckling", "sobbing", "crying loudly", "sighing", "groaning",
    "panting", "gasping", "yawning", "snoring", "clear throat",
}  # fmt: skip
# LiveKit's tone labels (it converts these itself), plus Fish's native names
TONES = {
    "whispering",
    "soft",
    "shouting",
    "hurried",
    "in a hurry tone",
    "soft tone",
    "screaming",
    "emphasis",
}

# How these works is that, if the LLM generates for example "shy" instead of "embarrased" it will map it to "embarrased" instead because thats the only tag that is documented in Fish audio as of Sep 2026
EMOTION_ALIASES = {
    "joyful": "delighted",
    "cheerful": "happy",
    "amused": "delighted",
    "playful": "excited",
    "thrilled": "ecstatic",
    "enthusiastic": "excited",
    "warm": "compassionate",
    "gentle": "calm",
    "tender": "moved",
    "affectionate": "moved",
    "loving": "moved",
    "flirty": "excited",
    "shy": "embarrassed",
    "sheepish": "embarrassed",
    "concerned": "worried",
    "afraid": "scared",
    "fearful": "scared",
    "panicked": "hysterical",
    "mad": "angry",
    "annoyed": "frustrated",
    "irritated": "frustrated",
    "grumpy": "unhappy",
    "melancholic": "sad",
    "heartbroken": "depressed",
    "sorry": "regretful",
    "apologetic": "regretful",
    "reassuring": "compassionate",
    "encouraging": "hopeful",
    "inspired": "optimistic",
    "intrigued": "curious",
    "puzzled": "confused",
    "skeptical": "doubtful",
    "wry": "sarcastic",
    "dry": "sarcastic",
    "mysterious": "curious",
    "serious": "determined",
    "focused": "determined",
    "neutral": "calm",
    "content": "satisfied",
    "peaceful": "relaxed",
    "sleepy": "bored",
    "tired": "resigned",
    "shocked": "surprised",
    "amazed": "surprised",
    "astonished": "surprised",
}
SOUND_ALIASES = {
    "laugh": "laughing",
    "giggle": "chuckling",
    "giggling": "chuckling",
    "chuckle": "chuckling",
    "snicker": "chuckling",
    "sigh": "sighing",
    "gasp": "gasping",
    "groan": "groaning",
    "moan": "groaning",
    "yawn": "yawning",
    "sob": "sobbing",
    "cry": "sobbing",
    "crying": "sobbing",
    "weeping": "sobbing",
    "wail": "crying loudly",
    "cough": "clear throat",
    "coughing": "clear throat",
    "ahem": "clear throat",
    "breath": "panting",
    "breathing": "panting",
    "exhale": "sighing",
    "snore": "snoring",
}

_EXPR_RE = re.compile(r"<expr\s+([^<>]*?)\s*(/?)>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')


def _clean(label: str) -> str:
    # strip intensity words, LiveKit adds "very" itself later
    label = label.strip().lower()
    for prefix in ("very ", "extremely ", "slightly ", "a little ", "a bit ", "quite "):
        if label.startswith(prefix):
            label = label[len(prefix) :]
    return label.strip()


def resolve_label(marker_type: str, label: str) -> str | None:
    """Return a documented Fish label for this marker, or None to drop the marker."""
    label = _clean(label)
    if label in BLOCKED:
        return None
    if marker_type == "expression":
        if label in EMOTIONS:
            return label
        return EMOTION_ALIASES.get(label)
    if marker_type == "sound":
        if label in SOUNDS:
            return label
        return SOUND_ALIASES.get(label)
    if marker_type == "prosody":
        return label if label in TONES else None
    if marker_type == "break":
        return label  # durations are validated by LiveKit
    return None


def normalize_markup(text: str) -> str:
    """Rewrite every complete <expr .../> in text so its label is one Fish documents."""

    def fix(m: re.Match[str]) -> str:
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        marker_type = attrs.get("type", "").lower()
        label = attrs.get("label", "")
        new_label = resolve_label(marker_type, label)
        if new_label is None:
            # drop the tag, keep the words (LiveKit strips any orphaned </expr>)
            return ""
        if new_label == label.strip().lower():
            return m.group(0)
        attrs["label"] = new_label
        rendered = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        return f"<expr {rendered}{m.group(2)}>"

    return _EXPR_RE.sub(fix, text)


async def normalize_stream(text: AsyncIterable[str]) -> AsyncIterable[str]:
    """Stream-safe wrapper: holds back a partial "<expr" at the end of a chunk."""
    buf = ""
    async for chunk in text:
        buf += chunk
        cut = buf.rfind("<")
        if cut != -1 and ">" not in buf[cut:]:
            ready, buf = buf[:cut], buf[cut:]
        else:
            ready, buf = buf, ""
        if ready:
            yield normalize_markup(ready)
    if buf:
        yield normalize_markup(buf)
