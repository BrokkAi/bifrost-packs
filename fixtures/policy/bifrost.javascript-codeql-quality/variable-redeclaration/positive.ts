export function typedRedeclared() {
  var duplicate: number = 1;
  var duplicate: number = 2;
  return duplicate;
}
