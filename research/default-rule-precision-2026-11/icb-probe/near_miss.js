export function scan(c, stack) {
  if (c === 0x7b) {
    return true;
  } else if (c === 0x28) {
    stack.push(0x29);
  } else if (c === 0x3b && stack.length === 0) {
    return true;
  }
  return false;
}

export function equals(other, Base, s) {
  if (other == null) {
    return false;
  } else if (other instanceof Base) {
    return s === other.s;
  } else {
    return false;
  }
}
