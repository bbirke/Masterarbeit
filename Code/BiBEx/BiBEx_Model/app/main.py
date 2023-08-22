import logging
from logging.config import dictConfig

import fitz
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tokenizers.pre_tokenizers import WhitespaceSplit
from transformers import AutoTokenizer, pipeline, AutoModelForTokenClassification
from transformers.models.layoutxlm import LayoutXLMTokenizerFast

from .body import *
from .config import LogConfig, Config
from .processing.author_model import NERPipeline, get_authors, segment_author
from .processing.document_model import get_processor
from .processing.document_model import process_images, predict, get_sequences, get_relevant_chunks
from .processing.image import get_token_boxes, get_images, read_images
from .processing.reference_model import get_pre_tokenizer, dehyphen_references, dehyphen_reference_str
from .utils import is_list_empty

description = """
The BiBEx API helps you to extract metadata from scientific publications.
"""

app = FastAPI(
    title="BiBEx API",
    description=description,
    version="1.0.0",
    contact={
        "name": "Geographische Netzwerkstatt",
        "url": "https://geographische-netzwerkstatt.uni-passau.de/",
        "email": "geographische-netzwerkstatt@uni-passau.de",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models = {}

config = Config()

dictConfig(LogConfig().dict())
logger = logging.getLogger("doc_seg_logger")

device = "cuda" if torch.cuda.is_available() else "cpu"


@app.on_event("startup")
async def startup_event():
    logger.info("Loading Reference Segmentation Model.")
    tokenizer_ref_seg = AutoTokenizer.from_pretrained(config.get_conf_value("Paths", "PathModelRefSeg"),
                                                      trust_remote_code=True)
    tokenizer_ref_seg.pre_tokenizer = get_pre_tokenizer()
    classifier_ref_seg = pipeline(model=config.get_conf_value("Paths", "PathModelRefSeg"), tokenizer=tokenizer_ref_seg,
                                  trust_remote_code=True, split_tokens=True)
    models["ref_seg_model"] = classifier_ref_seg

    logger.info("Loading Document Segmentation Model.")
    tokenizer_doc_ext = LayoutXLMTokenizerFast.from_pretrained(config.get_conf_value("Paths", "PathModelDocExt"),
                                                               trust_remote_code=True)
    model_doc_ext = AutoModelForTokenClassification.from_pretrained(config.get_conf_value("Paths", "PathModelDocExt"))
    models["doc_ext_tokenizer"] = tokenizer_doc_ext
    models["doc_ext_model"] = model_doc_ext

    logger.info("Loading NER Model.")

    tokenizer_ner = AutoTokenizer.from_pretrained(config.get_conf_value("Paths", "PathModelNER"),
                                                  trust_remote_code=True)
    model_ner = AutoModelForTokenClassification.from_pretrained(config.get_conf_value("Paths", "PathModelNER"))
    classifier_ner = NERPipeline(model=model_ner, tokenizer=tokenizer_ner)
    models["ner_model"] = classifier_ner
    models["ner_tokenizer"] = tokenizer_ner


@app.post("/process/pdf/", response_model=ExtractedSegments)
async def segment_document(
        file: UploadFile = File(content_type='application/pdf', description='Extract metadata from a publication.'),
        ocr: bool | None = False,
        ocr_lang: str | None = "deu",
        title_page: int | None = 0,
):
    """
    Extracts metadata from scientific publication, provided as a PDF file.<br/>
    Attempts to extract authors, title, abstract, and references from the document.<br/>
    The following query parameters are available:

    - **ocr**: Apply OCR on your PDF file.
    - **ocr_lang**: The language of your document.
    - **title_page**: Select the title page of your document.
    """
    accepted_langs = config.get_conf_value("AcceptedLanguages").values()
    if ocr_lang not in accepted_langs:
        raise HTTPException(status_code=422, detail=f"Query param {ocr_lang} not supported.")
    try:
        doc = fitz.open("pdf", file.file.read())
    except Exception:
        raise HTTPException(status_code=422, detail="There was an error uploading the file")
    finally:
        file.file.close()

    dpi = config.get_conf_value("OCR", "dpi_ocr") if ocr else config.get_conf_value("OCR", "dpi_default")
    dpi = int(dpi)
    images = get_images(doc, dpi)
    if (title_page >= len(images)) or (title_page < 0):
        raise HTTPException(status_code=422, detail="No valid title page parameter.")

    tokens = []
    bboxes = []
    if not ocr:
        tokens, bboxes = get_token_boxes(doc)

    if is_list_empty(tokens) and not ocr:
        raise HTTPException(status_code=422, detail="Could not extract text from the uploaded PDF file.")

    processor = get_processor(apply_ocr=ocr, ocr_lang=ocr_lang)

    processed_pages = process_images(images, processor, ocr=ocr, tokens=tokens, bboxes=bboxes)

    output_tokens_list, output_boxes_list, output_predictions_list = predict(processed_pages, models["doc_ext_model"],
                                                                             models["doc_ext_tokenizer"])

    page_sequences = get_sequences(output_tokens_list, output_boxes_list, output_predictions_list)

    selected_page = page_sequences[title_page]

    title_page_extraction_dict = get_relevant_chunks(selected_page)

    recognized_authors = get_authors(title_page_extraction_dict["author"], models["ner_model"], models["ner_tokenizer"])
    references = []
    fallback_authors = title_page_extraction_dict["author"]
    fallback_abstracts = []
    fallback_titles = []
    for i, page in enumerate(page_sequences):

        if i != title_page:
            page_extraction_dict = get_relevant_chunks(page)
            fallback_authors += page_extraction_dict["author"]
            fallback_titles += page_extraction_dict["title"]
            fallback_abstracts += page_extraction_dict["abstract"]

        for token_boxes, label in page:
            if label == 'reference':
                references += token_boxes

    dehyphen_reference_string = dehyphen_references(references)

    ref_entities = []
    n_references = 0
    if references:
        output = models["ref_seg_model"](dehyphen_reference_string)
        for r, ref in enumerate(output["references"]):
            entities = []
            reference_raw = ref["reference_raw"]
            for e, entity in enumerate(ref["entities"]):
                word = entity["word"]
                subtype = None
                if entity["entity_group"] == "author" or entity["entity_group"] == "editor":
                    author_dict = segment_author(word)
                    if author_dict:
                        subtype = Author(
                            first_name=author_dict["first"],
                            middle_name=author_dict["middle"],
                            surname=author_dict["last"],
                        )
                word = SegmentedWord(
                    raw=word,
                    segmented=subtype
                )
                entity_group = ReferenceEntity(
                    entity_id=e,
                    entity_group=entity["entity_group"],
                    score=float(entity["score"]),
                    word=word,
                )
                entities.append(entity_group)
            group = ReferenceEntityGroup(
                reference_id=r,
                reference_string=reference_raw,
                reference=entities
            )
            ref_entities.append(group)
            n_references = output["number_of_references"]
    seg_ref = SegmentedReference(number_of_references=n_references, references=ref_entities)
    return ExtractedSegments(
        authors=recognized_authors,
        titles=title_page_extraction_dict["title"],
        abstracts=title_page_extraction_dict["abstract"],
        fallback_authors=fallback_authors,
        fallback_titles=fallback_titles,
        fallback_abstracts=fallback_abstracts,
        segmented_references=seg_ref
    )


@app.post("/process/images/", response_model=ExtractedSegments)
async def segment_images(
        file: list[UploadFile] = File(description='Extract metadata from a publication.'),
        ocr_lang: str | None = "deu",
        title_page: int | None = 0,
):
    """
    Extracts metadata from scientific publication, provided as image files.<br/>
    Attempts to extract authors, title, abstract, and references from the document.<br/>
    The following query parameters are available:

    - **ocr_lang**: The language of your document.
    - **title_page**: Select the title page of your document.
    """
    accepted_langs = config.get_conf_value("AcceptedLanguages").values()
    if ocr_lang not in accepted_langs:
        raise HTTPException(status_code=422, detail=f"Query param {ocr_lang} not supported.")

    images = read_images(file)

    if (title_page >= len(images)) or (title_page < 0):
        raise HTTPException(status_code=422, detail="No valid title page parameter.")

    ocr = True
    processor = get_processor(apply_ocr=ocr, ocr_lang=ocr_lang)

    processed_pages = process_images(images, processor, ocr=ocr)

    output_tokens_list, output_boxes_list, output_predictions_list = predict(processed_pages, models["doc_ext_model"],
                                                                             models["doc_ext_tokenizer"])

    page_sequences = get_sequences(output_tokens_list, output_boxes_list, output_predictions_list)

    selected_page = page_sequences[title_page]

    title_page_extraction_dict = get_relevant_chunks(selected_page)

    recognized_authors = get_authors(title_page_extraction_dict["author"], models["ner_model"], models["ner_tokenizer"])
    references = []
    fallback_authors = title_page_extraction_dict["author"]
    fallback_abstracts = []
    fallback_titles = []
    for i, page in enumerate(page_sequences):

        if i != title_page:
            page_extraction_dict = get_relevant_chunks(page)
            fallback_authors += page_extraction_dict["author"]
            fallback_titles += page_extraction_dict["title"]
            fallback_abstracts += page_extraction_dict["abstract"]

        for token_boxes, label in page:
            if label == 'reference':
                references += token_boxes
    ref_boxes = [box for ref, box in references]
    spliter = WhitespaceSplit()
    reference_string = ' '.join([ref for ref, box in references])
    split_tokens = spliter.pre_tokenize_str(reference_string)
    pos2box = {start: ref_boxes[i] for i, (tk, (start, end)) in enumerate(split_tokens)}
    ref_entities = []
    n_references = 0
    if references:
        output = models["ref_seg_model"](reference_string)
        for r, ref in enumerate(output["references"]):
            entities = []
            reference_raw = ref["reference_raw"]
            for e, entity in enumerate(ref["entities"]):
                start = int(entity["start"])
                end = int(entity["end"])
                bboxes = []
                for i in range(start, end):
                    if i in pos2box:
                        box = pos2box[i]
                        bbox = BoundingBox(
                            x0=box[0],
                            y0=box[1],
                            x1=box[2],
                            y1=box[3],
                        )
                        bboxes.append(bbox)
                word = entity["word"]
                subtype = None
                if entity["entity_group"] == "author" or entity["entity_group"] == "editor":
                    author_dict = segment_author(word)
                    if author_dict:
                        subtype = Author(
                            first_name=author_dict["first"],
                            middle_name=author_dict["middle"],
                            surname=author_dict["last"],
                        )
                word = SegmentedWord(
                    raw=word,
                    segmented=subtype
                )
                entity_group = ReferenceEntity(
                    entity_id=e,
                    entity_group=entity["entity_group"],
                    score=float(entity["score"]),
                    word=word,
                )
                entities.append(entity_group)
            group = ReferenceEntityGroup(
                reference_id=r,
                reference_string=reference_raw,
                reference=entities
            )
            ref_entities.append(group)
            n_references = output["number_of_references"]
    seg_ref = SegmentedReference(number_of_references=n_references, references=ref_entities)
    return ExtractedSegments(
        authors=recognized_authors,
        titles=title_page_extraction_dict["title"],
        abstracts=title_page_extraction_dict["abstract"],
        fallback_authors=fallback_authors,
        fallback_titles=fallback_titles,
        fallback_abstracts=fallback_abstracts,
        segmented_references=seg_ref
    )


@app.post("/process/references/", response_model=SegmentedReference)
async def segment_references(ref: Reference):
    """
    Extracts metadata from a reference string.<br/>
    Multiple references can be pasted. The model tries to segment your input data.
    """
    text = ref.text
    dehyphen_text = dehyphen_reference_str(text)
    output = models["ref_seg_model"](dehyphen_text)
    ref_entities = []
    for r, ref in enumerate(output["references"]):
        entities = []
        reference_raw = ref["reference_raw"]
        for e, entity in enumerate(ref["entities"]):
            word = entity["word"]
            subtype = None
            if entity["entity_group"] == "author" or entity["entity_group"] == "editor":
                author_dict = segment_author(word)
                if author_dict:
                    subtype = Author(
                        first_name=author_dict["first"],
                        middle_name=author_dict["middle"],
                        surname=author_dict["last"],
                    )
            word = SegmentedWord(
                raw=word,
                segmented=subtype
            )
            entity_group = ReferenceEntity(
                entity_id=e,
                entity_group=entity["entity_group"],
                score=float(entity["score"]),
                word=word,
            )
            entities.append(entity_group)
        group = ReferenceEntityGroup(
            reference_id=r,
            reference_string=reference_raw,
            reference=entities
        )
        ref_entities.append(group)
    response_model = SegmentedReference(number_of_references=output["number_of_references"], references=ref_entities)
    return response_model
