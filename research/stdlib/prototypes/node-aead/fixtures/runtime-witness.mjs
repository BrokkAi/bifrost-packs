import assert from 'node:assert/strict';
import { sameNamesAreNotNodeCrypto } from './lookalike.mjs';
import {
  makeGcmPacket,
  finalizeOtherObjectFirst,
  aliasAndHelper,
  cbcSameNames,
  publishBeforeFinal,
  publishedCount,
  resetPublished,
  stageThenPublish,
} from './flow-cases.mjs';

const { body, tag } = makeGcmPacket(Buffer.from('reviewed fixture plaintext'));
const tamperedTag = Buffer.from(tag);
tamperedTag[0] ^= 0x01;

resetPublished();
assert.throws(() => publishBeforeFinal(body, tamperedTag));
assert.equal(publishedCount(), 1);
const positive = {
  case_id: 'positive_before_final_then_final_throws',
  final_outcome: 'throws',
  publication_count_after_throw: publishedCount(),
};

resetPublished();
stageThenPublish(body, tag);
assert.equal(publishedCount(), 1);
const negative = {
  case_id: 'private_staging_final_succeeds_then_publish',
  final_outcome: 'returns_normally',
  publication_count_after_final: publishedCount(),
};

resetPublished();
assert.throws(() => stageThenPublish(body, tamperedTag));
assert.equal(publishedCount(), 0);
const failingFinalBeforePublication = {
  case_id: 'private_staging_then_final_throws_before_publication',
  final_outcome: 'throws',
  publication_count_after_throw: publishedCount(),
};

resetPublished();
assert.throws(() => finalizeOtherObjectFirst(body, tamperedTag));
assert.equal(publishedCount(), 1);
const differentObject = {
  case_id: 'other_object_final_succeeds_before_target_final_throws',
  unrelated_final_outcome: 'returns_normally',
  target_final_outcome: 'throws',
  publication_count_after_target_throw: publishedCount(),
};

resetPublished();
assert.throws(() => aliasAndHelper(body, tamperedTag));
assert.equal(publishedCount(), 1);
const aliasHelper = {
  case_id: 'import_alias_and_helper_transfer_before_final_throws',
  final_outcome: 'throws',
  publication_count_after_throw: publishedCount(),
};

resetPublished();
cbcSameNames(Buffer.from('CBC is unauthenticated'));
assert.equal(publishedCount(), 1);
const nonAeadExclusion = {
  case_id: 'cbc_mode_is_not_authenticated_encryption',
  final_outcome: 'returns_normally',
  publication_count: publishedCount(),
};

sameNamesAreNotNodeCrypto(Buffer.from('local lookalike'));
const localLookalike = {
  case_id: 'same-spelling-workspace-local-api',
  outcome: 'returns_normally',
};

console.log(JSON.stringify({ runtime: process.version, positive, negative, failingFinalBeforePublication, differentObject, aliasHelper, nonAeadExclusion, localLookalike }, null, 2));
