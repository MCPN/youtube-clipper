import attr
import pytest

from youtube_clipper.converters.registry import CONVERTERS_REGISTRY
from youtube_clipper.parsers.model import Subtitle
from youtube_clipper.parsers.registry import PARSERS_REGISTRY
from youtube_clipper.searcher import SEARCH_SCHEMA
from youtube_clipper.utils import get_available_formats, get_url_from_filename


def test_searcher_schema() -> None:
    model_fields = set(attr.fields_dict(Subtitle))
    schema_fields = set(SEARCH_SCHEMA.names())
    assert model_fields == schema_fields == {'id', 'offset', 'content'}


def test_converters_compatability() -> None:
    assert all(converter.ext_to in PARSERS_REGISTRY for converter in CONVERTERS_REGISTRY.values())


def test_available_formats() -> None:
    assert set(get_available_formats()) == {'srt', 'ttml', 'vtt'}


@pytest.mark.parametrize('filename', [
    'dQw4w9WgXcQ.en.srt',
    'dQw4w9WgXcQ.en.ttml',
    'dQw4w9WgXcQ.ru.ttml',
    'dQw4w9WgXcQ.srt',
])
def test_get_url_from_filename(filename: str) -> None:
    assert get_url_from_filename(filename) == 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
