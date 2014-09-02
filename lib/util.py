'''
Created on Aug 27, 2014
@author: Mohammed Hamdy
'''

class ContinuationIterator(object):
  """
  Takes a list of strings as input. Concatenates lines with ampersands to one line
  before returning it. Acts as iterator
  """
  
  def __init__(self, lines):
    self._lines = lines
    self._current_index = 0
    
  def __iter__(self):
    return self
  
  def next(self):
    if len(self._lines) == self._current_index:
      raise StopIteration
    next_line = self._lines[self._current_index]
    self._current_index += 1
    continuation_lines = [next_line]
    continuation_line = '&' in next_line
    while continuation_line:
      if len(self._lines) == self._current_index:
        break
      next_line = self._lines[self._current_index]
      self._current_index += 1
      continuation_line = '&' in next_line
      if continuation_line:
        continuation_lines.append(next_line)
    if len(continuation_lines) > 1: # must have found a multi-line thing
      self._current_index -= 1 # since i'm now a line after continuation
    continuation_lines = [line.replace('&', '').strip() for line in continuation_lines]
    line = ' '.join(continuation_lines)
    return line
  