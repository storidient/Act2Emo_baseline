import re
from jamo import h2j, j2hcj
from cached_property import cached_property



"""a list of vowels"""
korean_vowel = ['ㅏ','ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ','ㅣ','ㅒ', 
              'ㅐ','ㅔ', 'ㅖ', 'ㅟ', 'ㅚ', 'ㅙ', 'ㅞ']


"""a string to a list"""
def make_list(words):
  output = [re.sub('[^가-힣]', '', w) for w in words.split(',')]
  return [w for w in output if len(w) > 0]


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
      
    elif self.jongsung in vowel_list:
      self.liquid = True
