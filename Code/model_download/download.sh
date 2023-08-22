if [ -d "./DocumentSegmentationModel/" ]; then
   echo "Document Segmentation Model found."
else
   echo "Cloning Document Segmentation Model..."
   git clone https://huggingface.co/GEOcite/DocumentSegmentationModel
fi

if [ -d "./ReferenceParserModel/" ]; then
   echo "Reference Parser Model found."
else
   echo "Cloning Reference Parser Model..."
   git clone https://huggingface.co/GEOcite/ReferenceParserModel
fi

if [ -d "./AuthorParserModel/" ]; then
   echo "Author Parser Model found."
else
   echo "Cloning Author Parser Model..."
   git clone https://huggingface.co/GEOcite/AuthorParserModel
fi