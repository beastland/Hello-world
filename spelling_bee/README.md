# NYT Spelling Bee Solver

Solves NYT-style Spelling Bee puzzles: given seven letters (one of which is
the required "key"/center letter), find every valid word of at least four
letters that uses only those letters (repeats allowed) and includes the key
letter at least once. Pangrams (words using all seven letters) are flagged
and scored with the game's bonus.

## Usage

```
python3 solver.py ABCDEFG D
python3 solver.py --letters abcdefg --key d
python3 solver.py abcdefg d --wordlist /path/to/custom_words.txt
echo "abcdefg d" | python3 solver.py
```

## Dictionary

By default the solver reads `data/words.txt`, a bundled list of ~171,800
words:

- A base of the [ENABLE1](https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt)
  word-game dictionary, which excludes proper nouns and abbreviations for
  cleaner results.
- A curated supplement of modern/internet-era words (e.g. `wifi`, `selfie`,
  `podcast`, `meme`, `hashtag`, `cosplay`) that older word lists tend to
  miss.
- A curated supplement of common internet acronyms (e.g. `yolo`, `fomo`,
  `nsfw`, `lmao`, `rofl`) and profanity/slang (e.g. `shit`, `fuck`, `damn`,
  `bitch`), most of which were already present in the ENABLE1 base — see the
  full list in git history at the commit that added it. Note that 3-letter
  acronyms like `lol` and `smh` can never appear in the output regardless of
  the dictionary, since the solver enforces a 4-letter minimum word length.

`data/words.txt` is a flat, one-word-per-line file — to add or remove words
yourself, just edit it directly (or point at a different file entirely with
`--wordlist path/to/file.txt`). Pass `--download` to fetch a fresh copy of
the base ENABLE1 dictionary from GitHub if no local word list is found.

Note: this won't be a perfect match to any single day's official NYT answer
list, since NYT's list is proprietary and hand-curated to exclude certain
obscure, offensive, or otherwise unwanted words — but it will find
effectively every legitimate English word (plus common modern slang) that
fits the puzzle rules.
