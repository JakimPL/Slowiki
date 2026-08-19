from lexica.grammar.dialect import TagsetDialect
from lexica.grammar.polimorf_segments import POLIMORF_SEGMENTS
from lexica.grammar.segments import SegmentTable
from lexica.grammar.sgjp_segments import SGJP_SEGMENTS


def segment_table(dialect: TagsetDialect) -> SegmentTable:
    match dialect:
        case TagsetDialect.SGJP:
            return SGJP_SEGMENTS
        case TagsetDialect.POLIMORF:
            return POLIMORF_SEGMENTS
