import logging
from pathlib import Path
from typing import Generator

import attr
from yt_dlp import YoutubeDL
from yt_dlp.extractor import gen_extractor_classes

from youtube_clipper.converters.exc import NoCorrespondingParserException
from youtube_clipper.converters.registry import CONVERTERS_REGISTRY
from youtube_clipper.parsers.registry import PARSERS_REGISTRY


LOGGER = logging.getLogger(__name__)


@attr.s
class SubtitlesDownloader:
    language: str = attr.ib()
    formats: list[str] = attr.ib(validator=attr.validators.min_len(1))
    output_dir: str = attr.ib()
    allow_autogenerated: bool = attr.ib(default=True)
    verbose: bool = attr.ib(default=False)
    quiet: bool = attr.ib(default=True)

    _converted_dir: str = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        converted_dir = Path(self.output_dir) / 'converted'
        converted_dir.mkdir(parents=True, exist_ok=True)  # ensure the dir exists
        self._converted_dir = str(converted_dir)

    def download_subtitles(self, url: str) -> None:
        youtube_dl_params = dict(
            skip_download=True,  # don't download a video itself
            writesubtitles=True,  # download subtitles
            writeautomaticsub=self.allow_autogenerated,  # whether to include automatic subtitles
            subtitlesformat='/'.join(self.formats),
            subtitleslangs=[self.language],
            outtmpl=f'{self.output_dir}/%(id)s.%(ext)s',
            verbose=self.verbose,
            quiet=self.quiet,
        )
        LOGGER.info(f'YoutubeDL params: {youtube_dl_params}')

        with YoutubeDL(youtube_dl_params, auto_init=False) as ydl:
            extractors = gen_extractor_classes()
            for extractor in extractors:  # keep only youtube extractors
                if extractor.__name__.startswith('Youtube'):
                    ydl.add_info_extractor(extractor)
            ydl.extract_info(url=url)

    def get_subtitles(self, url: str) -> Generator[str, None, None]:
        self.download_subtitles(url)
        for path in Path(self.output_dir).iterdir():
            if not path.is_file():
                continue

            ext = path.suffix
            if ext in CONVERTERS_REGISTRY:  # convert subtitles and return a new filename
                converter = CONVERTERS_REGISTRY[ext]
                if converter.ext_to not in PARSERS_REGISTRY:
                    raise NoCorrespondingParserException(
                        f'Converter {converter.__name__} doesn\'t have a corresponding parser'
                    )
                LOGGER.info(f'Going to convert {path} with a {converter.__name__}')
                converted_filename = converter(output_dir=self._converted_dir).convert(str(path))
                yield converted_filename
            elif ext in PARSERS_REGISTRY:  # can be parsed straight away
                yield str(path)
            else:
                LOGGER.warning(f'Unknown extension {ext} for a file {path}')
