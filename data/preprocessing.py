from pathlib import Path
import logging, re, argparse
from cached_property import cached_property
from boltons.iterutils import pairwise



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



class Cleansing:
  def __init__(self, logger, pattern = None, keys = None):    
    self.logger = logger
    self.showing = list()

    if pattern == None:
      from revising_pattern import pattern_dict
      self.pattern = pattern_dict
    else:
      self.pattern = pattern

    self.keys = self.pattern.keys() if keys == None else self.check(keys)
    self.ordering()


  def check(self, keys):
    revised_keys = [x for x in keys if x in self.pattern.keys()]    
    missing_keys = set(keys) - set(revised_keys)
    
    if len(missing_keys) > 0:
      self.logger.warning(
          'Not defined key - %s' % ('/'.join(missing_keys))
          )
    return revised_keys


  def ordering(self):
    self.keys = sorted(
        self.keys, key = lambda x: self.pattern[x][-1]
        )
    self.logger.info('The key list: %s \n' % (self.keys))


  def show(self, key_list):
    self.showing = self.check(key_list)  
    

  def build(self, text):
    for key in self.keys:
      text = list(
          map(lambda x: self.apply(key, x), text)
          )
    return text


  def apply(self, key, line):
    pattern = self.pattern[key]
    cleaned = re.sub(pattern[0], pattern[1], line)
		
		if cleaned == line: pass
		
		else:
    	message  = 'type : %s \ before : %s \ after : %s \n' % (key, line, cleaned)
			self.logger.info(message) if key in self.showing else self.logger.debug(messages)
                            
    return cleaned
