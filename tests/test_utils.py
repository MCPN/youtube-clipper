import attr

from youtube_clipper.converters.registry import CONVERTERS_REGISTRY
from youtube_clipper.parsers.model import Subtitle
from youtube_clipper.parsers.registry import PARSERS_REGISTRY
from youtube_clipper.searcher import SEARCH_SCHEMA
from youtube_clipper.utils import get_available_formats


def test_searcher_schema():
    model_fields = set(attr.fields_dict(Subtitle))
    schema_fields = set(SEARCH_SCHEMA.names())
    assert model_fields == schema_fields == {"id", "offset", "content"}


def test_converters_compatability():
    assert all(converter.ext_to in PARSERS_REGISTRY for converter in CONVERTERS_REGISTRY.values())


def test_available_formats():
    assert set(get_available_formats()) == {'srt', 'ttml', 'vtt'}
