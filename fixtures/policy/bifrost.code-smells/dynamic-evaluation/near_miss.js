function memberCalls(obj, factory, data) {
  obj.eval("1 + 1");
  obj.inner.eval("2");
  factory().eval("3");
  obj[0].eval("4");
  factory.Function(data);
  obj.eval(Function, data);
}

function shadowedEval() {
  const eval = (text) => text;
  return eval("local");
}

function shadowedFunction() {
  const Function = (text) => text;
  return Function("local");
}
