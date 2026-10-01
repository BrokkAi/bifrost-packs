import { createCipheriv, createDecipheriv } from 'node:crypto';
import { createDecipheriv as importedAlias } from 'node:crypto';

const KEY = Buffer.from('00112233445566778899aabbccddeeff', 'hex');
const IV = Buffer.from('101112131415161718191a1b', 'hex');
const ALT_IV = Buffer.from('202122232425262728292a2b', 'hex');
const CBC_IV = Buffer.from('303132333435363738393a3b3c3d3e3f', 'hex');
const published = [];

// Concrete, test-only publication boundary. The exported accessor models a
// trusted caller observing values after publish() returns.
export function publish(value) {
  published.push(Buffer.from(value));
}

export function resetPublished() {
  published.length = 0;
}

export function publishedCount() {
  return published.length;
}

export function makeGcmPacket(plaintext, iv = IV) {
  const cipher = createCipheriv('aes-128-gcm', KEY, iv);
  const body = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  return { body, tag: cipher.getAuthTag() };
}

// Expected positive: a changed tag makes final() throw after publish() has
// already exposed update() bytes to the module-visible publication ledger.
export function publishBeforeFinal(body, tag) {
  const decipher = createDecipheriv('aes-128-gcm', KEY, IV);
  decipher.setAuthTag(tag);
  const provisional = decipher.update(body);
  publish(provisional);
  return decipher.final();
}

// Expected negative: update() bytes remain private until final() succeeds.
export function stageThenPublish(body, tag) {
  const decipher = createDecipheriv('aes-128-gcm', KEY, IV);
  decipher.setAuthTag(tag);
  const staged = decipher.update(body);
  const tail = decipher.final();
  publish(Buffer.concat([staged, tail]));
}

// Expected positive: final() on a second decipher does not authenticate the
// first decipher's provisional bytes.
export function finalizeOtherObjectFirst(body, tag) {
  const provisionalDecipher = createDecipheriv('aes-128-gcm', KEY, IV);
  const unrelatedPacket = makeGcmPacket(Buffer.alloc(0), ALT_IV);
  const unrelatedDecipher = createDecipheriv('aes-128-gcm', KEY, ALT_IV);
  provisionalDecipher.setAuthTag(tag);
  unrelatedDecipher.setAuthTag(unrelatedPacket.tag);
  unrelatedDecipher.update(unrelatedPacket.body);
  const provisional = provisionalDecipher.update(body);
  unrelatedDecipher.final();
  publish(provisional);
  return provisionalDecipher.final();
}

// Expected exclusion: CBC is not an authenticated mode. The API shape alone
// must not make this an AEAD authenticity finding.
export function cbcSameNames(body) {
  const decipher = createDecipheriv('aes-128-cbc', KEY, CBC_IV);
  const cipher = createCipheriv('aes-128-cbc', KEY, CBC_IV);
  const ciphertext = Buffer.concat([cipher.update(body), cipher.final()]);
  const provisional = decipher.update(ciphertext);
  publish(provisional);
  return decipher.final();
}

// Expected positive if helper transfer and an import alias are modeled.
function takeChunk(decipher, body) {
  return decipher.update(body);
}

export function aliasAndHelper(body, tag) {
  const make = importedAlias;
  const decipher = make('aes-128-gcm', KEY, IV);
  decipher.setAuthTag(tag);
  const provisional = takeChunk(decipher, body);
  publish(provisional);
  return decipher.final();
}

// Expected negative: successful final() on the same object dominates the
// publication call.
export function finalBeforePublish(body, tag) {
  const decipher = createDecipheriv('aes-128-gcm', KEY, IV);
  decipher.setAuthTag(tag);
  const staged = decipher.update(body);
  const tail = decipher.final();
  publish(Buffer.concat([staged, tail]));
}
