import json
from transformers.utils import TensorType
from transformers.models.layoutxlm import LayoutXLMProcessor, LayoutXLMTokenizerFast
from transformers.models.layoutlmv2 import LayoutLMv2FeatureExtractor
from transformers.processing_utils import ProcessorMixin
from transformers.tokenization_utils_base import BatchEncoding, PaddingStrategy, PreTokenizedInput, TextInput, TruncationStrategy
from .config import Config
from typing import List, Optional, Union
import os
from fastapi import Response
import zipfile
from io import StringIO
from PIL import Image
import io


config = Config()


# class LayoutXLMProcessor(ProcessorMixin):
#     r"""
#     Constructs a LayoutXLM processor which combines a LayoutXLM feature extractor and a LayoutXLM tokenizer into a
#     single processor.
#     [`LayoutXLMProcessor`] offers all the functionalities you need to prepare data for the model.
#     It first uses [`LayoutLMv2FeatureExtractor`] to resize document images to a fixed size, and optionally applies OCR
#     to get words and normalized bounding boxes. These are then provided to [`LayoutXLMTokenizer`] or
#     [`LayoutXLMTokenizerFast`], which turns the words and bounding boxes into token-level `input_ids`,
#     `attention_mask`, `token_type_ids`, `bbox`. Optionally, one can provide integer `word_labels`, which are turned
#     into token-level `labels` for token classification tasks (such as FUNSD, CORD).
#     Args:
#         feature_extractor (`LayoutLMv2FeatureExtractor`):
#             An instance of [`LayoutLMv2FeatureExtractor`]. The feature extractor is a required input.
#         tokenizer (`LayoutXLMTokenizer` or `LayoutXLMTokenizerFast`):
#             An instance of [`LayoutXLMTokenizer`] or [`LayoutXLMTokenizerFast`]. The tokenizer is a required input.
#     """
#     feature_extractor_class = "LayoutLMv2FeatureExtractor"
#     tokenizer_class = ("LayoutXLMTokenizer", "LayoutXLMTokenizerFast")
#
#     def __call__(
#         self,
#         images,
#         text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None,
#         text_pair: Optional[Union[PreTokenizedInput, List[PreTokenizedInput]]] = None,
#         boxes: Union[List[List[int]], List[List[List[int]]]] = None,
#         word_labels: Optional[Union[List[int], List[List[int]]]] = None,
#         add_special_tokens: bool = True,
#         padding: Union[bool, str, PaddingStrategy] = False,
#         truncation: Union[bool, str, TruncationStrategy] = None,
#         max_length: Optional[int] = None,
#         stride: int = 0,
#         pad_to_multiple_of: Optional[int] = None,
#         return_token_type_ids: Optional[bool] = None,
#         return_attention_mask: Optional[bool] = None,
#         return_overflowing_tokens: bool = False,
#         return_special_tokens_mask: bool = False,
#         return_offsets_mapping: bool = False,
#         return_length: bool = False,
#         verbose: bool = True,
#         return_tensors: Optional[Union[str, TensorType]] = None,
#         **kwargs
#     ) -> BatchEncoding:
#         """
#         This method first forwards the `images` argument to [`~LayoutLMv2FeatureExtractor.__call__`]. In case
#         [`LayoutLMv2FeatureExtractor`] was initialized with `apply_ocr` set to `True`, it passes the obtained words and
#         bounding boxes along with the additional arguments to [`~LayoutXLMTokenizer.__call__`] and returns the output,
#         together with resized `images`. In case [`LayoutLMv2FeatureExtractor`] was initialized with `apply_ocr` set to
#         `False`, it passes the words (`text`/``text_pair`) and `boxes` specified by the user along with the additional
#         arguments to [`~LayoutXLMTokenizer.__call__`] and returns the output, together with resized `images``.
#         Please refer to the docstring of the above two methods for more information.
#         """
#         # verify input
#         if self.feature_extractor.apply_ocr and (boxes is not None):
#             raise ValueError(
#                 "You cannot provide bounding boxes "
#                 "if you initialized the feature extractor with apply_ocr set to True."
#             )
#
#         if self.feature_extractor.apply_ocr and (word_labels is not None):
#             raise ValueError(
#                 "You cannot provide word labels if you initialized the feature extractor with apply_ocr set to True."
#             )
#
#         if return_overflowing_tokens is True and return_offsets_mapping is False:
#             raise ValueError("You cannot return overflowing tokens without returning the offsets mapping.")
#
#         # first, apply the feature extractor
#         features = self.feature_extractor(images=images, return_tensors=return_tensors)
#
#         # second, apply the tokenizer
#         if text is not None and self.feature_extractor.apply_ocr and text_pair is None:
#             if isinstance(text, str):
#                 text = [text]  # add batch dimension (as the feature extractor always adds a batch dimension)
#             text_pair = features["words"]
#
#         encoded_inputs = self.tokenizer(
#             text=text if text is not None else features["words"],
#             text_pair=text_pair if text_pair is not None else None,
#             boxes=boxes if boxes is not None else features["boxes"],
#             word_labels=word_labels,
#             add_special_tokens=add_special_tokens,
#             padding=padding,
#             truncation=truncation,
#             max_length=max_length,
#             stride=stride,
#             pad_to_multiple_of=pad_to_multiple_of,
#             return_token_type_ids=return_token_type_ids,
#             return_attention_mask=return_attention_mask,
#             return_overflowing_tokens=return_overflowing_tokens,
#             return_special_tokens_mask=return_special_tokens_mask,
#             return_offsets_mapping=return_offsets_mapping,
#             return_length=return_length,
#             verbose=verbose,
#             return_tensors=return_tensors,
#             **kwargs,
#         )
#
#         # add pixel values
#         images = features.pop("pixel_values")
#         if return_overflowing_tokens is True:
#             images = self.get_overflowing_images(images, encoded_inputs["overflow_to_sample_mapping"])
#         encoded_inputs["image"] = images
#
#         return encoded_inputs
#
#     def get_overflowing_images(self, images, overflow_to_sample_mapping):
#         # in case there's an overflow, ensure each `input_ids` sample is mapped to its corresponding image
#         images_with_overflow = []
#         for sample_idx in overflow_to_sample_mapping:
#             images_with_overflow.append(images[sample_idx])
#
#         if len(images_with_overflow) != len(overflow_to_sample_mapping):
#             raise ValueError(
#                 "Expected length of images to be the same as the length of `overflow_to_sample_mapping`, but got"
#                 f" {len(images_with_overflow)} and {len(overflow_to_sample_mapping)}"
#             )
#
#         return images_with_overflow
#
#     def batch_decode(self, *args, **kwargs):
#         """
#         This method forwards all its arguments to PreTrainedTokenizer's [`~PreTrainedTokenizer.batch_decode`]. Please
#         refer to the docstring of this method for more information.
#         """
#         return self.tokenizer.batch_decode(*args, **kwargs)
#
#     def decode(self, *args, **kwargs):
#         """
#         This method forwards all its arguments to PreTrainedTokenizer's [`~PreTrainedTokenizer.decode`]. Please refer
#         to the docstring of this method for more information.
#         """
#         return self.tokenizer.decode(*args, **kwargs)
#
#     @property
#     def model_input_names(self):
#         return ["input_ids", "bbox", "attention_mask", "image"]





def iob_to_label(label):
    if not label:
        return 'other'
    return label


def zipfiles(filenames):
    zip_subdir = "archive"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(), mimetype = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


def file_process_in_memory(images: list[Image]):
    """ Converts PIL image objects into BytesIO in-memory bytes buffers. """

    for i, pil_image in enumerate(images):
        file_object = io.BytesIO()
        pil_image.save(file_object, "PNG")
        pil_image.close()
        images[i] = file_object  # Replace PIL image object with BytesIO memory buffer.

    return images  # Return modified list.


def is_list_empty(nested_list):
    if isinstance(nested_list, list):
        return all(map(is_list_empty, nested_list))
    return False
