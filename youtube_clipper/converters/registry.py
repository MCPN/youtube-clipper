from typing import Type

from youtube_clipper.converters.model import SubtitlesConverter
from youtube_clipper.converters.ttml_to_srt import TTMLToSRTConverter


CONVERTERS_REGISTRY: dict[str, Type[SubtitlesConverter]] = {
    '.ttml': TTMLToSRTConverter,
}
