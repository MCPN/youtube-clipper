import webvtt

from youtube_clipper.parsers.model import Subtitle, SubtitleParser


class VTTParser(SubtitleParser):
    @staticmethod
    def _parse_timestamp(timestamp: str) -> float:
        h, m, s = timestamp.split(':', maxsplit=3)
        return 3600 * int(h) + 60 * int(m) + float(s)

    def parse_subtitles(self, filename: str) -> list[Subtitle]:
        return [
            Subtitle(id=idx, offset=self._parse_timestamp(caption.start), content=caption.text)
            for idx, caption in enumerate(webvtt.read(filename))
        ]
