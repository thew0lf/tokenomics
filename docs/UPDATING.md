# Updating Tokenomics

Tokenomics separates application releases from knowledge updates.

## Application updates

Application upgrades can change code, schemas, detection behavior, and interfaces. They should be versioned and documented in the changelog.

Local user data should remain intact across normal upgrades. The local SQLite
database records its schema version using `PRAGMA user_version`. Migrations are
forward-only and applied in order; a newer database is rejected with a clear
upgrade error rather than being opened by an older application version.

## Knowledge updates

Knowledge packs contain generalized detection rules and optimization strategies. They can be updated independently from the application.

An intended update flow is:

```text
Tokenomics starts
      |
      v
Check knowledge version
      |
      v
Local version older?
   /          \
 yes           no
  |             |
Download      Continue
validate
  |
Install
  |
Continue
```

Tokenomics validates a candidate knowledge pack before activation, writes the
validated file atomically, and preserves the previous active pack alongside it
with a `.previous` suffix. Restoring that file is a local, manual rollback.

## Compatibility

Knowledge rules should declare the minimum Tokenomics version they require when behavior depends on a specific analyzer capability.

Example:

```yaml
id: repeated-context
version: 3
requires:
  tokenomics: ">=0.3"
confidence: 0.94
```

## Privacy during updates

Knowledge updates may download public rules. They must not require uploading private conversations, source code, project files, or other private usage data.
