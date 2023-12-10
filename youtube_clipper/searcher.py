from pathlib import Path

import attr
from whoosh.fields import NUMERIC, TEXT, Schema
from whoosh.index import Index, create_in
from whoosh.searching import Results
from whoosh.qparser import OrGroup, QueryParser

from youtube_clipper.parsers.registry import PARSERS_REGISTRY


# 1-to-1 correspondence with youtube_clipper.parsers.model:Subtitle
SEARCH_SCHEMA = Schema(id=NUMERIC(stored=True), offset=NUMERIC(stored=True), content=TEXT)


@attr.s
class SearchResult:
    offset: float = attr.ib()
    score: float = attr.ib()


@attr.s
class SubtitlesSearcher:
    index_directory: str = attr.ib()
    limit: int | None = attr.ib(default=None)
    deduplication_range: float | None = attr.ib(default=None)

    index: Index = attr.ib(init=False, default=attr.Factory(
        lambda self: create_in(self.index_directory, SEARCH_SCHEMA), takes_self=True,
    ))

    def get_query_parser(self) -> QueryParser:
        og = OrGroup.factory(0.9)  # https://whoosh.readthedocs.io/en/latest/parsing.html#common-customizations
        return QueryParser('content', self.index.schema, group=og)

    def normalize_query_string(self, query_string: str) -> str:
        return query_string.lower().translate(str.maketrans('', '', '.,!?'))

    def parse_results(self, results: Results) -> list[SearchResult]:
        """
        if deduplication_range is not None, performs a deduplication:
        sort the results by offset and iterate them from left to right;
        if we encounter two results within the deduplication range,
        we keep the best by score or the first one in case
        of equal scores
        """
        if self.deduplication_range is None:  # deduplication is disabled
            return [SearchResult(offset=result['offset'], score=result.score) for result in results]

        sorted_results = sorted(results, key=lambda x: x['offset'])
        if not sorted_results:
            return []

        current_result = sorted_results[0]
        kept_ids: set[int] = set()
        for result in sorted_results[1:]:
            # first case - the next result is far enough from the current one
            # this means the current result is safe and we can add it to the final result
            if result['offset'] - current_result['offset'] > self.deduplication_range:
                kept_ids.add(current_result['id'])
                current_result = result

            # second case - the next result is in the range and it's better
            # than the current one. then we just replace the current result
            elif result.score > current_result.score:
                current_result = result

            # last case - the next result is in the range and it's worse
            # we just skip it
            # else: pass

        if current_result['id'] not in kept_ids:
            kept_ids.add(current_result['id'])

        return [  # preserving the original order
            SearchResult(offset=result['offset'], score=result.score)
            for result in results if result['id'] in kept_ids
        ]

    def add_subtitles(self, filename: str) -> None:
        writer = self.index.writer()
        parser = PARSERS_REGISTRY[Path(filename).suffix]
        for subtitle in parser().parse_subtitles(filename):
            subtitle.content = self.normalize_query_string(subtitle.content)
            writer.add_document(**attr.asdict(subtitle))
        writer.commit()

    def search(self, query_string: str) -> list[SearchResult]:
        query_parser = self.get_query_parser()
        query = query_parser.parse(self.normalize_query_string(query_string))

        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=self.limit)
            return self.parse_results(results)
