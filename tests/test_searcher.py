from pathlib import Path
from tempfile import TemporaryDirectory

from youtube_clipper.searcher import SubtitlesSearcher, DeduplicationMode

import tests.test_data


TEST_DATA_DIR = Path(tests.test_data.__file__).parent


def get_testing_data(filename: str) -> str:
    return str(TEST_DATA_DIR / filename)


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
