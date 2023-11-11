import logging
from pathlib import Path

import attr
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from youtube_clipper.converter import convert_ttml_to_srt


LOGGER = logging.getLogger(__name__)


@attr.s
class SubtitlesDownloader:
    language: str = attr.ib()
    allow_autogenerated: bool = attr.ib(default=True)
    output_dir: str | None = attr.ib(default=None)
    verbose: bool = attr.ib(default=True)

    def download_subtitles(self, url: str) -> str | None:
        youtube_dl_params = dict(
            skip_download=True,  # don't download a video itself
            writesubtitles=True,  # download subtitles
            writeautomaticsub=self.allow_autogenerated,  # whether to include automatic subtitles
            subtitlesformat='ttml',  # works best with autogenerated subs (vtt duplicates lines)
            subtitleslangs=[self.language],
            verbose=self.verbose,
        )
        if self.output_dir:
            youtube_dl_params['outtmpl'] = f'{self.output_dir}/%(title)s.%(ext)s'
        LOGGER.info(f'YoutubeDL params: {youtube_dl_params}')

        try:
            with YoutubeDL(youtube_dl_params) as ydl:
                info = ydl.extract_info(url=url, ie_key='Youtube')  # ie_key ensures the Youtube extractor
                filename = Path(ydl.prepare_filename(info)).stem
        except DownloadError as e:
            LOGGER.error(f'Unable to download {url}: {e}')
            return

        filepath = Path(self.output_dir or '.') / f'{filename}.{self.language}.ttml'
        if not filepath.exists():
            LOGGER.warning(f'Subtitles file {filepath} not found, check YoutubeDL logs')
            return
        return convert_ttml_to_srt(str(filepath))
