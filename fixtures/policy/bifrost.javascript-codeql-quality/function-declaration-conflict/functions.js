function outer(flag) {
  if (flag) {
    function helper() { return 1; }
  } else {
    function helper() { return 2; }
  }
  return helper();
}

function unique() {
  return 0;
}

function globalDuplicate() {}
function globalDuplicate() {}
