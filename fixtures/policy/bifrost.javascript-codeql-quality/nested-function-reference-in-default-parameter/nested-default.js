function outer(value = inner()) {
  function inner() {
    return 1;
  }
  return value;
}

function clean(value = helper()) {
  return value;
}

function ordinary() {
  return inner();
}
