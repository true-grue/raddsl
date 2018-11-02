# code formatter

class Head(dict):
  def __eq__(self, right):
    return self["tag"] == right
  def __ne__(self, right):
    return not self.__eq__(right)

def make_term(tag):
  return lambda *a, **k: (Head(tag=tag, **k),) + a

is_term = lambda x: isinstance(x, tuple)

Id = make_term("Id")
Int = make_term("Int")
Assign = make_term("Assign")
Bop = make_term("Bop")
If = make_term("If")
Func = make_term("Func")

H = make_term("H")
V = make_term("V")
