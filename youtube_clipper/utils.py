from pathlib import Path

from youtube_clipper.converters.registry import CONVERTERS_REGISTRY
from youtube_clipper.parsers.registry import PARSERS_REGISTRY


YOUTUBE_PREFIX = 'https://www.youtube.com/watch'


def get_url_from_filename(filename: str) -> str:
    """
    Path(filename).stem would only remove the last extension, and
    a file from SubtitlesDownloader.download_subtitles would typically
    have multiple, e.g. *.en.ttml
    """
    path = Path(filename)
    video_id = path.name.removesuffix(''.join(path.suffixes))
    return f'{YOUTUBE_PREFIX}?v={video_id}'


def get_available_formats() -> list[str]:
    """Get all available formats from converters and parsers registries"""
    return list(map(lambda ext: ext.removeprefix('.'), CONVERTERS_REGISTRY.keys() | PARSERS_REGISTRY.keys()))
