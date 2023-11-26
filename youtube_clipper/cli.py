import argparse
import tempfile
from pathlib import Path

from colorama import Fore, Style

from youtube_clipper.downloader import SubtitlesDownloader
from youtube_clipper.searcher import SubtitlesSearcher


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--subs-dir', required=False)
    parser.add_argument('--language', default='en')
    parser.add_argument('--allow-autogenerated', action='store_true')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tempdir:
        subs_dir = args.subs_dir or tempdir
        downloader = SubtitlesDownloader(
            language=args.language,
            formats=['str', 'ttml'],
            allow_autogenerated=args.allow_autogenerated,
            output_dir=subs_dir,
        )

        for filename in downloader.download_subtitles(args.url):
            # Path(filename).stem would only remove the last extension, and
            # a file from SubtitlesDownloader.download_subtitles would typically
            # have multiple, e.g. *.en.ttml
            path = Path(filename)
            video_id = path.name.removesuffix(''.join(path.suffixes))
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            print(Fore.YELLOW + f'Searching for "{args.query}" in {video_url}' + Style.RESET_ALL)

            searcher = SubtitlesSearcher(tempdir)
            searcher.add_subtitles(filename)
            offsets = searcher.search(args.query)
            if not offsets:
                print(Fore.RED + f'"{args.query}" wasn\'t found in {video_url}' + Style.RESET_ALL)
            else:
                print(Fore.GREEN + f'Found {len(offsets)} (approximate) occurrences of "{args.query}" in {video_url}:')
                for offset in offsets:
                    print(f'{video_url}&t={int(offset)}s')
            print(Style.RESET_ALL)
