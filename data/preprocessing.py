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

  
class RxLogging:
  def __init__(self, logger):
    self.logger = logger
    self.show_key = list()

  def show(self, key):
    self.show_key = key if type(key) == list else [key]
  
  def print(self, key, message):
    self.logger.info(message) if key in self.show else self.logger.debug(message)

  def check(self, keys, pattern):
    keys = keys if type(keys) == list else [keys]
    undefined = [key for key in keys if key not in pattern]

    if len(undefined):
      self.logger.warning('Undefined key : %s' % ('/'.join(undefined)))

    return list(set(keys)- set(undefined))
