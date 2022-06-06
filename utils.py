import re
from jamo import h2j, j2hcj
from cached_property import cached_property
from pathlib import Path



"""a list of vowels"""
korean_vowel = ['ㅏ','ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ','ㅣ','ㅒ', 
              'ㅐ','ㅔ', 'ㅖ', 'ㅟ', 'ㅚ', 'ㅙ', 'ㅞ']


"""a string to a list"""
def make_list(words):
  output = [re.sub('[^가-힣]', '', w) for w in words.split(',')]
  return [w for w in output if len(w) > 0]


"""open the file"""
def open_dir(dir):
  if dir.endswith('.xlsx'):   
    return pd.read_excel(dir, header = 0)

  elif dir.endswith('.csv'):
    return pd.read_excel(dir, header = 0)

  else:
    raise Exception('The type of file should be csv or xlsx')

    
"""save_the_file"""
def save_file(result, output_dir, file_name, output_type = xlsx):
  output_dir = Path(output_dir)
  output_dir.mkdir(exist_ok = True)
  
  file_name = re.sub('/','-',file_name)
  
  if output_type == 'xlsx':
    file_name += '.xlsx'
    pd.DataFrame(result).to_excel(output_dir / Path(file_name))
  
  elif output_type == 'csv':
    file_name += '.csv'
    pd.DataFrame(result).to_csv(output_dir / Path(file_name))
  
  else:
    raise Exception('The type of file should be csv or xlsx')    

    
    
class JongSung:
  def __init__(self, word, vowel_list = korean_vowel):
    self.word = word
    self.vowel, self.liquid = False, False
    self._build(vowel_list)
      
  @cached_property
  def jongsung(self):
    return j2hcj(h2j(self.word[-1]))[-1]
  
  def _build(self, vowel_list):
    if self.jongsung in vowel_list:
      self.vowel, self.liquid = True, True
      
    elif self.jongsung == 'ㄹ':
      self.liquid = True
