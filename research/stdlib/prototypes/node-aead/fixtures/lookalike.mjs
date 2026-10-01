// Same spellings as Node's API, but these are workspace-local declarations.
// A production policy must not identify them as node:crypto Decipheriv calls.
function createDecipheriv() {
  return {
    update(value) { return Buffer.from(value); },
    setAuthTag() {},
    final() { return Buffer.alloc(0); },
  };
}

function publish(_value) {}

export function sameNamesAreNotNodeCrypto(bytes) {
  const decipher = createDecipheriv();
  decipher.setAuthTag(Buffer.alloc(16));
  const provisional = decipher.update(bytes);
  publish(provisional);
  decipher.final();
}
