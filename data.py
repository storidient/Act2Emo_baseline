import re
import pandas as pd
from cached_property import cached_property
from utils import extract_jongsung, decide_jongsung, make_list

"""a dictionary of josa"""
josa_dict = dict()

josa_dict['common'] =  ['에', '에서']
josa_dict['liquid'] = ['로부터', '로']
josa_dict['vowel'] = [
                      ('를', '을'), 
                      ('가', '이'),
                      ('는', '은')
                      ]
                      
class AddPrompts:
  def __init__(self, word, josa = josa_dict):
    self.word = word
    self.vowel, self.liquid = decide_jongsung(self.word)
    self.prompts = self.make_prompts(josa)
    self.input = self.add_prompts()
  
  """make a list of prompts"""
  def make_prompts(self, josa):
    prompts = list()

    prompts += josa['common']
    prompts += [t[0] if self.vowel == True else t[1] for t in josa['vowel']]
    prompts += ['으' + t if self.liquid == False else t for t in sorted(josa['liquid'])]

    return prompts
  
  """make a list of words"""
  def add_prompts(self):
    return list(map(lambda p : self.word + p, self.prompts))
  
  def __getitem__(self, idx):
    return (self.prompts[idx], self.input[idx])

class BodyDataset:
  def __init__(self, dir):
    
    """open the file"""
    if dir.endswith('.xlsx'):   
      data = pd.read_excel(dir, header = 0)
    
    elif dir.endswith('.csv'):
      data = pd.read_excel(dir, header = 0)
    
    else:
      raise Exception('The type of file should be csv or xlsx')
    
    self.keywords = data['Keywords']
    self.cat = data['Category']
    self.subcat = data['SubCategory']

  @cached_property
  def items(self):
    item_list = [
      [
        [(input, prompt, word, self.cat[idx], self.subcat[idx]) 
          for prompt, input in AddPrompts(word)] 
        for word in make_list(string)
      ] 
      for idx, string in enumerate(self.keywords)
    ]
    
    return sum(item_list, [[]])
  
  def __len__(self):
    return len(self.items)
  
  def __getitem__(self, idx):
    return self.items[idx]
