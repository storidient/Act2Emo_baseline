import pandas as pd
from jamo import h2j, j2hcj
from cached_property import cached_property

"""a list of vowels"""
vowel_list = ['ㅏ','ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ','ㅣ','ㅒ', 
              'ㅐ','ㅔ', 'ㅖ', 'ㅟ', 'ㅚ', 'ㅙ', 'ㅞ']

"""a dictionary of josa"""
josa_dict = dict()

josa_dict['common'] =  ['에', '에서']
josa_dict['liquid'] = ['로부터', '로']
josa_dict['vowel'] = [
                      ('를', '을'), 
                      ('가', '이'),
                      ('는', '은')
                      ]
                      
"""a string to a list"""
def make_list(words):
  output = [re.sub('[^가-힣]', '', w) for w in words.split(',')]
  return [w for w in output if len(w) > 0]             
                      
class AddPrompts:
  def __init__(self, word, vowel = vowel_list, josa = josa_dict):
    self.word = word
    self.vowel, self.liquid = self.decision(vowel)
    self.prompts = self.make_prompts(josa)
    self.input = self.add_prompts()

  @cached_property
  def jongsung(self):
    return j2hcj(h2j(self.word[-1]))[-1]
  
  """decide the type of word"""
  def decision(self, vowel_list):
    vowel, liquid = False, False
    
    if self.jongsung in vowel_list:
      vowel = True
      liquid = True

    if self.jongsung == 'ㄹ':
      liquid = True
          
    return vowel, liquid
  
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
    assert dir.endswith('.xlsx'), 'The file does not end with xlsx'
    
    data = pd.read_excel(dir, header = 0)

    self.keywords = data['Keywords']
    self.cat = data['Category']
    self.subcat = data['SubCategory']

  @cached_property
  def items(self):
    item_list = list()

    for idx, string in enumerate(self.keywords):
      for word in make_list(string):
        item = [(input, 
                 prompt, 
                 word, 
                 self.cat[idx], 
                 self.subcat[idx]
                 ) for prompt, input in AddPrompts(word)
                 ]
        """add items to the list"""
        item_list += item
    
    return item_list
  
  def __len__(self):
    return len(self.items)
  
  def __getitem__(self, idx):
    return self.items[idx]
