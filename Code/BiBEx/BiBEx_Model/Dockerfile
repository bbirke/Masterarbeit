#
FROM python:3.10

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

# Install required packages
RUN apt-get update
RUN apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu tesseract-ocr-fra tesseract-ocr-spa poppler-utils git-lfs

# install python packages
# tested with detectron2 v 0.6
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git@v0.6'

#
COPY ./app /code/app
COPY ./resources /code/resources

#
RUN git lfs install
RUN git clone https://huggingface.co/GEOcite/DocumentSegmentationModel /code/resources/models/DocumentSegmentationModel
RUN git clone https://huggingface.co/GEOcite/ReferenceParserModel /code/resources/models/ReferenceParserModel
RUN git clone https://huggingface.co/GEOcite/AuthorParserModel /code/resources/models/AuthorParserModel

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]