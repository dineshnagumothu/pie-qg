import re
import pandas as pd
import argparse
import sys
import nltk
from tqdm import tqdm
import os


from nltk.corpus import stopwords
cstopwords = stopwords.words("english")

def check_passage_sentences(sentences):
    new_sentences = []
    
    for sentence in sentences:
        words = [word for word in sentence.split() if word not in cstopwords]
        repeating = [item for item in set(words) if words.count(item) > 8]
        words_2 = sentence.split('-')
        repeating_2 = [item for item in set(words_2) if words_2.count(item) > 3]
        if(len(repeating)==0 and len(repeating_2)==0):
            new_sentences.append(sentence)
    return new_sentences 

def clean_string(mystring):
    mystring = re.sub(r"\([^()]*\)", "", mystring)
    return re.sub('[^A-Za-z0-9]+', ' ', mystring)
    #return ''.join(e for e in mystring if e.isalnum())

class Triple:
    def __init__(self, subj, rel, obj, text=None, confidence=None):
        self.subj = subj
        self.rel = rel
        self.obj = obj
        self.text = text
        self.confidence = confidence
  
    def __str__(self):
        x=  "Text:"+self.text+"\n"
        x+=  "Confidence:"+str(self.confidence)+"\n"
        x+=  self.subj+" --- "+ self.rel+"--- "+self.obj+"\n---\n"
        return str(x)

def ie6_format(filepath):
    all_triples=[]
    seperator_flag = False
    with open(filepath, "r", encoding="utf-8") as file:
        context_triples = []
        context=""
        for line in file:
            if(line=='\n' or len(line)<=4):
                if(seperator_flag == True):
                  seperator_flag=False;
                  all_triples.append(context_triples)
                  context_triples=[]
            elif ("Dinesh Nagumothu is a PhD student at Deakin University" in line):
                seperator_flag = True
            elif (seperator_flag==True):
                continue
            elif (line[4]==':' and line[:4].replace('.','',1).isdigit()):
                confidence = float(line[:4])       
                triple = line[6:].split(';')
                if(len(triple)<2):
                    continue
                try:
                    triple_text = triple
                    triple[0]=clean_string(triple[0][1:])
                    triple[2]=clean_string(triple[2][:-2])
                    triple[1]=clean_string(triple[1])
                    triple_object = [triple[0], triple[1], triple[2]]

                except:
                    print(triple_text)    
                
                #triple_object = Triple(triple[0], triple[1], triple[2], text=context, confidence=confidence)
                context_triples.append(triple_object)
            else:
                context = line
                #print ("Context")
    print ("Number of items:", len(all_triples))
    
    no_triple_passage_count=0
    for context_triples in all_triples:
        if(len(context_triples)==0):
                no_triple_passage_count+=1
    print ("Number of items without any triples:", no_triple_passage_count)
    '''
    sub_triples = all_triples[:5]
    for triples in sub_triples:
      for triple in triples:
        print (triple)
      print ("----Document End----")
    '''
    return (all_triples)

    ###Formatting triples generated from IE6 Triples
    all_triples=[]
    seperator_flag = False
    with open(filepath, "r", encoding="utf-8") as file:
        context_triples = []
        context=""
        for line in file:
            if(line=='\n' or len(line)<=4):
                if(seperator_flag == True):
                  seperator_flag=False;
                  all_triples.append(context_triples)
                  context_triples=[]
            elif ("Dinesh Nagumothu is a PhD student at Deakin University" in line):
                seperator_flag = True
            elif (seperator_flag==True):
                continue
            elif (line[4]==':' and line[:4].replace('.','',1).isdigit()):
                confidence = float(line[:4])       
                triple = line[6:].split(';')
                if(len(triple)<2):
                    continue
                triple[0]=clean_string(triple[0][1:])
                triple[2]=clean_string(triple[2][:-2])
                triple[1]=clean_string(triple[1])
                #triple_object = Triple(triple[0], triple[1], triple[2], text=context, confidence=confidence)
                triple_object = [triple[0], triple[1], triple[2]]
                context_triples.append(triple_object)
            else:
                context = line
                #print ("Context")
    print ("Number of questions:", len(all_triples))
    
    return (all_triples)  

def convert_triple_to_list(all_triple_objects):
  all_triples = []
  all_confidences = []
  for triple_objects in all_triple_objects:
    context_triples = []
    context_confidences = []
    for triple_object in triple_objects:
      context_triples.append([triple_object.subj, triple_object.rel, triple_object.obj])
      context_confidences.append(triple_object.confidence)
    all_triples.append(context_triples)
    all_confidences.append(context_confidences)
  return all_triples, all_confidences

def convert_to_sentences(passages):
  all_sentences=[]
  sentence_counter = 0
  for i in range(len(passages)):
    passage_sentences = nltk.sent_tokenize(passages[i])
    passage_sentences = check_passage_sentences(passage_sentences)
    all_sentences.append(passage_sentences)
    sentence_counter += len(passage_sentences)
  print ("Total number of Documents", len(all_sentences))
  print ("Total number of Sentences with seperator sentence", sentence_counter)
  return all_sentences

def read_lines_from_text(filename):
  print ("Reading from "+filename)
  lines = []
  with open(filename, 'r') as f:
      for line in f:
        lines.append(line.strip())
  print ("Number of lines: "+str(len(lines)))
  return lines

if __name__=="__main__":
    my_parser = argparse.ArgumentParser(description='Convert Triples to Dataframe for parsing')
    my_parser.add_argument('--filename', help='Name of the dataset', required=True)
    args = my_parser.parse_args()

    triples_file = args.filename
    data_folder = "data/"
    openie6_data_folder = "openie6/data/"

    passages_file = os.path.join(data_folder, args.filename)
    passages = read_lines_from_text(passages_file)

    passage_triples_file_name = os.path.splitext(args.filename)[0]+'_triples.txt'
    passages_triples_file = os.path.join(openie6_data_folder, passage_triples_file_name)
    ie6_passages_triples = ie6_format(passages_triples_file)

    try:
        assert(len(passages)==len(ie6_passages_triples))
    except AssertionError:
        print ("The files are corrupt; Lengths of ids file and text file did not match")
        sys.exit()

    
    out_df = pd.DataFrame()
    out_df['passage'] = passages
    out_df['passage_triples'] = ie6_passages_triples

    out_df_filename = os.path.splitext(args.filename)[0]+'_triples_df.json'
    out_file = os.path.join(data_folder, out_df_filename)
    out_df.to_json(out_file, orient='records', lines=True)
