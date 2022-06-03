import tqdm, json, re, os

import torch
import numpy as np
import pandas as pd
from pathlib import Path

from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'

from transformers import AutoTokenizer, AutoModelForCausalLM

import wandb
import logging

from data import BodyDataset

"""cut the generations"""
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start if start != -1 else None

"""save the excel file"""
def save_xslx(list_dict, dir):
  df = pd.DataFrame(list_dict)
  df.to_excel(dir)
  
def main():
  wandb.init(project="Act2Emo_keywords")
  config = wandb.config

  """Set Config"""
  config.GPT2_MODEL = os.environ.get("GPT2_MODEL", 'skt/kogpt2-base-v2')
  config.DATA_PATH = os.environ.get("DATA_PATH")
  config.OUTPUT_DIR = os.environ.get("OUTPUT_DIR")

  config.OUTPUT_LEN = int(os.environ.get("OUTPUT_LEN", 3))
  config.SEED = int(os.environ.get("SEED", 42))

  config.TOP_K = int(os.environ.get("TOP_K", 1))
  config.TOP_P = int(os.environ.get("TOP_P", 0.9))
  config.NUM_BEAMS = int(os.environ.get("NUM_BEAMS", 10))
  config.NUM_SEQUENCES = int(os.environ.get("NUM_SEQUENCES", 10))
  config.STOP_TOKEN = "."
  
  """set seed"""
  torch.manual_seed(config.SEED) # pytorch random seed
  np.random.seed(config.SEED) # numpy random seed
  torch.backends.cudnn.deterministic = True

  """Set Model"""
  model_name = config.GPT2_MODEL

  tokenizer = AutoTokenizer.from_pretrained(config.GPT2_MODEL)
  model = AutoModelForCausalLM.from_pretrained(config.GPT2_MODEL)
  model.to(device)
  wandb.watch(model, log="all")

  """Download Data"""
  BDdataset = BodyDataset(config.DATA_PATH)
  
  result = list()
  for idx, row in tqdm.tqdm(enumerate(BDdataset)):
    input, prompt, word, cat, subcat = row

    input_ids = tokenizer.encode(input, add_special_tokens=False, return_tensors="pt")

    generations = model.generate(
        input_ids=input_ids.to(device),
        max_length=input_ids.size(1) + config.SUMMARY_LEN,
        temperature=1.0,
        top_k=config.TOP_K,
        top_p=config.TOP_P,
        repetition_penalty=1.0,
        do_sample=True,
        num_return_sequences=config.NUM_SEQUENCES,
        num_beams=config.NUM_BEAMS
    )

    if len(generations.shape) > 2:
      generations.squeeze_()

    text_generations = list()
    
    for gen in generations:
        gen = gen.tolist()
        text = tokenizer.decode(gen, clean_up_tokenization_spaces=True)
        text = text[:find_nth(text, config.STOP_TOKEN, 1)] if config.STOP_TOKEN not in input else text[:find_nth(text, config.STOP_TOKEN, 2)]
        text_generations.append(text)

    result.append({
        "input": input,
        "prompt": prompt,
        "word": word,
        "category": cat,
        "subcategory": subcat,
        "generations": text_generations
        })
    
  output_path = Path(config.OUTPUT_DIR)
  output_path.mkdir(exist_ok = True)

  f_name = '{}-{}-{}-{}-{}.xlsx'.format(re.sub('/','-', config.GPT2_MODEL), 
                                  config.TOP_K,
                                  config.TOP_P,
                                  config.NUM_BEAMS,
                                  config.SUMMARY_LEN)
  
  save_xslx(result, output_path / Path(f_name))

if __name__ == "__main__":
    main()
