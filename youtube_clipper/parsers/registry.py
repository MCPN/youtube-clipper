from typing import Type

from youtube_clipper.parsers.model import SubtitleParser
from youtube_clipper.parsers.srt import SRTParser
from youtube_clipper.parsers.vtt import VTTParser


PARSERS_REGISTRY: dict[str, Type[SubtitleParser]] = {
    '.srt': SRTParser,
    '.vtt': VTTParser,
}
