from enum import Enum
from itertools import pairwise
from pathlib import Path

import attr
from whoosh.fields import NUMERIC, TEXT, Schema
from whoosh.index import Index, create_in
from whoosh.searching import Results
from whoosh.qparser import OrGroup, QueryParser

from youtube_clipper.parsers.model import Subtitle
from youtube_clipper.parsers.registry import PARSERS_REGISTRY


# 1-to-1 correspondence with youtube_clipper.parsers.model:Subtitle
SEARCH_SCHEMA = Schema(id=NUMERIC(stored=True), offset=NUMERIC(stored=True), content=TEXT)


@attr.s
class SearchResult:
    offset: float = attr.ib()
    score: float = attr.ib()


class DeduplicationMode(Enum):
    DISABLE = 'disable'
    KEEP_FIRST = 'keep_first'
    KEEP_LAST = 'keep_last'


@attr.s
class SubtitlesSearcher:
    index_directory: str = attr.ib()
    limit: int | None = attr.ib(default=None)

    enable_pairwise_group: bool = attr.ib(default=False)
    deduplication_mode: DeduplicationMode = attr.ib(default=DeduplicationMode.KEEP_FIRST)

    index: Index = attr.ib(init=False, default=attr.Factory(
        lambda self: create_in(self.index_directory, SEARCH_SCHEMA), takes_self=True,
    ))

    def _get_query_parser(self) -> QueryParser:
        """
        See https://whoosh.readthedocs.io/en/latest/parsing.html#common-customizations
        """
        og = OrGroup.factory(0.9)
        return QueryParser('content', self.index.schema, group=og)

    def _normalize(self, text: str) -> str:
        return text.lower().translate(str.maketrans('', '', '.,!?'))

    def parse_results(self, results: Results) -> list[SearchResult]:
        """
        Parse results from searcher and perform a deduplication depending on a `self.deduplication_mode`:
        * DeduplicationMode.DISABLE - just parse results without a deduplication
        * DeduplicationMode.KEEP_FIRST - keep only the first subtitle in every chain of consecutive matches
        * DeduplicationMode.KEEP_LAST - keep only the last subtitle in every chain of consecutive matches
        """
        if not results or self.deduplication_mode == DeduplicationMode.DISABLE:  # skip deduplication
            return [SearchResult(offset=result['offset'], score=result.score) for result in results]

        ids = sorted(result['id'] for result in results)
        kept_ids: set[int] = {ids[0]}  # to cover a corner case of len(results) == 1
        removed_ids: set[int] = set()
        for id_pair in pairwise(ids):  # type: tuple[int, int]
            if id_pair[0] + 1 == id_pair[1]:  # consecutive subtitles - perform a deduplication
                if self.deduplication_mode == DeduplicationMode.KEEP_FIRST:
                    kept_ids.add(id_pair[0])
                    removed_ids.add(id_pair[1])
                elif self.deduplication_mode == DeduplicationMode.KEEP_LAST:
                    removed_ids.add(id_pair[0])
                    kept_ids.add(id_pair[1])
                else:
                    raise ValueError(f'Unknown deduplication mode {self.deduplication_mode}')
            else:  # non-consecutive subtitles - keep both
                kept_ids.add(id_pair[0])
                kept_ids.add(id_pair[1])

        return [  # preserving the original order
            SearchResult(offset=result['offset'], score=result.score)
            for result in results if result['id'] in kept_ids and result['id'] not in removed_ids
        ]

    def add_subtitles(self, filename: str) -> None:
        """
        Parses a subtitles file and adds subtitles to the search index
        Parser is chosen based on a file extension
        If enable_pairwise_group is True, subtitles will be joined in pairs
        """
        writer = self.index.writer()
        parser = PARSERS_REGISTRY[Path(filename).suffix]
        parsed_subtitles = parser().parse_subtitles(filename)

        if self.enable_pairwise_group:
            for subtitles_pair in pairwise(parsed_subtitles):  # type: tuple[Subtitle, Subtitle]
                joined_subtitle = Subtitle(
                    id=subtitles_pair[0].id,
                    offset=subtitles_pair[0].offset,
                    content=self._normalize(' '.join(sub.content for sub in subtitles_pair)),
                )
                writer.add_document(**attr.asdict(joined_subtitle))
        else:
            for subtitle in parsed_subtitles:
                subtitle.content = self._normalize(subtitle.content)
                writer.add_document(**attr.asdict(subtitle))

        writer.commit()

    def search(self, query_string: str) -> list[SearchResult]:
        """
        Perform a search on previously added subtitles
        """
        query_parser = self._get_query_parser()
        query = query_parser.parse(self._normalize(query_string))

        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=self.limit)
            return self.parse_results(results)

    def clear(self) -> None:
        """
        Clear the current index of all previously added documents
        """
        writer = self.index.writer()
        for docnum in range(self.index.doc_count()):
            writer.delete_document(docnum)
        writer.commit()
        assert self.index.doc_count() == 0
