function runExpression() {
  return eval(process.argv[2]);
}

function buildFunction() {
  return Function("a", process.argv[3]);
}

function constructFunction() {
  return new Function("a", process.argv[4]);
}
