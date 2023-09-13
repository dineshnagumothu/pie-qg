import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from scipy.stats import ttest_ind
from scipy.spatial import distance
import statistics
from tqdm import tqdm
import nltk
import os
from tqdm import tqdm
import argparse

model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
print (torch_device)
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

def batcher(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

#setting up the model
def tokenize_sents(input_texts):
  #print (len(input_texts))
  batch = tokenizer(input_texts, truncation=True,padding='longest',max_length=60, return_tensors="pt").to(torch_device)
  #print (batch['input_ids'])
  return batch

def get_response(batch,num_return_sequences):
    translated = model.generate(**batch,max_length=60,num_beams=10, num_return_sequences=num_return_sequences, temperature=1.5)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    #print (tgt_text)
    return_texts = []
    for i in range(len(batch['input_ids'])):
        start_num = num_return_sequences*i
        end_num = num_return_sequences*(i+1)
        sliced_list = tgt_text[start_num:end_num]
        return_texts.append(sliced_list)
    return return_texts

def get_numbers(text, response):
    counter = {}
    text = text.lower().strip()
    words = text.split()
    for word in words:
        if word in counter:
            counter[word][0] += 1
        else:
            counter[word] = [1,0]
  
    response = response.lower().strip()
    words = response.split()
    for word in words:
        if word in counter:
            counter[word][1] += 1
        else:
            counter[word] = [0,1]
    return counter

def calc_ttest(text, response):
    counter = get_numbers(text, response)
    text_list=[]
    resp_list = []
    text_len = len(text.lower().split())
    resp_len = len(response.lower().split())

    for i in counter.keys():
        text_list.append(counter[i][0]/text_len)
        #rel.append(counter[i][0])
        resp_list.append(counter[i][1]/resp_len)
        #irrel.append(counter[i][1])
    stat, p = ttest_ind(text_list, resp_list)
    js = distance.jensenshannon(text_list, resp_list, 2)
    #print (stat, p)
    return (js)

def select_question(batch_text, passages=False):
    batched_model_input = tokenize_sents(batch_text)
    batch_responses = get_response(batched_model_input, 10)
    return_questions = []
    i=0
    for responses in batch_responses:
        all_jsd =[]
        text = batch_text[i]
        i+=1
        for response in responses:
            if(response==""):
                jsd==0
            else:
                jsd = calc_ttest(text, response)
            all_jsd.append(jsd) 
            #print (text)
        final_response = responses[all_jsd.index(max(all_jsd))]
        if(passages==False):
            if(final_response[-1]!="?"):
                final_response = final_response[:-1]+"?"
        return_questions.append(final_response)
    return return_questions

def read_passages_from_file(in_file_name):
    print ("Reading Passages from "+in_file_name)
    passages = []
    with open(in_file_name, 'r') as f:
        for line in f:
            passages.append(line.strip())
    print ("Number of passages :"+str(len(passages)))
    return passages

def read_passages_from_folder(folder_name):
    passages = []
    print ("Reading files from %s" %folder_name)
    for filename in tqdm(os.listdir(folder_name)):
        with open(os.path.join(folder_name, filename), 'r') as f:
            passage = ""
            for line in f:
                passage=passage+ " "+line
            passage = passage.strip()
            passages.append(passage)
    return passages

def write_sentences_to_file(passages, out_file_name):
    print ("Writing Sentences to " + out_file_name)
    with open(out_file_name, 'w') as f:
        for passage in passages:
            f.write("%s\n" % passage)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Paraphrases')
    parser.add_argument('--passage_file', help='File to paraphrase', required=True)
    parser.add_argument('--batch_size', type=int, help='Batch size of the model', default = 16)
    args = parser.parse_args()
    
    #passages = read_passages_from_file("openie6/wiki_refine_corpus.txt")
    data_folder = 'data/'
    passages_filepath = os.path.join(data_folder, args.passage_file)
    passages = read_passages_from_file(passages_filepath)
    paraphrased_passages_filepath = os.path.splitext(passages_filepath)[0]+'_paraphrased.txt' 
    print ("Output file: "+paraphrased_passages_filepath)
    print ("Number of Passages",len(passages)) 

    passages_sents = []
    for passage in passages:
        passage_sentences = nltk.sent_tokenize(passage)
        passages_sents.append(passage_sentences)
    
    #pf_texts = []
    with open(paraphrased_passages_filepath, "a") as file_object:
        for batch_text in tqdm(passages_sents):
            pf_passage = []
            if (len(batch_text)>args.batch_size):
                plen = len(batch_text)
                for ndx in range(0, plen, args.batch_size):
                    new_batch = batch_text[ndx:min(ndx + args.batch_size, plen)]
                    pf_passage.extend(select_question(new_batch,passages=True))
            else:    
                pf_passage.extend(select_question(batch_text,passages=True))
            pf_text = ' '.join(pf_passage)
            pf_text = pf_text.strip()
            file_object.write("%s\n" % pf_text)

        

       
   