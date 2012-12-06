#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Roboter spider for bjhjyd.org.cn
'''
import httplib, urllib
import time

def Post(page, issue):
  params = urllib.urlencode({'pageNo':page,
                             'issueNumber':issue,
                             'applyCode':''})
  headers = {'Content-type': 'text/html;charset=utf-8',
             'Accept': 'text/html'}
  conn = httplib.HTTPConnection('apply.bjhjyd.gov.cn')
  conn.request('POST', '/apply/norm/personQuery.html', params, headers)
  response = conn.getresponse()
  if response.status == httplib.OK:
    result = response.read()
  else:
    result = None
  return result


from HTMLParser import HTMLParser
class SimpleHTMLParser(HTMLParser):
  '''
  Parse HTML response.
  '''
  selected = ('table', 'tr', 'td', 'span')
  def reset(self):
    HTMLParser.reset(self)
    self._level_stack = []
    self.data = []
    self.page = []
    self.tmp = None

  def handle_starttag(self, tag, attrs):
    if tag == 'div' and attrs[0][1] == 'resulttable':
      self._level_stack.append('div')
    if 'div' in self._level_stack:
      if tag in self.selected:
        self._level_stack.append(tag)

  def handle_endtag(self, tag):
    if 'table' in self._level_stack:
      if tag in self.selected:
        self._level_stack.remove(tag)

  def handle_data(self, data):
    if 'div' in self._level_stack:
      if 'tr' in self._level_stack:
        if self.tmp is None:
          self.tmp = []
        if 'td' in self._level_stack: 
          self.tmp.append(data)
        if len(self.tmp) > 0:
          self.data.append(self.tmp)
      else:
        self.tmp = None
      
      if 'span' in self._level_stack:
        # page html is not standard
        try:
          self.page.append(int(data))
        except:
          pass
 
def Process():
  parser = SimpleHTMLParser()
  parser.reset()
  
  issue = '201211'
  resp = Post(1, issue)
  parser.feed(resp)
  output = open('tmp.db', 'a')
  if resp is not None:
    parser.feed(resp)
    totalPage = parser.page[0]
    totalNum = parser.page[1]
    output.write('%s\t%s\r\n' % (issue, totalNum))
  
    for page in xrange(1, totalPage):
      time.sleep(3) # bjhjyd.org.cn will block fast access.
      print page
      res = Post(page, issue)
      parser.reset()
      parser.feed(res)
      for data in parser.data:
        output.write('%s\t%s\t%s\r\n' % (data[0], data[1], data[2]))
  output.close()

if __name__ == '__main__':
  Process()
