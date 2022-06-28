from pathlib import Path
import logging, re, argparse
from cached_property import cached_property
from boltons.iterutils import pairwise
from data.utils import Rx, B



class RxLogging:
  """Gets the logger and monitor the process"""
  
  def __init__(self, logger):
    self.logger = logger
    self.show_key = list()
  
  def show(self, key: str):
    """Gets the show_key list updated"""
    self.show_key = [key] if type(key) == str else key
  
  def print(self, key : str, message : str):
    """Prints the message if the key is in the show_key list"""
    self.logger.info(message) if key in self.show_key else self.logger.debug(message)
  
  def check(self, keys, pattern):
    """Checks if the keys are in the pattern dictionary"""
    keys = keys if type(keys) == list else [keys]
    undefined = [key for key in keys if key not in pattern]

    if len(undefined):
      self.logger.warning('Undefined key : %s' % ('/'.join(undefined)))

    return list(set(keys)- set(undefined))


class RxDivision(RxLogging):
  """Divides the episodes and scenes"""
  def __init__(self, logger, 
               ep_pattern : dict = None,
               scene_pattern : dict = None):
    
    RxLogging.__init__(self, logger)
    self.pattern, self.ep, self.scene = dict(), ep_pattern, scene_pattern

    if ep_pattern == None:
      from data.scripts import ep_pattern_dict
      self.ep = ep_pattern_dict
    
    if scene_pattern == None:
      from data.scripts import scene_pattern_dict
      self.scene = scene_pattern_dict
  
  def match(self, key, line):
    """Returns True if the line matches with the pattern"""
    if re.match(self.pattern[key], line):
      self.print(key, 'seperation_pattern : %s / line : %s' % (key,line))
      return True
    else:
      return False
    
  def get_idx(self, key, text):
    return [idx for for idx, line in enumerate(text) if self.match(key, line) == True]
      
  def main(self, text, scene = False):
    """Divides the text into episodes"""
    self.pattern = self.ep if scene == False else self.scene
    
    indices = list(map(lambda key : self.get_idx(key, text), self.pattern.keys()))
    indices = sum(indices, [])
    indices = [0] + sorted(set(indices))
    
    output = [text[s1:s2] if (s1 == 0 and indices.count(0) == 1) else text[s1+1:s2] 
              for s1, s2 in pairwise(indices)]
    output.append(text[max(indices)+1:])
    
    return [x for x in output if len(x) > 0]

  
class RxSetting(RxLogging):
  """Gets the revising rules and patterns easily
   
   Args:
    letter : Korean, imperfect Korean letters(e.g. ㅋㅋㅋ), English, Chinese, Numbers ...
    bracket -> (), <>, [], {}, ...
    unify -> other special marks to unify (e.g. -, ...)
  
  """
  def __init__(self, logger,
               letter : dict = None, 
               bracket : dict = None, 
               unify : dict = None,
               default : bool = True):
    
    RxLogging.__init__(self, logger)
    RxSetting.__init__(self)
    
    self.pattern, self.excluded_bracket = dict(), list()
    self.letter, self.bracket, self.unify = letter, bracket, unify
    
    self.basic_marks = ['\.', '\!', '\?', ' ', ',', '\-', '⋯', '"', "'"] #TODO

    if default == True: #TODO
      from data.scripts import default_dict
      self.pattern.update(default_dict)

    if letter == None: #TODO
      from data.scripts import letter_dict
      self.letter = letter_dict
    
    if bracket == None: #TODO
      from data.scripts import bracket_dict
      self.bracket = bracket_dict

    if unify == None: #TODO
      from data.scripts import unify_dict
      self.unify = unify_dict

  def update_letter(self, keys):
    """Gets the letter type to delete and updates the revising rules"""
    keys = self.check([x.lower() for x in keys], self.letter)
    self.pattern.update({key : Rx('[%s]' % (self.letter[key]), '', 1) for key in keys})
  
  def update_bracket(self, target_keys, outcome_key : str):
    """Gets the brackets to revise and updates the revising rules"""
    targets = self.check(target_keys, self.bracket)  
    
    t_open = '|'.join([self.bracket[t].open for t in targets])
    t_close = '|'.join([self.bracket[t].close for t in targets])
    
    if outcome_key in self.bracket:
      self.pattern.update({
        'bracket_open' : Rx(t_open, self.bracket[outcome_key].open, 2),
        'bracket_close' : Rx(t_close, self.bracket[outcome_key].close, 2)
        })  
    else:
      self.logger.warning('The outcome key is not defined')
      
    self.excluded_bracket = targets #save the brackets to exclude  
    self.update_empty_bracket()
  
  def update_unify(self, keys):
    """Gets the special marks to unify and updates the revising rules"""
    if keys == 'all':
      self.pattern.update(self.unify)    
    else:
      self.pattern.update(
        {key : self.unify[key] for key in self.check(keys, self.unify)}
      )
  
  def update_empty_bracket(self):
    """Makes rules to delete empty brackets e.g. (), <> ..."""
    remain_keys = set(self.bracket.keys()) - set(self.exclude_bracket)

    self.pattern.update(
      {'empty_'+ key : Rx('%s[^%s%s]*%s' % (self.bracket[key].open,
                                            ''.join(self.letter.values()),
                                            self.bracket[key].close,
                                            self.bracket[key].close), '', 100) 
       for key in remain_keys})
  
  def check_marks(self, 
                  add_marks : list = None, 
                  default: bool = True) -> str:
    """Returns the RxPattern to check if lines have unexpected special marks"""
    output = add_marks if add_marks != None else list()
    output += [self.letter[key] for key in self._exclude(self.letter.keys())]
    output += [self.bracket[key].open + self.bracket[key].close
               for key in self._exclude(self.bracket, self.exclude_bracket)]
    
    if default == True:
      outcome += self.basic_marks
      
    return '[^%s]' % (''.join(set(outcome)))
  
  def _exclude(self, whole_keys, minus_keys = None):
    minus_keys = self.pattern.keys() if minus_keys == None else minus_keys
    return set(whole_keys) - set(minus_keys)

  
class RxRevision(RxLogging):
  """Gets the revising patterns and revise the text"""
  def __init__(self, logger, pattern, keys = None):
    super().__init__(logger)
    self.pattern = pattern
    self.keys = self.pattern.keys() if keys == None else self.check(keys, self.pattern)
  
  def ordering(self):
    """Re-orders the revising rules by the level"""
    self.keys = sorted(self.keys, key = lambda x : self.pattern[x].level)

  def update_pattern(self, text):
    """Adds 「」『』 marks as quotation marks if there is no " in the text"""
    text = ''.join(text) if type(text) == list else text
    
    if re.match('.*["“”].*', text):
      self.pattern.pop('alternative_quotation', None)

    elif re.match('.*[「」『』].*', text):
      self.pattern.update({'alternative_quotation' : Rx('[「」『』]', '"', 0)})
      self.logger.info('Quotation_updated : 「」『』')
    
    elif re.match('.*[<>].*', text):
      self.pattern.update({'alternative_quotation' : Rx('[<>]', '"', 0)})
      self.logger.info('Quotation_updated : <>')
   
  def apply(self, key : str, input : str):
    """Applies the revsing rules to the line"""
    pattern = self.pattern[key]
    output = re.sub(pattern.target, pattern.outcome, input)
    if input != output:
      self.print(key,'pattern : %s / before %s / after %s' %(key, input, output))              
    return output

  def main(self, text):
    """Revises the text"""
    self.update_pattern(text)
    self.ordering()
    
    output = list()
    for line in text:
      for key in self.keys:
        line = self.apply(key, line)
      output.append(line)
        
    return output
