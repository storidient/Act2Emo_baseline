from jamo import h2j, j2hcj

"""a list of vowels"""
korean_vowel = ['ㅏ','ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ','ㅣ','ㅒ', 
              'ㅐ','ㅔ', 'ㅖ', 'ㅟ', 'ㅚ', 'ㅙ', 'ㅞ']

"""a string to a list"""
def make_list(words):
  output = [re.sub('[^가-힣]', '', w) for w in words.split(',')]
  return [w for w in output if len(w) > 0]

"""extract jongsung from a word"""
def extract_jongsung(word):
  return j2hcj(h2j(word[-1]))[-1]

"""decide jongsung type for josa"""
def decide_jongsung(word, vowel_list=korean_vowel):
  jongsung = extract_jongsung(word)
  
  vowel, liquid = False, False
  
  if jongsung in vowel_list:
    vowel, liquid = True, True

  if jongsung == 'ㄹ':
    liquid = True
          
  return vowel, liquid
