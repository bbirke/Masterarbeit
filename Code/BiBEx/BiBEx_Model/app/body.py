from pydantic import BaseModel


class Reference(BaseModel):
    text: str


class Author(BaseModel):
    first_name: str | None
    middle_name: str | None
    surname: str | None


class SegmentedWord(BaseModel):
    raw: str | None
    segmented: Author | None


class ReferenceEntity(BaseModel):
    entity_id: int
    entity_group: str
    score: float
    word: SegmentedWord


class BoundingBox(BaseModel):
    x0: int
    y0: int
    x1: int
    y1: int


class TokenBox(BaseModel):
    token: str
    box: BoundingBox | None


class Token(BaseModel):
    token: str


class ReferenceBoxEntity(BaseModel):
    entity_id: int
    entity_group: str
    score: float
    word: str
    boxes: list[BoundingBox]


class ReferenceEntityGroup(BaseModel):
    reference_id: int
    reference_string: str
    reference: list[ReferenceEntity | ReferenceBoxEntity]


class SegmentedReference(BaseModel):
    number_of_references: int
    references: list[ReferenceEntityGroup]


class ExtractedToken(BaseModel):
    token_id: int
    token: str
    bbox: BoundingBox
    label: str


class ExtractedPage(BaseModel):
    page_id: int
    tokens: list[ExtractedToken]


class ExtractedTokens(BaseModel):
    number_of_pages: int
    pages: list[ExtractedPage]


class ExtractedChunk(BaseModel):
    segment: list[TokenBox | Token | SegmentedWord]


# class ExtractedChunks(BaseModel):
#     segments: list[ExtractedChunk]


class ExtractedSegments(BaseModel):
    authors: list[ExtractedChunk]
    titles: list[ExtractedChunk]
    abstracts: list[ExtractedChunk]

    fallback_authors: list[ExtractedChunk]
    fallback_titles: list[ExtractedChunk]
    fallback_abstracts: list[ExtractedChunk]

    segmented_references: SegmentedReference


