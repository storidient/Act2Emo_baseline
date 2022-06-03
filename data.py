import re
import pandas as pd
from cached_property import cached_property
from utils import Jongsung, make_list, open_dir

"""a dictionary of josa"""
josa_dict = dict()

josa_dict['common'] =  ['에', '에서']
josa_dict['liquid'] = ['로부터', '로']
josa_dict['vowel'] = [
                      ('를', '을'), 
                      ('가', '이'),
                      ('는', '은')
                      ]

"""inherit class Jongsung and add prompts"""
class AddPrompts(Jongsung):
  def __init__(self, word, josa = josa_dict):
    super().__init__(word)
    
    self.prompts = self.make_prompts(josa)
    self.input = self.add_prompts()
  
  """make a list of prompts"""
  def make_prompts(self, josa):
    prompts = josa['common']
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
    self.data = open_dir(dir)
   
    self.keywords = self.data['Keywords']
    self.cat = self.data['Category']
    self.subcat = self.data['SubCategory']
    
  @cached_property
  def items(self):
    item_list = list()
    
    for idx, string in enumerate(self.keywords):
      for word in make_list(string):
        item_list += [(input, prompt, word, self.cat[idx], self.subcat[idx]) 
                      for prompt, input in AddPrompts(word)]
    
    return item_list
         
  def __len__(self):
    return len(self.items)
  
  def __getitem__(self, idx):
    return self.items[idx]
