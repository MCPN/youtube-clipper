from collections.abc import Generator

import srt

from youtube_clipper.parsers.model import Subtitle, SubtitleParser


class SRTParser(SubtitleParser):
    def parse_subtitles(self, filename: str) -> Generator[Subtitle, None, None]:
        with open(filename) as f:
            subtitles = srt.parse(f.read())
        for subtitle in subtitles:
            yield Subtitle(id=subtitle.index, offset=subtitle.start.total_seconds(), content=subtitle.content)
