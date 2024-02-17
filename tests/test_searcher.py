from pathlib import Path
from tempfile import TemporaryDirectory

from searcher import SubtitlesSearcher

TEST_DATA_DIR = Path('test_data')


def get_testing_data(filename: str) -> str:
    return str(TEST_DATA_DIR / filename)


def test_pairwise_group():
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
