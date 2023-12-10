import attr

from youtube_clipper.parsers.model import Subtitle
from youtube_clipper.searcher import SEARCH_SCHEMA


def test_searcher_schema():
    model_fields = set(attr.fields_dict(Subtitle))
    schema_fields = set(SEARCH_SCHEMA.names())
    assert model_fields == schema_fields == {"id", "offset", "content"}
