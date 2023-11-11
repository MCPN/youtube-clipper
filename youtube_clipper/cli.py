import argparse
import tempfile

from youtube_clipper.downloader import SubtitlesDownloader
from youtube_clipper.searcher import SubtitlesSearcher


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--video')
    parser.add_argument('--language', default='en')
    parser.add_argument('--allow-autogenerated', action='store_true')
    parser.add_argument('--query')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tempdir:
        downloader = SubtitlesDownloader(
            language=args.language,
            allow_autogenerated=args.allow_autogenerated,
            output_dir=tempdir,
        )
        subtitles_filename = downloader.download_subtitles(args.video)
        if subtitles_filename is None:
            exit(1)

        searcher = SubtitlesSearcher(index_directory=tempdir)
        searcher.add_subtitles(subtitles_filename)
        offsets = searcher.search(args.query)

        if not offsets:
            print('Query not found')
        for offset in offsets:
            print(args.video + f'&t={int(offset)}s')
