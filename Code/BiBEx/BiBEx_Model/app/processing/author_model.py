from transformers import TokenClassificationPipeline
from ..body import *
import re
import unicodedata

# Matches: initial surname
regex_type_1 = r"^(?P<first>(?:[a-zA-Z]+[.][-\s]*)+)\s+(?P<last>[\w]{2,}[-'\w\s]*)+$"
pattern_1 = re.compile(regex_type_1)

# Matches: surname, initial
regex_type_2 = r"^(?P<last>(?:[a-zA-Z]+[-' ])*[a-zA-Z]+),\s+(?P<first>(?:[a-zA-Z][-.\s]*)+)$"
pattern_2 = re.compile(regex_type_2)

# Matches: surname INITIAL
regex_type_3 = r"^(?P<last>[a-zA-Z][a-zA-Z- ]+)\s(?P<first>[A-Z]{1,2})$"
pattern_3 = re.compile(regex_type_3)

# Matches firstname surname
normalized_char_dict = {
    "Ä": "AE",
    "Ü": "UE",
    "Ö": "OE",
    "ä": "ae",
    "ü": "ue",
    "ö": "oe",
}


class NERPipeline(TokenClassificationPipeline):
    def preprocess(self, sentence, offset_mapping=None):
        truncation = True if self.tokenizer.model_max_length and self.tokenizer.model_max_length > 0 else False
        model_inputs = self.tokenizer(
            sentence,
            return_tensors=self.framework,
            truncation=truncation,
            #is_split_into_words=True,
            return_special_tokens_mask=True,
            return_offsets_mapping=self.tokenizer.is_fast,
        )
        if offset_mapping:
            model_inputs["offset_mapping"] = offset_mapping
        model_inputs["sentence"] = sentence
        return model_inputs


def is_subtoken(token):
    return token.startswith("##") or (token == "-") or (token == ".")


def remove_accented_chars(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text


def strip_umlauts(text: str) -> str:
    for umlaut, replacement in normalized_char_dict.items():
        text = text.replace(umlaut, replacement)
    return text


def segment_initials(text: str) -> (str, str):
    first = None
    middle = ''
    first_groups = text.split()
    for group in first_groups:
        if "-" not in group:
            first_punct = group.split(".")
        else:
            first_punct = [group]
        for initial in first_punct:
            if first is None:
                first = initial
            else:
                middle += initial + ' '
    middle = middle.strip()
    return first, middle


def segment_author(author: str) -> dict:
    author = strip_umlauts(author)
    normalized_author = remove_accented_chars(author)
    tokens = normalized_author.split()
    result = {}

    if len(tokens) == 1:
        result["first"] = ""
        result["last"] = normalized_author
        result["middle"] = ""
        return result

    match = pattern_1.match(normalized_author)
    if match:
        first, middle = segment_initials(match.group("first"))
        result["first"] = first
        result["last"] = match.group("last")
        result["middle"] = middle
        return result

    match = pattern_2.match(normalized_author)
    if match:
        first, middle = segment_initials(match.group("first"))
        result["first"] = first
        result["last"] = match.group("last")
        result["middle"] = middle
        return result

    match = pattern_3.match(normalized_author)
    if match:
        first, middle = segment_initials(match.group("first"))
        result["first"] = first
        result["last"] = match.group("last")
        result["middle"] = middle
        return result

    if len(tokens) == 2:
        result["first"] = tokens[0]
        result["last"] = tokens[1]
        result["middle"] = ""
        return result

    if len(tokens) > 2:
        result["first"] = tokens[0]
        result["last"] = tokens[-1]
        result["middle"] = " ".join(tokens[1:-1])
        return result
    return result


def get_authors(chunks: list[ExtractedChunk], model, tokenizer) -> list[ExtractedChunk]:
    output = []
    authors = []
    authors_str = []

    for chunk in chunks:
        token_boxes = chunk.segment
        tokens = []
        boxes = []
        for token_box in token_boxes:
            # tokens.append(''.join(x for x in token_box.token if x.isalpha() or x.isspace() or x in punctuation))
            tokens.append(token_box.token)
            boxes.append(token_box.box)

        token_str = " ".join(tokens)
        # tokenized_words = models["ner_tokenizer"].tokenize([tokens], add_special_tokens=True)
        ner_results = model(token_str)

        author = []
        author_str = ""
        b_tag = None

        for res in ner_results:
            if res["entity"] == "B-PER" and not is_subtoken(res["word"]):
                if author:
                    authors.append(tokenizer.convert_tokens_to_string(author))
                    authors_str.append(author_str)
                author = [res["word"]]
                author_str = token_str[res["start"]:res["end"]]
                b_tag = res["entity"]
            elif res["entity"].startswith("B") and not is_subtoken(res["word"]):
                b_tag = res["entity"]
            elif ((res["entity"] == "I-PER") and not is_subtoken(res["word"])) or (
                    b_tag == "B-PER" and is_subtoken(res["word"])):
                author.append(res["word"])
                sep = "" if is_subtoken(res["word"]) else " "
                author_str += sep + token_str[res["start"]:res["end"]]
            else:
                if author:
                    authors.append(tokenizer.convert_tokens_to_string(author))
                    author = []
                    authors_str.append(author_str)
                    author_str = ""
        if author:
            authors.append(tokenizer.convert_tokens_to_string(author))
            authors_str.append(author_str)

    reduced_authors = []

    for i, author_outer in enumerate(authors_str):
        author_outer_lower = author_outer.lower()
        is_unique = True
        for j, author_inner in enumerate(authors_str):
            author_inner_lower = author_inner.lower()
            if i == j:
                continue
            elif author_outer_lower == author_inner_lower and author_outer not in reduced_authors:
                pass
            elif author_outer_lower in author_inner_lower:
                is_unique = False
                break
        if is_unique:
            author_outer = re.sub(r"\s*[-]\s*", "-", author_outer)
            reduced_authors.append(author_outer)

    for author in reduced_authors:
        author_dict = segment_author(author)
        if author_dict:
            output.append(
                ExtractedChunk(
                    segment=[SegmentedWord(
                        raw=author,
                        segmented=Author(
                            first_name=author_dict["first"],
                            middle_name=author_dict["middle"],
                            surname=author_dict["last"],
                        ),
                    )]
                )
            )
    return output
