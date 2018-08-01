# Author: Peter Sovietov

class Parser:
  def __init__(self, data):
    self.data = data
    self.begin_index = 0
    self.end_index = 0
    self.error_index = 0
    self.value = None

def back(state, index):
  state.error_index = max(state.error_index, state.end_index)
  state.end_index = index
  return False

def empty(state):
  state.value = None
  return True

def opt(f):
  def parse(state):
    if not f(state):
      state.value = None
    return True
  return parse

def andp(f):
  def parse(state):
    i = state.end_index
    state.value = f(state)
    back(state, i)
    return state.value
  return parse

def notp(f):
  def parse(state):
    i = state.end_index
    state.value = not f(state)
    back(state, i)
    return state.value
  return parse

def alt(*args):
  def parse(state):
    for f in args:
      if f(state):
        return True
    return False
  return parse

def many(f):
  def parse(state):
    value = []
    while f(state):
      value.append(state.value)
    state.value = value
    return True
  return parse

def some(f):
  def parse(state):
    value = []
    while f(state):
      value.append(state.value)
    state.value = value
    return len(value) != 0
  return parse

def last(*args):
  def parse(state):
    i = state.end_index
    for f in args:
      if not f(state):
        return back(state, i)
    return True
  return parse

def seq(*args):
  def parse(state):
    value = []
    i = state.end_index
    for f in args:
      if not f(state):
        return back(state, i)
      value.append(state.value)
      state.value = value
    return True
  return parse

def act(f, g):
  def parse(state):
    i = state.end_index
    if f(state):
      state.begin_index = i
      state.value = g(state)
      return True
    return False
  return parse

def next(data):
  def parse(state):
    i = state.end_index
    for x in data:
      if i >= len(state.data) or state.data[i] != x:
        return False
      i += 1
    state.value = data
    state.end_index = i
    return True
  return parse

def eat(f):
  def parse(state):
    if state.end_index < len(state.data) and f(state.data[state.end_index]):
      state.value = state.data[state.end_index]
      state.end_index += 1
      return True
    return False
  return parse

any = eat(lambda x: True)
end = notp(any)

digit = eat(str.isdigit)
letter = eat(str.isalpha)
lower = eat(str.islower)
upper = eat(str.isupper)
alnum = eat(str.isalnum)
space = eat(str.isspace)

def acts(f, g):
  return act(f, lambda state: g(*state.value))

def first(*args):
  return act(seq(*args), lambda x: x.value[0])

def charset(chars):
  return eat(lambda x: x in chars)

def one_of(p, args):
  return alt(*map(p, args))

def list_of(p, d):
  return act(seq(p, many(last(d, p))), lambda x: [x.value[0]] + x.value[1])
