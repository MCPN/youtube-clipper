from pathlib import Path
from tempfile import TemporaryDirectory

from youtube_clipper.searcher import DeduplicationMode, SearchResult, SubtitlesSearcher

import tests.test_data


TEST_DATA_DIR = Path(tests.test_data.__file__).parent


def get_testing_data(filename: str) -> str:
    return str(TEST_DATA_DIR / filename)


def get_timestamps(results: list[SearchResult]) -> set[float]:
    return {result.offset for result in results}


def test_basic_search() -> None:
    test_filename = get_testing_data('mEVnj0BOFbE.en.vtt')
    query = "Vaporeon"
    expected_timestamps = {4.56, 6.71, 6.72, 10.24, 12.39, 12.4, 29.119, 31.269, 31.279, 60.559, 62.79, 62.8}

    with TemporaryDirectory() as tempdir:
        searcher = SubtitlesSearcher(tempdir, enable_pairwise_group=False, deduplication_mode=DeduplicationMode.DISABLE)
        searcher.add_subtitles(test_filename)
        assert get_timestamps(searcher.search(query)) == expected_timestamps

        searcher.limit = 5
        results = searcher.search(query)
        assert len(results) == 5
        assert get_timestamps(results).issubset(expected_timestamps)


def test_pairwise_group() -> None:
    test_filename = get_testing_data('uCuWBWS4vfw_truncated.en.srt')
    query = '"FUMO have oversold"'
    with TemporaryDirectory() as tempdir:
        searcher = SubtitlesSearcher(tempdir, enable_pairwise_group=False)
        searcher.add_subtitles(test_filename)
        assert not searcher.search(query)

        searcher.clear()
        searcher.enable_pairwise_group = True
        searcher.add_subtitles(test_filename)
        results = searcher.search(query)
        assert len(results) == 1
        assert results[0].offset == 7.106


def test_deduplication() -> None:
    test_filename = get_testing_data('uCuWBWS4vfw_truncated.en.srt')
    query = '"seems more crazy"'
    with TemporaryDirectory() as tempdir:
        searcher = SubtitlesSearcher(tempdir, enable_pairwise_group=True, deduplication_mode=DeduplicationMode.DISABLE)
        searcher.add_subtitles(test_filename)
        raw_results = searcher.search(query)
        assert len(raw_results) == 2

        searcher.deduplication_mode = DeduplicationMode.KEEP_FIRST
        keep_first_results = searcher.search(query)
        assert len(keep_first_results) == 1
        assert keep_first_results[0].offset == 2.374

        searcher.deduplication_mode = DeduplicationMode.KEEP_LAST
        keep_last_results = searcher.search(query)
        assert len(keep_last_results) == 1
        assert keep_last_results[0].offset == 4.562
