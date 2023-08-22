# coding=utf-8
import csv
import os

import datasets

from PIL import Image

logger = datasets.logging.get_logger(__name__)


_CITATION = """
nothing
"""
_DESCRIPTION = """\
test
"""

def load_image(image_path):
    image = Image.open(image_path).convert("RGB")
    w, h = image.size
    return image, (w, h)

def normalize_bbox(bbox, size):
    return [
        int(1000 * bbox[0] / size[0]),
        int(1000 * bbox[1] / size[1]),
        int(1000 * bbox[2] / size[0]),
        int(1000 * bbox[3] / size[1]),
    ]

class DocBankConfig(datasets.BuilderConfig):
    """BuilderConfig for DocBank"""

    def __init__(self, **kwargs):
        """BuilderConfig for DocBank.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(DocBankConfig, self).__init__(**kwargs)

class DocBank(datasets.GeneratorBasedBuilder):
    """DocBank dataset."""

    BUILDER_CONFIGS = [
        DocBankConfig(name="docbank", version=datasets.Version("1.0.0"), description="DocBank dataset"),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "id": datasets.Value("string"),
                    "words": datasets.Sequence(datasets.Value("string")),
                    "bboxes": datasets.Sequence(datasets.Sequence(datasets.Value("int64"))),
                    "token_labels": datasets.Sequence(
                        datasets.features.ClassLabel(
                            names=['abstract','author','caption','date','equation','figure','footer','list','paragraph','reference','section','table','title']
                        )
                    ),
                    "image_path": datasets.Value("string"),
                }
            ),
            supervised_keys=None,
            homepage="none",
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        logger.info("Before DL")
        downloaded_file = dl_manager.download_and_extract("https://huggingface.co/datasets/MrPotato/docbank_small/resolve/main/dataset.zip")
        logger.info("After DL")
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN, gen_kwargs={"data-file": f"{downloaded_file}/train/"}
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST, gen_kwargs={"data-file": f"{downloaded_file}/test/"}
            ),
        ]

    def _generate_examples(self, filepath):
        logger.info("⏳ Generating examples from = %s", filepath)
        ann_dir = os.path.join(filepath, "txt")
        img_dir = os.path.join(filepath, "img")
        for guid, file in enumerate(sorted(os.listdir(ann_dir))):
            words = []
            bboxes = []
            token_labels = []
            #file_path = os.path.join(ann_dir, file)
            data = []
            with open('db_test.txt', newline='\n', encoding='utf-8') as csvfile:
                spamreader = csv.reader(csvfile, delimiter='\t', quotechar='\"')
                for row in spamreader:
                    data.append(row)
            image_path = os.path.join(img_dir, file)
            image_path = image_path.replace(".txt", "_ori.jpg")
            image, size = load_image(image_path)
            for item in data:
                words_example, label = item[0], item[-1]
                #words_example = [w for w in words_example if w["text"].strip() != ""]
                if len(words_example) == 0:
                    continue
                # if label == "other":
                #     for w in words_example:
                #         words.append(w["text"])
                #         ner_tags.append("O")
                #         bboxes.append(normalize_bbox(w["box"], size))
                else:
                    words.append(words_example)
                    token_labels.append(label)
                    bboxes.append(normalize_bbox([int(item[1]), int(item[2]), int(item[3]), int(item[4])], size))
            yield guid, {"id": str(guid), "words": words, "bboxes": bboxes, "ner_tags": token_labels, "image_path": image_path}