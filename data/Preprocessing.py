from pathlib import Path
import logging, re, argparse
from cached_property import cached_property
from boltons.iterutils import pairwise
from data.utils import Rx, B

class Download:
  def __init__(self, dir):
    self.dir = dir
    self.text = [x for x in map(self.clean_txt, self.read(self.dir)) if len(x) > 0]

  def read(self, dir):
    with open(dir,  mode='rt', encoding='utf-8') as f:
      text = f.readlines()
    return text 

  def clean_txt(self, line):
    return line.replace('\n', '').replace(u'\xa0', u' ').strip()

  
class RxLogging:
  def __init__(self, logger):
    self.logger = logger
    self.show_key = list()

  def show(self, key):
    self.show_key = key if type(key) == list else [key]
  
  def print(self, key, message):
    self.logger.info(message) if key in self.show_key else self.logger.debug(message)

  def check(self, keys, pattern):
    keys = keys if type(keys) == list else [keys]
    undefined = [key for key in keys if key not in pattern]

    if len(undefined):
      self.logger.warning('Undefined key : %s' % ('/'.join(undefined)))

    return list(set(keys)- set(undefined))


class RxSetting:
  def __init__(self):
    self.pattern = dict()
  
  def replace(self, key, target, outcome = '', level = 1):
    self.pattern.update({key : Rx(target, outcome, level)})
  

class RxImport(RxLogging, RxSetting):
  def __init__(self, logger, 
               default : bool = True,
               letter : dict = None, 
               bracket : dict = None, 
               unify : dict = None):
    
    RxLogging.__init__(self, logger)
    RxSetting.__init__(self)

    self.letter, self.bracket, self.unify = letter, bracket, unify

    if default == True:
      from data.scripts import default_dict
      self.pattern.update(default_dict)

    if letter == None:
      from data.scripts import letter_dict
      self.letter = letter_dict
    
    if bracket == None:
      from data.scripts import bracket_dict
      self.bracket = bracket_dict

    if unify == None:
      from data.scripts import unify_dict
      self.unify = unify_dict

  def update_letter(self, keys):
    keys = self.check([x.lower() for x in keys], self.letter)
    self.pattern.update({key : Rx(self.letter[key], '', 1) for key in keys})

  def update_bracket(self, target_keys, outcome_key : str):
    targets = self.check(target_keys, self.bracket)

    assert outcome_key in self.bracket, 'The outcome key is not defined'

    open = '|'.join([self.bracket[t].open for t in targets])
    close = '|'.join([self.bracket[t].close for t in targets])
    self.pattern.update({
        'bracket_open' : Rx(open, self.bracket[outcome_key].open, 2),
        'bracket_close' : Rx(close, self.bracket[outcome_key].close, 2)
        })
    self.empty_bracket(targets)

  def update_unify(self, keys):
    if keys == 'all':
      self.pattern.update(self.unify)
    
    else:
      keys = self.check(keys, self.unify)
      self.pattern.update({key : self.unify[key] for key in keys})

  def empty_bracket(self, bracket_target):
    survive_keys = set(list(self.bracket.keys())) - set(bracket_target)
    
    self.pattern.update({
        'empty_'+ key : Rx(
            '%s[^%s]*%s' % (self.bracket[key].open, 
                              self.bracket[key].close, 
                              self.bracket[key].close), '', 100) 
        for key in survive_keys})
    
    
class RxRevision(RxLogging):
  def __init__(self, logger, pattern, keys = None):
    super().__init__(logger)
    self.pattern = pattern
    self.keys = self.pattern.keys() if keys == None else self.check(keys, self.pattern)
  
  def ordering(self):
    self.keys = sorted(self.keys, key = lambda x : self.pattern[x].level)

  def apply(self, key, input):
    pattern = self.pattern[key]
    output = re.sub(pattern.target, pattern.outcome, input)

    if input != output:
      self.print(key,'pattern : %s / before %s / after %s' %(key, input, output))
      
    return output

  def build(self, text):
    self.ordering()
    self.logger.info('Revising : %s' % ('/'.join(self.keys)))
    
    for key in self.keys:
      text = list(map(lambda x: self.apply(key, x), text))
    
    return text
