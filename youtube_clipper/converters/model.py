import abc
from pathlib import Path
from typing import ClassVar

import attr

from youtube_clipper.converters.exc import ExtensionError


@attr.s
class SubtitlesConverter(abc.ABC):
    ext_from: ClassVar[str]
    ext_to: ClassVar[str]

    output_dir: str = attr.ib()

    @abc.abstractmethod
    def _convert(self, source_filename: str, output_filename: str) -> None:
        """
        Main implementation, should read subtitles from `source_filename` and
        output the result to `output_filename`
        """
        pass

    def convert(self, source_filename: str) -> str:
        """
        Converts subtitles from `source_filename` with `ext_from` extension
        to a corresponding file with `ext_to` extension
        """
        path = Path(source_filename)
        if path.suffix != self.ext_from:
            raise ExtensionError(f'Expected {self.ext_from} file, got {source_filename}')
        output_filename = f'{self.output_dir}/{path.stem}{self.ext_to}'
        self._convert(source_filename, output_filename)
        return output_filename
