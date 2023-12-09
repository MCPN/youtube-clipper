import attr

from youtube_clipper.parsers.model import Subtitle
from youtube_clipper.searcher import SEARCH_SCHEMA


def test_searcher_schema():
    model_fields = set(attr.fields_dict(Subtitle))
    schema_fields = {key for key, value in SEARCH_SCHEMA.items()}
    assert model_fields == schema_fields
