# Author: Peter Sovietov

class Tree:
  def __init__(self, out=[]):
    self.scope = None
    self.out = out

def match_list(tree, x, y):
  for i in range(len(x)):
    if not match(tree, x[i], y[i]):
      return False
  return True

def match(tree, x, y):
  if callable(y):
    m, r = apply(tree, y, x)
    return m
  if isinstance(y, list):
    return isinstance(x, list) and len(x) == len(y) and match_list(tree, x, y)
  return x == y

def apply(tree, f, x):
  out = tree.out
  tree.out = x
  m = f(tree)
  r = tree.out
  tree.out = out
  return m, r

def perform(tree, x):
  if callable(x):
    return x(tree)
  return match(tree, tree.out, x)

def any(tree):
  return True

def non(x):
  def walk(tree):
    return not perform(tree, x)
  return walk

def alt(*args):
  def walk(tree):
    for x in args:
      if perform(tree, x):
        return True
    return False
  return walk

def seq(*args):
  def walk(tree):
    out = tree.out
    for x in args:
      if not perform(tree, x):
        tree.out = out
        return False
    return True
  return walk

def let(**kwargs):
  name, value = list(kwargs.items())[0]
  def walk(tree):
    if name in tree.scope:
      return match(tree, tree.out, tree.scope[name])
    if perform(tree, value):
      tree.scope[name] = tree.out
      return True
    return False
  return walk

def var(**kwargs):
  name, value = list(kwargs.items())[0]
  def walk(tree):
    if perform(tree, value):
      tree.scope[name] = tree.out
      return True
    return False
  return walk

class Scopedict(dict):
  def __getattr__(self, n):
    return self[n]

def rule(*args):
  f = seq(*args)
  def walk(tree):
    scope = tree.scope
    tree.scope = Scopedict()
    m = f(tree)
    tree.scope = scope
    return m
  return walk

def where(*args):
  f = seq(*args)
  def walk(tree):
    m, r = apply(tree, f, tree.out)
    return m
  return walk

def to(f):
  def walk(tree):
    tree.out = f(tree.scope)
    return True
  return walk

def use_var(name):
  def walk(tree):
    tree.out = tree.scope[name]
    return True
  return walk

def rebuild(f):
  def walk(tree):
    tree.out = f(tree)
    return True
  return walk

def cons(x, y):
  def walk(tree):
    if isinstance(tree.out, list) and tree.out:
      return match(tree, tree.out[0], x) and match(tree, tree.out[1:], y)
    return False
  return walk

def rewrite_list(tree, x, y):
  for i in range(len(x)):
    if not rewrite_node(tree, x[i], y[i]):
      return False
    x[i] = tree.out
  return True

def rewrite_node(tree, x, y):
  if callable(y):
    m, x = apply(tree, y, x)
    if not m:
      return False
  elif isinstance(y, list):
    if not isinstance(x, list) or len(x) != len(y):
      return False
    x = x[:]
    if not rewrite_list(tree, x, y):
      return False
  elif x != y:
    return False
  tree.out = x
  return True

def rewrite(y):
  def walk(tree):
    out = tree.out
    if not rewrite_node(tree, tree.out, y):
      tree.out = out
      return False
    return True
  return walk

def each(*args):
  f = seq(*args)
  def walk(tree):
    if not isinstance(tree.out, list):
      return False
    out = tree.out[:]
    for i in range(len(out)):
      if isinstance(out[i], list):
        m, r = apply(tree, f, out[i])
        if not m:
          return False
        out[i] = r
    tree.out = out
    return True
  return walk

scope = lambda f: lambda t: f(t.scope)(t)
guard = lambda f: lambda t: f(t.scope)
opt = lambda x: alt(x, any)
call = lambda f, *a: lambda t: f(t, *a)
delay = lambda f: lambda t: f()(t)

repeat = lambda x: opt(seq(x, delay(lambda: repeat(x))))
topdown = lambda x: seq(x, each(delay(lambda: topdown(x))))
bottomup = lambda x: seq(each(delay(lambda: bottomup(x))), x)
innermost = lambda x: bottomup(opt(seq(x, delay(lambda: innermost(x)))))
alltd = lambda x: alt(x, each(delay(lambda: alltd(x))))
untiltd = lambda x, y: seq(x, alt(y, each(delay(lambda: untiltd(x, y)))))
