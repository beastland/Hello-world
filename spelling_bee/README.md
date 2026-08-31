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

By default the solver reads `data/words.txt`, a bundled list of ~172,000
words:

- A base of the [ENABLE1](https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt)
  word-game dictionary, which excludes proper nouns and abbreviations for
  cleaner results.
- A curated supplement of modern/internet-era words (e.g. `wifi`, `selfie`,
  `podcast`, `meme`, `hashtag`, `cosplay`) that older word lists tend to
  miss.

You can point at a different dictionary with `--wordlist path/to/file.txt`
(one word per line), or pass `--download` to fetch a fresh copy of the base
ENABLE1 dictionary from GitHub if no local word list is found.

Note: this won't be a perfect match to any single day's official NYT answer
list, since NYT's list is proprietary and hand-curated to exclude certain
obscure or offensive words — but it will find effectively every legitimate
English word that fits the puzzle rules.
