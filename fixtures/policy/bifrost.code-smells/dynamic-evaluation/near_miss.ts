function memberCalls(obj: any, factory: any, data: string) {
  obj.eval("1 + 1");
  obj.inner.eval("2");
  factory().eval("3");
  obj[0].eval("4");
  factory.Function(data);
  obj.eval(Function, data);
}

function shadowedFunction() {
  const Function = (text: string) => text;
  return Function("local");
}
