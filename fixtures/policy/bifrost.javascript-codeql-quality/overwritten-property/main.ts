const overwritten = {
  x: 1,
  x: 2,
};

const distinct = {
  x: 1,
  y: 2,
};

const methods = {
  run() { return 1; },
  run() { return 2; },
};

const accessors = {
  get value() { return 1; },
  set value(next) { void next; },
};

const computed = {
  ["x"]: 1,
  ["x"]: 2,
};

console.log(overwritten.x, distinct.x, distinct.y);
// Keep the source identity distinct while exercising object-method property facts.
