#!/usr/bin/env python3
"""Solve NYT-style Spelling Bee puzzles.

Given seven letters (one of which is the required "key" letter), find every
valid word of at least four letters that:
  - uses only the seven available letters (letters may repeat),
  - contains the key letter at least once.

Words that use all seven letters are "pangrams" and are scored with a bonus,
matching the real game's scoring rules.

Usage:
    python3 solver.py ABCDEFG D
    python3 solver.py --letters abcdefg --key d
    python3 solver.py abcdefg d --wordlist /path/to/custom_words.txt
    echo "abcdefg d" | python3 solver.py

By default the solver loads data/words.txt, a bundled ~172k word dictionary
(the ENABLE1 word-game word list, which excludes proper nouns and
abbreviations) plus a curated set of modern words such as "wifi", "selfie",
"podcast", and "meme" that many standard dictionaries omit. Pass --wordlist
to use a different word list file (one word per line), or --download to
fetch a fresh copy of the base dictionary from GitHub if no local word list
can be found.
"""

from __future__ import annotations

import argparse
import string
import sys
import urllib.request
from pathlib import Path

DEFAULT_WORDLIST = Path(__file__).parent / "data" / "words.txt"
FALLBACK_DOWNLOAD_URL = (
    "https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt"
)
MIN_WORD_LENGTH = 4
PANGRAM_BONUS = 7


class PuzzleError(ValueError):
    """Raised for invalid puzzle input (letters/key)."""


def parse_letters(letters: str, key: str) -> tuple[set[str], str]:
    letters = letters.strip().lower()
    key = key.strip().lower()

    if len(letters) != 7:
        raise PuzzleError(f"Expected exactly 7 letters, got {len(letters)}: {letters!r}")
    if not all(c in string.ascii_lowercase for c in letters):
        raise PuzzleError(f"Letters must be alphabetic: {letters!r}")
    if len(set(letters)) != 7:
        raise PuzzleError(f"The 7 letters must be unique: {letters!r}")
    if len(key) != 1 or key not in string.ascii_lowercase:
        raise PuzzleError(f"Key letter must be a single letter: {key!r}")
    if key not in letters:
        raise PuzzleError(f"Key letter {key!r} must be one of the 7 letters {letters!r}")

    return set(letters), key


def load_wordlist(path: Path) -> list[str]:
    with path.open(encoding="utf-8", errors="ignore") as f:
        return [line.strip().lower() for line in f if line.strip()]


def download_wordlist(dest: Path) -> list[str]:
    print(f"Downloading base dictionary from {FALLBACK_DOWNLOAD_URL} ...", file=sys.stderr)
    with urllib.request.urlopen(FALLBACK_DOWNLOAD_URL, timeout=30) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    words = [w.strip().lower() for w in data.splitlines() if w.strip()]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(sorted(set(words))) + "\n", encoding="utf-8")
    return words


def resolve_wordlist(wordlist_arg: str | None, allow_download: bool) -> list[str]:
    candidates = []
    if wordlist_arg:
        candidates.append(Path(wordlist_arg))
    candidates.append(DEFAULT_WORDLIST)
    candidates.append(Path("/usr/share/dict/words"))
    candidates.append(Path("/usr/share/dict/american-english"))

    for path in candidates:
        if path.is_file():
            words = load_wordlist(path)
            if words:
                return words

    if allow_download:
        return download_wordlist(DEFAULT_WORDLIST)

    raise FileNotFoundError(
        "No word list found. Provide one with --wordlist, restore "
        f"{DEFAULT_WORDLIST}, or pass --download to fetch one."
    )


def find_words(
    words: list[str],
    allowed_letters: set[str],
    key_letter: str,
    min_length: int = MIN_WORD_LENGTH,
) -> list[str]:
    found = []
    for word in words:
        if len(word) < min_length:
            continue
        if key_letter not in word:
            continue
        if not set(word) <= allowed_letters:
            continue
        found.append(word)
    return sorted(set(found), key=lambda w: (len(w), w))


def is_pangram(word: str, allowed_letters: set[str]) -> bool:
    return set(word) == allowed_letters


def score_word(word: str, allowed_letters: set[str]) -> int:
    points = 1 if len(word) == MIN_WORD_LENGTH else len(word)
    if is_pangram(word, allowed_letters):
        points += PANGRAM_BONUS
    return points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("letters", nargs="?", help="The 7 available letters, e.g. ABCDEFG")
    parser.add_argument("key", nargs="?", help="The required key/center letter, e.g. D")
    parser.add_argument("--letters", dest="letters_opt", help="The 7 available letters (alternative to positional arg)")
    parser.add_argument("--key", dest="key_opt", help="The required key/center letter (alternative to positional arg)")
    parser.add_argument("--wordlist", help="Path to a custom word list file (one word per line)")
    parser.add_argument(
        "--download",
        action="store_true",
        help="If no local word list is found, download one from GitHub",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=MIN_WORD_LENGTH,
        help=f"Minimum word length to accept (default: {MIN_WORD_LENGTH})",
    )
    args = parser.parse_args(argv)

    letters = args.letters_opt or args.letters
    key = args.key_opt or args.key

    if not letters or not key:
        try:
            line = input("Enter the 7 letters and key letter (e.g. 'abcdefg d'): ")
        except EOFError:
            parser.error("letters and key are required")
            return 2
        parts = line.split()
        if len(parts) != 2:
            parser.error("expected two space-separated values: letters and key")
            return 2
        letters, key = parts

    try:
        allowed_letters, key_letter = parse_letters(letters, key)
    except PuzzleError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    try:
        words = resolve_wordlist(args.wordlist, args.download)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    found = find_words(words, allowed_letters, key_letter, args.min_length)
    pangrams = [w for w in found if is_pangram(w, allowed_letters)]
    total_score = sum(score_word(w, allowed_letters) for w in found)

    print(f"Letters: {''.join(sorted(allowed_letters)).upper()}  Key: {key_letter.upper()}")
    print(f"Found {len(found)} words ({len(pangrams)} pangram{'s' if len(pangrams) != 1 else ''}), "
          f"maximum possible score {total_score}")
    print()

    by_length: dict[int, list[str]] = {}
    for w in found:
        by_length.setdefault(len(w), []).append(w)

    for length in sorted(by_length):
        words_of_length = by_length[length]
        print(f"-- {length} letters ({len(words_of_length)}) --")
        for w in words_of_length:
            marker = " *PANGRAM*" if is_pangram(w, allowed_letters) else ""
            print(f"  {w}{marker}")
        print()

    if pangrams:
        print("Pangrams:", ", ".join(pangrams))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Output was piped into something like `head` that closed early.
        sys.stderr.close()
        raise SystemExit(0)
