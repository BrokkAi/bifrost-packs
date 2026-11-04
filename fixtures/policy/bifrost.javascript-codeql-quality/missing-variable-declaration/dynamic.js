function dynamicWith(object) {
  with (object) {
    implicit = 1;
    return implicit;
  }
}

function dynamicEval() {
  eval("implicit = 1");
  another = 1;
  return another;
}
