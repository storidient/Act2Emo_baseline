from bs4 import BeautifulSoup
import requests, re, logging, argparse
from pathlib import Path
from cached_property import cached_property
from boltons.iterutils import pairwise



def open_link(url):
    response = requests.get(url)
    html = response.text
    return BeautifulSoup(html, 'html.parser')

  
def clean_html(line):
    return str(line).lstrip('<p>').rstrip('</p>').strip('br/>')

  
class WikiCrawling:
  def __init__(self, url, home=''):
      self.url = url
      self.home = home

      if 'wiki' in self.url:
          self.home = 'https://ko.wikisource.org/'
            
  @cached_property
  def files(self):
    return open_link(self.url).select(
        '#mw-pages > div > div > div > ul > li > a'
        )
    
  def novel(self, name):
    link = [x.attrs['href'] for x in self.files if name in x.attrs['title']]
    
    assert len(link) == 1, '%d link for %s' % (len(link), name)

    novel_text = open_link(self.home + link[0]).select(
        '#mw-content-text > div.mw-parser-output > p'
        )
    
    return list(map(clean_html, novel_text))
