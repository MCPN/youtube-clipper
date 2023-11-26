from typing import Type

from youtube_clipper.parsers.model import SubtitleParser
from youtube_clipper.parsers.srt import SRTParser


PARSERS_REGISTRY: dict[str, Type[SubtitleParser]] = {
    '.srt': SRTParser,
}
