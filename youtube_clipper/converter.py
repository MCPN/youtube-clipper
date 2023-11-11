import os
import xml.etree.ElementTree as ET

import ttconv.imsc.reader as imsc_reader
import ttconv.srt.writer as srt_writer

from youtube_clipper.exc import ExtensionError


def convert_ttml_to_srt(filename: str) -> str:
    """
    See ttconv docs:
    https://github.com/sandflow/ttconv/blob/master/doc/imsc_reader.md
    https://github.com/sandflow/ttconv/blob/master/doc/srt_writer.md
    """
    name, ext = os.path.splitext(filename)
    if ext != '.ttml':
        raise ExtensionError(f'Attempt to convert non-ttml file {filename}')

    xml_doc = ET.parse(filename)
    doc = imsc_reader.to_model(xml_doc)
    output_file = name + '.srt'
    with open(output_file, 'w') as f:
        print(srt_writer.from_model(doc), file=f)
    return output_file
