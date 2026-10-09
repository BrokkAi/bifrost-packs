export function typedOuter(value: number = inner()) {
  function inner(): number {
    return 1;
  }
  return value;
}
