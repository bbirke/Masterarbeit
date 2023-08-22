from typing import List
from tokenizers.pre_tokenizers import Sequence, Whitespace, Digits, Split
from dehyphen import FlairScorer, text_to_format
from ..body import TokenBox


def get_pre_tokenizer(split_tokens: List[str] = None) -> Sequence:
    if split_tokens is None:
        split_tokens = [".", ":", ",", ";", "/", "-", "(", ")"]
    tokenizer_list = [Whitespace(), Digits()]
    for token in split_tokens:
        tokenizer_list.append(Split(token, behavior="isolated"))
    return Sequence(tokenizer_list)


def dehyphen_references(references: list[TokenBox]) -> str:
    scorer = FlairScorer(lang="multi-v0")
    reference_string = ''
    last_y0 = None
    for ref, box in references:
        if last_y0 is None:
            last_y0 = box[1]
        if last_y0 < box[1]:
            reference_string += "\n"
        else:
            reference_string += " "
        reference_string += ref

        last_y0 = box[1]
    dehyphen_references = scorer.dehyphen(text_to_format(reference_string))
    dehyphen_reference_string = ""
    for dehyphen_token_list in dehyphen_references[0]:
        for dehyphen_token in dehyphen_token_list:
            dehyphen_reference_string += dehyphen_token.strip() + " "
    return dehyphen_reference_string.strip()


def dehyphen_reference_str(reference_str: str) -> str:
    if "\n" not in reference_str:
        return reference_str
    scorer = FlairScorer(lang="multi-v0")
    dehyphen_references = scorer.dehyphen(text_to_format(reference_str))
    dehyphen_reference_string = ""
    for dehyphen_token_list in dehyphen_references[0]:
        for dehyphen_token in dehyphen_token_list:
            dehyphen_reference_string += dehyphen_token.strip() + " "
    return dehyphen_reference_string.strip()
