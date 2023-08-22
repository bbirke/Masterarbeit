from fitz import Document, Matrix, Rect
from PIL import Image
import io


def get_images(doc: Document, dpi: int) -> list[Image]:
    zoom = int(dpi) / 72  # zoom factor, standard: 72 dpi
    magnify = Matrix(zoom, zoom)  # magnifies in x, resp. y direction
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=magnify)  # render page to an image
        img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        images.append(img)
    return images


def read_images(images):
    return [Image.open(io.BytesIO(image_data.file.read())).convert("RGB") for image_data in images]


def unnormalize_box(bbox, width, height):
    return [
        width * (bbox[0] / 1000),
        height * (bbox[1] / 1000),
        width * (bbox[2] / 1000),
        height * (bbox[3] / 1000),
    ]


def normalize_box(box, width, height):
    return [
        int(1000 * (box[0] / width)),
        int(1000 * (box[1] / height)),
        int(1000 * (box[2] / width)),
        int(1000 * (box[3] / height)),
    ]


def get_token_boxes(doc: Document) -> tuple[list[list[str]], list[list[int, int, int, int]]]:
    tokens = []
    bboxes = []
    for page in doc:
        x = page.rect[2]
        y = page.rect[3]
        bboxes_page = []
        tokens_page = []
        for x0, y0, x1, y1, word, block_no, line_no, word_no in page.get_text("words"):
            # sanitized_word = bytes(word, 'ISO-8859-1', 'ignore').decode('ISO-8859-1', 'ignore')
            sanitized_word = word
            if sanitized_word:
                tokens_page.append(sanitized_word)
                bboxes_page.append(normalize_box([x0, y0, x1, y1], x, y))
        tokens.append(tokens_page)
        bboxes.append(bboxes_page)
    return tokens, bboxes
