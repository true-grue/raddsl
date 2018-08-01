# Author: Peter Sovietov

def t_eq_list(tree, pattern):
  if not isinstance(tree, list) or len(tree) != len(pattern):
    return False
  for i in range(len(tree)):
    if not t_eq(tree[i], pattern[i]):
      return False
  return True

def t_eq(tree, pattern):
  if isinstance(pattern, list):
    if t_eq_list(tree, pattern):
      return True
  elif callable(pattern):
    if pattern(tree):
      return True
  elif pattern == tree:
    return True
  return False

def t_alt(*args):
  def match(x):
    for pattern in args:
      if t_eq(x, pattern):
        return True
    return False
  return match

def t_not(pattern):
  def match(x):
    return not t_eq(x, pattern)
  return match

def t_any(x):
  return True

def t_to(p, table, name):
  def match(x):
    if t_eq(x, p):
      table[name] = x
      return True
    return False
  return match

def t_list_of(pattern):
  def match(x):
    for e in x:
      if not t_eq(e, pattern):
        return False
    return True
  return match
