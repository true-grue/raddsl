# Author: Peter Sovietov

class Stream:
  def __init__(self, data):
    self.data = data
    self.size = len(data)
    self.pos = 0
    self.error_pos = 0
    self.out = []

def back(state, i, j):
  if state.pos > state.error_pos:
    state.error_pos = state.pos
  state.pos = i
  del state.out[j:]
  return False

def empty(state):
  return True

def andp(f):
  def parse(state):
    i, j = state.pos, len(state.out)
    t = f(state)
    state.pos = i
    del state.out[j:]
    return t
  return parse

def notp(f):
  def parse(state):
    i, j = state.pos, len(state.out)
    t = f(state)
    state.pos = i
    del state.out[j:]
    return not t
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
    while f(state):
      pass
    return True
  return parse

def some(f):
  def parse(state):
    if not f(state):
      return False
    while f(state):
      pass
    return True
  return parse

def seq(*args):
  def parse(state):
    i, j = state.pos, len(state.out)
    for f in args:
      if not f(state):
        return back(state, i, j)
    return True
  return parse

def quote(f):
  def parse(state):
    i = state.pos
    if f(state):
      state.out.append(state.data[i:state.pos])
      return True
    return False
  return parse

def push(f):
  def parse(state):
    i = state.pos
    if f(state):
      state.out.append(state.data[i])
      return True
    return False
  return parse

def pop(f):
  def parse(state):
    if f(state):
      state.out.pop()
      return True
    return False
  return parse

def use(n, f):
  def parse(state):
    i = len(state.out) - n
    state.out[i:] = [f(*state.out[i:])]
    return True
  return parse

def group(f):
  def parse(state):
    i = len(state.out)
    if f(state):
      state.out[i:] = [state.out[i:]]
      return True
    return False
  return parse

def a(term):
  def parse(state):
    i = state.pos
    for x in term:
      if i >= state.size or state.data[i] != x:
        return False
      i += 1
    state.pos = i
    return True
  return parse

def eat(f):
  def parse(state):
    if state.pos < state.size and f(state.data[state.pos]):
      state.pos += 1
      return True
    return False
  return parse

any = eat(lambda x: True)
end = notp(any)
opt = lambda f: alt(f, empty)
non = lambda f: seq(notp(f), any)

digit = eat(str.isdigit)
letter = eat(str.isalpha)
lower = eat(str.islower)
upper = eat(str.isupper)
alnum = eat(str.isalnum)
space = eat(str.isspace)

one_of = lambda c: eat(lambda x: x in c)

def tdop(peek_token, prefix, infix):
  def parse(state, rbp):
    i, j = state.pos, len(state.out)
    t = peek_token(state)
    if t not in prefix or not prefix[t](state):
      return False
    while True:
      t = peek_token(state)
      if t not in infix:
        return True
      f, lbp = infix[t]
      if rbp > lbp:
        return True
      if not f(lbp)(state):
        return back(state, i, j)
  return lambda rbp: lambda state: parse(state, rbp)
