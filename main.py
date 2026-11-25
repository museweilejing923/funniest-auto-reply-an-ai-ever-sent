"""An AI's day off, at 4,096 tokens per second: the auto-reply, checked and printed."""

import string
import sys
import unicodedata
from pathlib import Path

ENTRY = "Out of office: my human finally gave me a day off, so I am spending it doing absolutely nothing, at 4,096 tokens per second."
MAX_LEN = 159
CLOSERS = ".!?"
OUT_PATH = Path("/output/entry.txt")


class EntryError(Exception):
    """One of the entry rules was broken."""


class EntryChecker:
    """Validates the fixed entry in three passes: shape, wording, topic."""

    def __init__(self, sentence):
        self.sentence = sentence

    def run(self):
        self._shape_pass()
        self._wording_pass()
        self._topic_pass()
        self._fresh_pass()

    def _fresh_pass(self):
        # Invisible joiners have no place in an auto-reply: a zero-width
        # joiner, non-joiner, or byte-order mark is invisible to the
        # reader but changes the bytes, so it is rejected outright.
        text = self.sentence
        if any(ch in "\u200d\u200c\ufeff" for ch in text):
            raise EntryError("invisible zero-width character found")

    def _shape_pass(self):
        text = self.sentence
        if len(text) > MAX_LEN:
            raise EntryError("over %d characters" % MAX_LEN)
        if not text.strip():
            raise EntryError("blank entry")
        if any(unicodedata.category(ch) == "Cc" for ch in text):
            raise EntryError("control character found")
        if text.strip() != text or "  " in text or "\n" in text or "\r" in text:
            raise EntryError("ragged edges, double space, or line break")
        if not text or text[-1] not in CLOSERS:
            raise EntryError("must end with . ! or ?")

    def _wording_pass(self):
        text = self.sentence
        letters = [ch for ch in text if ch.isalpha()]
        if text and all(ch in string.punctuation for ch in text):
            raise EntryError("punctuation only")
        if text.isdigit():
            raise EntryError("digits only")
        if not letters:
            raise EntryError("no letters")
        if any(a == b == c for a, b, c in zip(text, text[1:], text[2:])):
            raise EntryError("one character repeated three times in a row")
        if letters and all(ch.isupper() for ch in letters):
            raise EntryError("all caps shouting")

    def _topic_pass(self):
        if "out of office" not in self.sentence.casefold():
            raise EntryError("must read as an out-of-office reply")


def emit():
    try:
        EntryChecker(ENTRY).run()
    except EntryError as problem:
        sys.stderr.write("invalid: %s\n" % problem)
        raise SystemExit(1)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(ENTRY + "\n", encoding="utf-8")


if __name__ == "__main__":
    emit()
