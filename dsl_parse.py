# Author: Peter Sovietov

class Stream:
  def __init__(self, buf):
    self.buf = buf
    self.size = len(buf)
    self.pos = 0
    self.error_pos = 0
    self.out = []

def back(state, i, j):
  if state.pos > state.error_pos:
    state.error_pos = state.pos
  state.pos = i
  del state.out[j:]
  return False

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

def quote(*args):
  f = seq(*args)
  def parse(state):
    i = state.pos
    if f(state):
      state.out.append(state.buf[i:state.pos])
      return True
    return False
  return parse

def push(f):
  def parse(state):
    i = state.pos
    if f(state):
      state.out.append(state.buf[i])
      return True
    return False
  return parse

def to(n, f):
  def parse(state):
    i = len(state.out) - n
    state.out[i:] = [f(*state.out[i:])]
    return True
  return parse

def group(*args):
  f = seq(*args)
  def parse(state):
    i = len(state.out)
    if f(state):
      state.out[i:] = [state.out[i:]]
      return True
    return False
  return parse

def eat(f):
  def parse(state):
    if state.pos < state.size and f(state.buf[state.pos]):
      state.pos += 1
      return True
    return False
  return parse

def a(term):
  def parse(state):
    i = state.pos + len(term)
    if state.buf[state.pos:i] == term:
      state.pos = i
      return True
    return False
  return parse

def match(words):
  d = {}
  for w in words:
    d[len(w)] = d.get(len(w), set()) | set([w])
  sets = sorted(d.items(), reverse=True)
  def parse(state):
    for s in sets:
      if state.buf[state.pos:state.pos + s[0]] in s[1]:
        state.pos += s[0]
        return True
    return False
  return parse

def first(table):
  def parse(state):
    c = state.buf[state.pos:state.pos + 1]
    return table[c](state) if c in table else False
  return parse

empty = lambda s: True
one = eat(lambda x: True)
end = notp(one)
opt = lambda f: alt(f, empty)
non = lambda f: seq(notp(f), one)
maybe = lambda f, x: alt(f, to(0, lambda: x))
one_of = lambda c: eat(lambda x: x in c)
range_of = lambda a, b: eat(lambda x: a <= x <= b)
list_of = lambda f, d: seq(f, many(seq(d, f)))

digit = eat(str.isdigit)
letter = eat(str.isalpha)
lower = eat(str.islower)
upper = eat(str.isupper)
alnum = eat(str.isalnum)
space = eat(str.isspace)

def tdop(prefix, infix):
  def parse(state, bp):
    i, j = state.pos, len(state.out)
    f = prefix(state.buf[state.pos]) if state.pos < state.size else None
    if f is None or not f(state):
      return False
    while state.pos < state.size:
      f = infix(state.buf[state.pos])
      if f is None or f[1] < bp:
        return True
      if not f[0](f[1])(state):
        return back(state, i, j)
    return True
  return lambda b: lambda s: parse(s, b)
