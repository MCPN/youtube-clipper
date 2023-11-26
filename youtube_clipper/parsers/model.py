import abc

import attr


@attr.s
class Subtitle:
    id: int = attr.ib()
    offset: float = attr.ib()
    content: str = attr.ib()


class SubtitleParser(abc.ABC):
    @abc.abstractmethod
    def parse_subtitles(self, filename: str) -> list[Subtitle]:
        pass
