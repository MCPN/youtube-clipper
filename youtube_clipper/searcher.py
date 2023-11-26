from pathlib import Path

import attr
from whoosh.fields import NUMERIC, TEXT, Schema
from whoosh.index import Index, create_in
from whoosh.qparser import OrGroup, QueryParser

from youtube_clipper.parsers.registry import PARSERS_REGISTRY


# 1-to-1 correspondence with youtube_clipper.parsers.model:Subtitle
SCHEMA = Schema(id=NUMERIC(stored=True), offset=NUMERIC(stored=True), content=TEXT)


@attr.s
class SubtitlesSearcher:
    index_directory: str = attr.ib()
    index: Index = attr.ib(init=False, default=attr.Factory(
        lambda self: create_in(self.index_directory, SCHEMA), takes_self=True,
    ))

    def get_query_parser(self) -> QueryParser:
        og = OrGroup.factory(0.9)  # https://whoosh.readthedocs.io/en/latest/parsing.html#common-customizations
        return QueryParser('content', self.index.schema, group=og)

    def normalize_query_string(self, query_string: str) -> str:
        return query_string.lower().translate(str.maketrans('', '', '.,!?'))

    def add_subtitles(self, filename: str) -> None:
        writer = self.index.writer()
        parser = PARSERS_REGISTRY[Path(filename).suffix]
        for subtitle in parser().parse_subtitles(filename):
            subtitle.content = self.normalize_query_string(subtitle.content)
            writer.add_document(**attr.asdict(subtitle))
        writer.commit()

    def search(self, query_string: str) -> list[float]:
        query_parser = self.get_query_parser()
        query = query_parser.parse(self.normalize_query_string(query_string))

        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=None)
            return [result['offset'] for result in results]
