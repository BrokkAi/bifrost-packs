export function adjacent(a, b, out) {
  if (a) {
    out.push(1);
  } else if (b) {
    out.push(1);
  } else {
    out.push(2);
  }
}

export function redundantElse(c) {
  if (c === 0x7b) {
    return 1;
  } else if (c === 0x7d) {
    return true;
  } else {
    return true;
  }
}
