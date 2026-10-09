function redeclared() {
  var duplicate = 1;
  var duplicate = 2;
  console.log(duplicate);
}
redeclared();

function nestedVar() {
  if (true) {
    var inside = 1;
  }
  var inside = 2;
  return inside;
}
