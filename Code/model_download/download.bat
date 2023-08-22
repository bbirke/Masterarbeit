@echo off
if not exist .\DocumentSegmentationModel\ (
  echo Cloning Document Segmentation Model...
  git clone https://huggingface.co/GEOcite/DocumentSegmentationModel
) else (
  echo Document Segmentation Model found.
)
if not exist .\ReferenceParserModel\ (
  echo Cloning Reference Parser Model...
  git clone https://huggingface.co/GEOcite/ReferenceParserModel
) else (
  echo Reference Parser Model found.
)
if not exist .\AuthorParserModel\ (
  echo Cloning Author Parser Model...
  git clone https://huggingface.co/GEOcite/AuthorParserModel
) else (
  echo Author Parser Model found.
)