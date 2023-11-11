import attr
import srt
from whoosh.fields import NUMERIC, Schema, TEXT
from whoosh.index import Index, create_in
from whoosh.qparser import OrGroup, QueryParser


SCHEMA = Schema(id=NUMERIC(stored=True), offset=NUMERIC(stored=True), content=TEXT)


@attr.s
class SubtitlesSearcher:
    index_directory: str = attr.ib()
    index: Index = attr.ib(init=False, default=attr.Factory(
        lambda self: create_in(self.index_directory, SCHEMA), takes_self=True,
    ))

    def add_subtitles(self, filename: str) -> None:
        writer = self.index.writer()
        with open(filename) as f:
            subtitles = srt.parse(f.read())
        for subtitle in subtitles:
            writer.add_document(id=subtitle.index, offset=subtitle.start.total_seconds(), content=subtitle.content)
        writer.commit()

    def search(self, query_string: str) -> list[float]:
        og = OrGroup.factory(0.9)
        parser = QueryParser('content', self.index.schema, group=og)
        normalized_query = query_string.lower().translate(str.maketrans('', '', '.,!?'))
        query = parser.parse(normalized_query)

        with self.index.searcher() as searcher:
            results = searcher.search(query)
            return [result['offset'] for result in results]
