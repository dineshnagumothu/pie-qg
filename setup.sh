#!/bin/bash

# conda create -n triple python=3.6
# conda activate triple
# conda init bash

# cd openie6

# pip install -r requirements.txt
# python -m nltk.downloader stopwords
# python -m nltk.downloader punkt 
# pip install --upgrade gevent

# python -m zenodo_get 4054476
# tar -xvf openie6_data.tar.gz

# python -m zenodo_get 4055395
# tar -xvf openie6_models.tar.gz

# cd ..

conda create -n question_generation python=3.8
conda activate question_generation
conda init bash

pip install -r requirements.txt
python -m spacy download en_core_web_trf

