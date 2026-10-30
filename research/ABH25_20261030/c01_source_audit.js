// ABH25 C01 — static source-provenance audit, frozen before source read.
// Input is the original scripts/fetch-reunions.mjs at pinned public Git commit.
// Deliberately conservative: text matches are *candidates*, not proof of behavior.
// No fetching, execution of upstream JS or data collection.
function auditSource(source) {
  if (typeof source !== 'string' || source.length < 100) throw new Error('SOURCE_EMPTY_OR_TRUNCATED');
  const find = rx => (source.match(rx) || []).length;
  const versionedHints = find(/(?:first[_-]?public|initial[_-]?publish|published[_-]?at|premier[e_]?[ _-]?publication|archive(?:_at|d)?|histor(?:ique|y)|version[_-]?hash)/gi);
  const timestampHints = find(/(?:scrap(?:ed|ing)|fetch(?:ed)?[_-]?at|download[_-]?at|last[_-]?update|mise[a-z_ -]*jour|updatedAt|datePublication)/gi);
  const explicitNumberHints = find(/(?:petition|p[eé]tition)[^\n]{0,75}(?:num[eé]ro|number|identifiant|[nN][°º])|(?:num[eé]ro|number|identifiant)[^\n]{0,75}(?:petition|p[eé]tition)/gi);
  const snapshotHints = find(/(?:sha256|createHash|digest\(|checksum|etag|git show|commit_sha|git_sha)/gi);
  return {schema:'pfl.abh25.c01.static_audit.v1',source_characters:source.length,versionedHints,timestampHints,explicitNumberHints,snapshotHints,
    first_public_verified:'NOT_ESTABLISHED_BY_STRING_SCAN',semantics_executed:false,requires_manual_context_review:true};
}
if (typeof module !== 'undefined') module.exports = {auditSource};
