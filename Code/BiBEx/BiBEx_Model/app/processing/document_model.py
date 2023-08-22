import numpy as np
import torch
from PIL import Image
from transformers import BatchEncoding, LayoutLMv2Model
from transformers.models.layoutlmv2 import LayoutLMv2FeatureExtractor
from transformers.models.layoutxlm import LayoutXLMProcessor
from transformers.models.layoutxlm import LayoutXLMTokenizerFast

from ..config import Config
from ..body import TokenBox, BoundingBox, ExtractedChunk

config = Config()


def get_processor(apply_ocr=False, ocr_lang="deu"):
    feature_extractor = LayoutLMv2FeatureExtractor(apply_ocr=apply_ocr, ocr_lang=ocr_lang)
    tokenizer = LayoutXLMTokenizerFast.from_pretrained(config.get_conf_value("Paths", "PathModelDocExt"))
    processor = LayoutXLMProcessor(feature_extractor, tokenizer)
    return processor


def process_images(images: list[Image], processor: LayoutXLMProcessor, ocr: bool = True, tokens: list[list[str]] = None,
                   bboxes: list[list[list[int]]] = None, max_length: int = 512) -> list[BatchEncoding]:
    """
Preprocess all input images. The tokens and bounding boxes must be provided, if OCR is not applied.
    :param images: The images, which should be processed.
    :param processor: The LayoutXLM processor.
    :param ocr: Specify if OCR should be applied.
    :param tokens: All word tokens.
    :param bboxes: The bounding boxes of the provided word tokens.
    :param max_length: Max truncation length of the processor.
    :return: A list of BatchEncodings extracted from all images.
    """
    if not ocr and (tokens is None or bboxes is None):
        raise ValueError("Expected tokens and bounding boxes, if OCR is not applied.")

    processed_pages = []
    for i, img in enumerate(images):
        if ocr:
            processed = processor(img, return_tensors="pt", padding="max_length", truncation=True,
                                  max_length=max_length,
                                  return_overflowing_tokens=True, return_offsets_mapping=True)
        else:
            processed = processor(img, return_tensors="pt", text=tokens[i], boxes=bboxes[i], padding="max_length",
                                  truncation=True, max_length=max_length, return_overflowing_tokens=True,
                                  return_offsets_mapping=True)
        processed_pages.append(processed)
    return processed_pages


def predict(processed_pages: list[BatchEncoding], model: LayoutLMv2Model, tokenizer: LayoutXLMTokenizerFast):
    output_list = []
    for i, processed in enumerate(processed_pages):
        with torch.no_grad():
            outputs = model(input_ids=processed['input_ids'],
                            attention_mask=processed['attention_mask'],
                            bbox=processed['bbox'],
                            image=torch.stack(processed['image']), )
            output_list.append(outputs)

    output_tokens_list = []
    output_boxes_list = []
    output_predictions_list = []
    for i, outputs in enumerate(output_list):
        predictions = torch.flatten(outputs.logits.argmax(-1)).tolist()
        flattened_boxes = torch.flatten(processed_pages[i]['bbox'], end_dim=-2).tolist()
        flattened_inputs = torch.flatten(processed_pages[i]['input_ids']).tolist()
        flattened_offsets = torch.flatten(processed_pages[i]["offset_mapping"], end_dim=-2).tolist()
        flattened_tokens = tokenizer.convert_ids_to_tokens(flattened_inputs)
        is_subword = np.array(flattened_offsets)[:, 0] != 0

        output_tokens = []
        output_predictions = []
        output_boxes = []
        token = None
        last_pred = None
        last_box = None
        for tkn, pred, box, sub in zip(flattened_tokens, predictions, flattened_boxes, is_subword):
            if tkn in tokenizer.special_tokens_map.values():
                continue
            if not token:
                token = tkn
                last_pred = pred
                last_box = box
                continue
            if sub:
                token += tkn
            else:
                output_predictions.append(last_pred)
                output_tokens.append(token)
                output_boxes.append(last_box)
                token = tkn
                last_pred = pred
                last_box = box
        if token:
            output_predictions.append(last_pred)
            output_tokens.append(token)
            output_boxes.append(last_box)

        true_tokens = [tokenizer.convert_tokens_to_string([tkn]) for tkn in output_tokens]
        true_predictions = [model.config.id2label[pred] for pred in output_predictions]

        output_tokens_list.append(true_tokens)
        output_boxes_list.append(output_boxes)
        output_predictions_list.append(true_predictions)
    return output_tokens_list, output_boxes_list, output_predictions_list


def get_sequences(output_tokens_list, output_boxes_list, output_predictions_list):
    page_sequences = []
    for i, (output_tokens, output_boxes, output_predictions) in enumerate(
            zip(output_tokens_list, output_boxes_list, output_predictions_list)):
        chunked_sequences = []
        sequence = []
        last_label = None
        for j, (token, boxes, pred) in enumerate(zip(output_tokens, output_boxes, output_predictions)):
            if not token:
                continue
            if not last_label:
                last_label = pred
                sequence = [(token, boxes)]
                continue

            if pred != last_label:
                chunked_sequences.append((sequence, last_label))
                sequence = [(token, boxes)]
                last_label = pred
            else:
                sequence.append((token, boxes))
        if sequence:
            chunked_sequences.append((sequence, last_label))
        page_sequences.append(chunked_sequences)
    return page_sequences


def get_relevant_chunks(page, relevant_fields: list[str] = None):
    if relevant_fields is None:
        relevant_fields = ["author", "title", "abstract"]

    return_dict = {k: [] for k in relevant_fields}
    for token_boxes, label in page:
        if label in return_dict:
            tkboxes = [TokenBox(
                token=token,
                box=BoundingBox(
                    x0=box[0],
                    y0=box[1],
                    x1=box[2],
                    y1=box[3],
                )
            ) for token, box in token_boxes]
            chunk = ExtractedChunk(
                segment=tkboxes
            )

            return_dict[label].append(chunk)
    return return_dict
