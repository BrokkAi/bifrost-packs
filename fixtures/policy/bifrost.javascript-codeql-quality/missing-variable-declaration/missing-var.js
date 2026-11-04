function accidental(limit) {
  for (i = 0; i < limit; i++) {
    total += i;
  }
  return total;
}

function declared(limit) {
  let i = 0;
  return i + limit;
}

function assigned() {
  value = 1;
  return value;
}
