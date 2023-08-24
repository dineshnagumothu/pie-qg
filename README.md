# PIE-QG: Paraphrased Information Extraction for Unsupervised Question Generation from Small Corpora

# Abstract
Supervised Question Answering (QA) systems rely on domain-specific human-labeled data for training. Unsupervised QA systems generate their own question-answer training pairs, typically using secondary knowledge sources to achieve this outcome. Our approach (called PIE-QG) uses Open Information Extraction (OpenIE) to generate synthetic training questions from paraphrased passages and uses the question-answer pairs as training data for a language model for a state-of-the-art QA system based on BERT. Triples in the form of <subject, predicate, object> are extracted from each passage, and questions are formed with subjects (or objects) and predicates while objects (or subjects) are considered as answers. Experimenting on five extractive QA datasets demonstrates that our technique achieves on-par performance with existing state-of-the-art QA systems with the benefit of being trained on an order of magnitude fewer documents and without any recourse to external reference data sources.

# Instructions to run the code
<ol>
  <li><b>Create environments</b></li>

  This step creates separate environments for OpenIE6 and for HuggingFace ransformers. (Single environment setup will not work because of conflicting packages)
  
  ```
  sh setup.sh
  ```

  <li><b>Paraphrase passages, extract triples and generate Questions</b></li>

  This step paraphrases the passages, prepares the data for OpenIE6, extracts semantic triples from passages and generates synthetic training questions, and saves them to disk. 

  You can edit the settings in the bash file to define the number of GPUs ```NUM_GPUS``` to use.
  
  ```
  sh question_generation.sh
  ```

  <li><b>Train extractive QA models with synthetic training data and evaluate with standard datasets</b></li>

  This step trains and measures the performance of the extractive QA model with cross-encoder architecture and answer-span prediction

  Feel free to experiment with different language models, and change ```MODEL_NAME``` to any HuggingFace encoder models. This work experiments with BERT-base ```bert-base-uncased``` and BERT-large-whole-word-masking ```bert-large-uncased-whole-word-masking```.  
  
  ```
  sh train.sh
  ```
</ol>

## CITE

If you use this research, please cite us at

    @inproceedings{nagumothu-etal-2022-pie,
    title = "{PIE}-{QG}: Paraphrased Information Extraction for Unsupervised Question Generation from Small Corpora",
    author = "Nagumothu, Dinesh  and
      Ofoghi, Bahadorreza  and
      Huang, Guangyan  and
      Eklund, Peter",
    booktitle = "Proceedings of the 26th Conference on Computational Natural Language Learning (CoNLL)",
    month = dec,
    year = "2022",
    address = "Abu Dhabi, United Arab Emirates (Hybrid)",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.conll-1.24",
    doi = "10.18653/v1/2022.conll-1.24",
    pages = "350--359",
}
