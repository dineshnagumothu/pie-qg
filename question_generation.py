import pandas as pd
import sys
import spacy
nlp = spacy.load('en_core_web_trf')
import argparse
import os

class Question_Answer:
    def __init__(self, question, context, answer, answer_start=0, triple = []):
        self.question = question
        self.context = context
        self.answer = answer
        self.answer_start = context.find(answer)
        self.triple = triple
  
    def __str__(self):
        x= "Question: "+ self.question+"\n"
        #x+= "Context: "+self.context+"\n"
        x+= "Answer: "+self.answer+"\n"
        #x+= "Answer start: "+str(self.answer_start)+"\n"
        return str(x)

class Triple:
    def __init__(self, subj, rel, obj, text=None):
        self.subj = subj
        self.rel = rel
        self.obj = obj
        self.text = text
  
    def __str__(self):
        x=  "Text:"+self.text+"\n"
        x+=  self.subj+" --- "+ self.rel+"--- "+self.obj+"\n---\n"
        return str(x)
    
def ne_question_formation(named_entity):
    if (named_entity=="GPE"):
        return "In what"
    elif (named_entity=="PERSON"):
        return "Who was"
    elif (named_entity=="CARDINAL" or named_entity=="QUANTITY"):
        return "How many" 
    elif (named_entity=="DATE"):
        return "When did" 
    elif (named_entity=="EVENT"):
        return "What event" 
    elif (named_entity=="FAC"):
        return "What is" 
    elif (named_entity=="MONEY"):
        return "How much"
    elif (named_entity=="PERCENT"):
        return "What percentage"
    elif (named_entity=="LANGUAGE"):
        return "What language"
    elif (named_entity=="LAW"):
        return "What law"
    elif (named_entity=="LOC"):
        return "What is"
    elif (named_entity=="ORDINAL"):
        return "Where does"
    elif (named_entity=="PRODUCT" or named_entity=="WORK_OF_ART"):
        return "What was"
    elif (named_entity=="TIME"):
        return "How long"
    else:
        return "What"

def extract_named_entities(document):
    nlp_doc = nlp(document)
    named_entities = {}
    for ent in nlp_doc.ents:
        named_entities[ent.text]=ent.label_
    return named_entities

def create_questions(context, triple, named_entities):
    questions = []

    if(triple.subj in context):
        if(triple.subj in named_entities.keys()):
            #print (named_entities[triple[0]])
            ne_0 = ne_question_formation(named_entities[triple.subj])
            question = ne_0+" "+triple.rel+" "+triple.obj
        else:
            ##Canberra - is the capital of  - Australia
            ##What is the capital of Australia?
            #Dinesh - Went to - India -  Who went to India?
            ##Dinesh - Went - last Year - Who went last year?
            ##Who went to India last year?
            question = "What"+" "+ triple.rel+" "+triple.obj
        question=question.strip()
        question = question+"?"
        
        qa = Question_Answer(question, context, triple.subj, triple = [triple.subj, triple.rel, triple.obj])
        questions.append (qa)

    if(triple.obj in context):
        if(triple.obj in named_entities.keys()):
            #print (named_entities[triple[2]])
            ne_1 = ne_question_formation(named_entities[triple.obj])
            question = ne_1+" "+triple.subj+" "+triple.rel
        else:
            question = "What"+" "+ triple.subj+" "+triple.rel
        question=question.strip()
        question = question+"?"
        qa = Question_Answer(question, context, triple.obj, triple = [triple.subj, triple.rel, triple.obj])
        questions.append(qa)
    return questions

def get_index_positions(list_of_elems, element):
    ''' Returns the indexes of all occurrences of give element in
    the list- listOfElements '''
    index_pos_list = []
    for i in range(len(list_of_elems)):
        if list_of_elems[i] == element:
            index_pos_list.append(i)
    return index_pos_list

def get_triple_objects_as_list(triples):
    list_triple = []
    for triple in triples:
        list_triple.append([triple.subj,triple.rel,triple.obj])
    return list_triple
        

def form_merged_questions(context, triples, named_entities):
    answer = triples[0].subj
    question_text = ne_question_formation(named_entities[answer])+" "
    for triple in triples:
        question_text+=triple.rel+" "+ triple.obj+", "    
    question_text = question_text.strip()
    question_text=question_text[:-1]
    question_text += "?"
    qa = Question_Answer(question_text, context, answer, triple=get_triple_objects_as_list(triples))
    return qa

def question_generate(text,triples):
    named_entities = extract_named_entities(text)
    question_texts=[]
    answer_texts=[]
    final_questions=[]
    
    for i in range(len(triples)):
        if(triples[i].subj==triples[i].obj):
            del triples[i]
    
    all_subjects = []
    unique_subjects = []
    multi_subject_flag = [-1]*len(triples)
    
    for i in range(len(triples)):
        #print (triples[i])
        all_subjects.append(triples[i].subj)
        if(triples[i].subj not in unique_subjects):
            unique_subjects.append(triples[i].subj)
            
    counter=0
    for subject in unique_subjects:
        rep_list = get_index_positions(all_subjects, subject)
        #print (rep_list)
        if(len(rep_list)>1):
            merging_triples = []
            #print ("merging_triples")
            for item in rep_list:
                merging_triples.append(triples[item])
                multi_subject_flag[item]=counter
            #print (merging_triples)
            qa = form_merged_questions(context, merging_triples, named_entities)
            final_questions.append(qa)
        counter+=1
        
    final_triples = []
    for i in range(len(multi_subject_flag)):
        if multi_subject_flag[i]==-1:
            final_triples.append(triples[i])
    #print (final_triples)
    
    triples = final_triples
    
    for triple in triples:
        if(triple.subj !="" and triple.obj!=""): 
          questions = create_questions(text,triple, named_entities)
          for qa in questions:
            if (qa.question not in question_texts or qa.answer not in answer_texts):
              question_texts.append(qa.question)
              answer_texts.append(qa.answer)
              final_questions.append(qa)
    return final_questions

import re
def clean_string(mystring):
    mystring = re.sub(r"\([^()]*\)", "", mystring)
    return re.sub('[^A-Za-z0-9]+', ' ', mystring)
    #return ''.join(e for e in mystring if e.isalnum())

def create_df_from_questions(questions):
  questions_list = []
  answers_list = []
  contexts_list = []
  answer_start_list = []
  triples = []

  for question in questions:
    questions_list.append(question.question)
    answers_list.append(question.answer)
    contexts_list.append(question.context)
    answer_start_list.append(question.answer_start)
    triples.append(question.triple)

  questions_df = pd.DataFrame()
  questions_df['Question']=questions_list
  questions_df['Answer']=answers_list
  questions_df['Context']=contexts_list
  questions_df['Answer_start']=answer_start_list
  questions_df['triple']=triples
  return questions_df

def filter_topics_nes(text,triples):
    named_entities = extract_named_entities(text)
    return_triples=[]
    for triple in triples:
        if(triple[0] in named_entities.keys() or triple[2] in named_entities.keys()):
            return_triples.append(triple)
    return return_triples

def remove_substring_duplicates(triples):
  triple_texts = []
  for triple in triples:
    triple_text = triple[0].strip()+" "+triple[1].strip()+" "+triple[2].strip()
    triple_texts.append(triple_text)

  for j in range(len(triple_texts)):
    for k in range(len(triple_texts)):
      if(triple_texts[j] in triple_texts[k] and triple_texts[j]!=triple_texts[k]):
          triple_texts[j] = '[REM]'

  ids = [i for i,d in enumerate(triple_texts) if d == '[REM]']

  #print (ids)
  return_triples = []
  for i in range(len(triples)):
    if i not in ids:
      return_triples.append(triples[i])

  return return_triples


if __name__ == "__main__":
  my_parser = argparse.ArgumentParser(description='Generate Questions')
  my_parser.add_argument('--input', help='Name of the file to read passages and triples', required=True)
  my_parser.add_argument('--output', help='Name of the file to write generated questions', required=True)
  my_parser.add_argument('--filter_substring', action='store_true' , help='Flag to filter substring')
  my_parser.add_argument('--filter_ne', action='store_true' , help='Flag to filter named entities')
  args = my_parser.parse_args()

  data_folder = 'data/'
  input_file = os.path.join(data_folder,args.input)
  triple_contexts_df = pd.read_json(input_file, orient='records', lines=True)
  print ("Number of passages", len(triple_contexts_df))
  all_qa_pairs = []
  for i in range(len(triple_contexts_df)):
    context = triple_contexts_df['passage'].iloc[i]
    triples = triple_contexts_df['passage_triples'].iloc[i]
    if(args.filter_ne):
        triples = filter_topics_nes(context,triples)
    if(args.filter_substring):
        triples = remove_substring_duplicates(triples)
    ctx_triples = []
    for triple in triples:
      triple_object=Triple(triple[0].strip(), triple[1].strip(), triple[2].strip(), text=context)
      ctx_triples.append(triple_object)
    ctx_qa_pairs = question_generate(context, ctx_triples)
    all_qa_pairs.extend(ctx_qa_pairs)
    print (str(i)+" Passages processed", end="\r")
  print ("Question Generation Finished")
  all_questions_dataframe = create_df_from_questions(all_qa_pairs)
  print (all_questions_dataframe.head())
  print ("Number of Questions Generated", len(all_questions_dataframe))

  data_folder = 'data/'
  out_file = os.path.join(data_folder,args.output)
  all_questions_dataframe.to_json(out_file, orient='records', lines=True)


