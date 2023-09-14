#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate question_generation

PASSAGE_FILE="wikicorpus"

# #Paraphrase passages
PASSAGE_FILE_EXT="${PASSAGE_FILE}.txt"
python paraphrase.py --passage_file $PASSAGE_FILE_EXT

#Convert paraphrased passages to sentences
PARAPHRASED_PASSAGE_FILE="${PASSAGE_FILE}_paraphrased.txt"
python convert_to_sentences.py --filename $PARAPHRASED_PASSAGE_FILE

#Triple extraction

eval "$(conda shell.bash hook)"
conda activate triple
cd openie6

PARAPHRASED_SENTENCES_FILE="data/${PASSAGE_FILE}_paraphrased_sentences.txt"
PARAPHRASED_TRIPLE_FILE="data/${PASSAGE_FILE}_triples.txt"
NUM_GPUS=0

python run.py --mode splitpredict --inp $PARAPHRASED_SENTENCES_FILE --out $PARAPHRASED_TRIPLE_FILE --rescoring --task oie --gpus $NUM_GPUS --oie_model models/oie_model/epoch=14_eval_acc=0.551_v0.ckpt --conj_model models/conj_model/epoch=28_eval_acc=0.854.ckpt --rescore_model models/rescore_model --num_extractions 5 

#Form passages and triples as dataframes 
cd ..
eval "$(conda shell.bash hook)"
conda activate question_generation

python triples_to_df.py --filename $PASSAGE_FILE_EXT

#Generate Questions
TRIPLES_DF_FILE="${PASSAGE_FILE}_triples_df.json"
OUTPUT_QUESTION_FILE="${PASSAGE_FILE}_questions.json"
python question_generation.py --input $TRIPLES_DF_FILE --output $OUTPUT_QUESTION_FILE --filter_substring --filter_ne
