import srt

from youtube_clipper.parsers.model import Subtitle, SubtitleParser


class SRTParser(SubtitleParser):
    def parse_subtitles(self, filename: str) -> list[Subtitle]:
        with open(filename) as f:
            subtitles = srt.parse(f.read())
        return [
            Subtitle(id=subtitle.index, offset=subtitle.start.total_seconds(), content=subtitle.content)
            for subtitle in subtitles
        ]
