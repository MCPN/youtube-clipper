# youtube-clipper

Tool for finding clips in YouTube videos. Supports searching in multiple videos, e.g. in playlists or channels.

YouTube Clipper (YTC) downloads subtitles (without videos themselves) using [yt-dlp](https://github.com/yt-dlp/yt-dlp), parses them using provided parsers and converters and performs the search using [whoosh](https://whoosh.readthedocs.io).

## Installation

### From PyPI

1. Create and activate a virtualenv: `python3 -m venv .venv && source .venv/bin/activate`.
2. Install `youtube-clipper` using `pip`: `pip install youtube-clipper`

### From source

1. Clone the repository: `git clone git@github.com:MCPN/youtube-clipper.git`.
2. Install poetry: `pip install poetry`.
3. Install `youtube-clipper` using `poetry`: `cd youtube-clipper && poetry install`.
4. To install test dependencies, run `poetry install --with tests`.

## Usage

Basic usage: `youtube-clipper --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --query 'were no strangers to love' --allow-autogenerated`.

There are two groups of additional arguments:
1. yt-dlp arguments are passed almost directly to the yt-dlp client and are related to downloaded subtitles
2. Searcher arguments are used after the download and control the search process and postprocessing.

For a full list of settings, run `youtube-clipper --help`.

## Downloading subtitles

By default, yt-dlp will only look for manual subtitles. By adding the `--allow-autogenerated` option, one allows yt-dlp to download autogenerated subtitles, but manual ones are always preferred.

Despite YouTube only showing autogenerated subtitles in one language, there are often many translated versions in a yt-dlp result, so a search can be performed in a completely different one. For example, `youtube-clipper --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --query 'нам не чужда любовь' --allow-autogenerated --language ru --search-limit 1` surprisingly outputs the correct result.

However, one should note that autogenerated subtitles can be faulty, are often censored of obscene language, and contain marks like `[Music]`, so exact searches over autogenerated subtitles are not recommended.

## Query language

The query argument supports the whoosh query language. The full description can be found in the [official documentation](https://whoosh.readthedocs.io/en/latest/querylang.html), here are some key features:

* By default, the searcher doesn't require all words to appear in the result, with more matched words resulting in a better overall match. To search for an exact phrase, one can wrap a query in `"double quotes"` (be careful with bash escaping!)
* While using the phrase search, one can allow words to be at a certain distance from each other `"like this"~5` (now `like` can be within 5 words from `this`)
* On the other hand, while allowing imperfect search, one can boost or lower the importance of a certain word using the `^` operator. For example, in query `i^2 love cookies^0.5` the word `i` is twice as important as the word `love` while the word `cookies` is half as important

## Pairwise grouping and deduplication

Searcher treats every separate subtitle (i.e. the phrase that appears on a screen at a singular moment) as its own document. The problem occurs when a phrase is split between two subtitles. In this case, the exact search will fail, while the regular one might be inaccurate.

To deal with it, one can enable pairwise grouping for the subtitles with the `--enable-pairwise-group` option. When enabled, every successive overlapping subtitle pair will be merged into one subtitle, and a search will be performed on new subtitles. For example, given three subtitles with phrases `a`, `b` and `c` respectively, the pairwise grouping will generate two new subtitles with phrases `a b` and `b c`.

Note that autogenerated subtitles already have overlaps in them, so the pairwise grouping might be excessive.

The downside of using pairwise grouping is that output might contain duplicates: indeed, a search query can match a common part of new subtitles (for example, in the previous example a search for `b` will match twice). The `--deduplication-mode` option allows to remove these duplicates:
* When set to `--keep-first`, if two consecutive subtitles are in the output, only the first one will be kept. This also applies to a chain of more than two consecutive subtitles
* When set to `--keep-last`, the last subtitle in a consecutive chain will be kept
* When set to `--disable`, the deduplication is skipped

By default, the pairwise grouping is disabled and deduplication with the keep first mode is enabled. When searching in manual subtitles, pairwise grouping is highly recommended, and as for the deduplication, the keep first mode is preferred because the keep last mode can result in a timestamp that points after the phrase.

## Development

### Parsers and converters

There is an easy API for adding new subtitle formats to YTC. To do so, one should implement a parser interface at `youtube_clipper.parsers.model:SubtitleParser` and add the implementation to the registry at `youtube_clipper.parsers.model:PARSERS_REGISTRY`.

Alternatively, one can implement a converter for a currently unsupported format that will output a new file with an existing parser for it. This is done similarly to parsers, one should implement a parser interface at `youtube_clipper.converters.model:SubtitlesConverter` and add the implementation to the registry at `youtube_clipper.converters.model:CONVERTERS_REGISTRY`. Tests ensure that every converter has a corresponding parser.

### Tests

Testing is done using pytest: `pytest tests`.

Type checking is done using mypy: `mypy youtube_clipper tests`. However, it's not very efficient, as most of the dependencies don't have stubs.
