import logging
import xml.etree.ElementTree as ET

import ttconv.imsc.reader as imsc_reader
import ttconv.srt.writer as srt_writer

from youtube_clipper.converters.model import SubtitlesConverter


LOGGER = logging.getLogger(__name__)
logging.getLogger('ttconv').setLevel(logging.ERROR)  # too much noise on the WARNING level


class TTMLToSRTConverter(SubtitlesConverter):
    ext_from = '.ttml'
    ext_to = '.srt'

    def _convert(self, source_filename: str, output_filename: str) -> None:
        """
        See ttconv docs:
        https://github.com/sandflow/ttconv/blob/master/doc/imsc_reader.md
        https://github.com/sandflow/ttconv/blob/master/doc/srt_writer.md
        """

        xml_doc = ET.parse(source_filename)
        logging.info(f'Loading a ttml model for {source_filename}')
        doc = imsc_reader.to_model(xml_doc)
        logging.info(f'Converting {source_filename} to srt')
        with open(output_filename, 'w') as f:
            print(srt_writer.from_model(doc), file=f)
        logging.info(f'Conversion completed!')
