import torch
import numpy as np
import pandas as pd
from pathlib import Path
import tqdm, json, re

from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'

from transformers import AutoTokenizer, AutoModelForCausalLM
from data import BodyDataset



"""cut the generations"""
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start if start != -1 else None


def main(args):  
  """set seed"""
  torch.manual_seed(args.SEED) # pytorch random seed
  np.random.seed(args.SEED) # numpy random seed
  torch.backends.cudnn.deterministic = True

  """Set Model"""
  model_name = args.GPT2_MODEL

  tokenizer = AutoTokenizer.from_pretrained(args.GPT2_MODEL)
  model = AutoModelForCausalLM.from_pretrained(args.GPT2_MODEL)
  model.to(device)

  """Download Data"""
  BDdataset = BodyDataset(args.DATA_PATH)
  
  result = list()
  for idx, row in tqdm.tqdm(enumerate(BDdataset)):
    input, prompt, word, cat, subcat = row

    input_ids = tokenizer.encode(input, add_special_tokens=False, return_tensors="pt")

    generations = model.generate(
        input_ids=input_ids.to(device),
        max_length=input_ids.size(1) + args.OUTPUT_LEN,
        temperature=1.0,
        top_k=args.TOP_K,
        top_p=args.TOP_P,
        repetition_penalty=1.0,
        do_sample=True,
        num_return_sequences=args.NUM_SEQUENCES,
        num_beams=args.NUM_BEAMS
    )

    if len(generations.shape) > 2:
      generations.squeeze_()

    text_generations = list()
    
    for gen in generations:
        gen = gen.tolist()
        text = tokenizer.decode(gen, clean_up_tokenization_spaces=True)
        text = text[:find_nth(text, args.STOP_TOKEN, 1)] if args.STOP_TOKEN not in input else text[:find_nth(text, args.STOP_TOKEN, 2)]
        text_generations.append(text)

    result.append({
        "input": input,
        "prompt": prompt,
        "word": word,
        "category": cat,
        "subcategory": subcat,
        "generations": text_generations
        })
    
  output_path = Path(args.OUTPUT_DIR)
  output_path.mkdir(exist_ok = True)

  f_name = '{}-{}-{}-{}-{}.xlsx'.format(re.sub('/','-', args.GPT2_MODEL), 
                                        args.TOP_K,
                                        args.TOP_P,
                                        args.NUM_BEAMS,
                                        args.OUTPUT_LEN)
  
  pd.DataFrame(list_dict).to_excel(output_path / Path(f_name))
