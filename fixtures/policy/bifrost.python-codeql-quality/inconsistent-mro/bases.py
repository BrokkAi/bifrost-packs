class X:
    pass

class Y(X):
    pass

# Python raises TypeError while constructing this class because C3 cannot
# satisfy X before Y when Y already requires X first.
class Broken(X, Y):
    pass

class Good(Y, X):
    pass
