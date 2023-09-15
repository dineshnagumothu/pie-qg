import nltk
import json
import argparse
import os

def convert_to_sentences(passages):
  all_sentences=[]
  sentence_counter = 0
  actual_sentence_counter = 0
  for i in range(len(passages)):
    passage_sentences = nltk.sent_tokenize(passages[i])
    actual_sentence_counter += len(passage_sentences)
    seperator_sentence = "Dinesh Nagumothu is a PhD student at Deakin University - " + str(i) + "."
    passage_sentences.append(seperator_sentence)
    all_sentences.extend(passage_sentences)
    sentence_counter += len(passage_sentences)
  return all_sentences

def perform_coref(texts):
  print ("Performing Coref")
  import spacy
  #import neuralcoref
  nlp = spacy.load('en_coreference_web_trf')
  #neuralcoref.add_to_pipe(nlp)

  updated_passages = []
  i = 0
  for text in texts:
    doc = nlp(text)
    print (doc.spans)
    for span in doc.spans:
      print (span)
      if 'coref_clusters' in span:
        actual_word = str(doc.spans[span][0])
        pronouns = []
        print ("Actual word:",actual_word)
        for i in range(1,len(doc.spans[span])):
          coref_word = str(doc.spans[span][i])
          if (actual_word.lower()!=coref_word.lower()):
            #print (coref_word)
            start_ix=doc.spans[span][i].start
            end_ix=doc.spans[span][i].end
            print (doc[start_ix:end_ix])
    # word_list = []
    # for token in doc:
    #     word_list.append(token.text_with_ws)
    # for cluster in doc._.coref_clusters:
    #     for mention in cluster.mentions:
    #         replacer = mention._.coref_cluster.main
    #         start_pos = mention.start
    #         end_pos = mention.end
    #         word_list[start_pos: end_pos] = ["[REP]"] * (end_pos-start_pos)
    #         word_list[start_pos] = replacer.text_with_ws
    # word_list = [word for word in word_list if word != "[REP]"]
    # out = "".join(word_list)
    # updated_passages.append(out)
    # i+=1
  return passages

def write_sentences_to_file(sentences, out_file_name):
  print ("Writing Sentences to " + out_file_name)
  with open(out_file_name, 'w') as f:
    for sentence in sentences:
      f.write("%s\n" % sentence)

def read_passages_from_file(in_file_name):
    #print ("Reading Passages from "+in_file_name)
    passages = []
    with open(in_file_name, 'r') as f:
        for line in f:
            passages.append(line.strip())
    #print ("Number of passages :"+str(len(passages)))
    return passages

if __name__=="__main__":
  my_parser = argparse.ArgumentParser(description='Convert Passages to Sentences')
  my_parser.add_argument('--filename', help='Input File Name', required=True)
  my_parser.add_argument('--coref', action='store_true' , help='Flag to perform co-reference resolution')

  args = my_parser.parse_args()
  data_folder = 'data/'
  input_passages_file = os.path.join(data_folder, args.filename)

  passages = read_passages_from_file(input_passages_file)
  print ("Total number of passages in the corpus ", len(passages))

  if(args.coref):
    passages = perform_coref(passages)

  all_passage_sentences = convert_to_sentences(passages)

  output_folder = 'openie6/data/'

  if (os.path.isdir(output_folder)==False):
      os.mkdir(output_folder)
  
  passage_sents_file_name = os.path.splitext(args.filename)[0]+'_sentences.txt'
  passage_sents_file = os.path.join(output_folder, passage_sents_file_name)
  write_sentences_to_file(all_passage_sentences, passage_sents_file)