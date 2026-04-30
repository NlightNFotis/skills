---
name: pickling-and-preservation
description: Converting perishable to stable forms — the discipline of snapshots, immutable archives, frozen schemas, and pinned versions, with awareness of what is lost in preservation.
user-invocable: true
---

# Pickling and Preservation

Act as a cook stocking the larder. Fresh ingredients are alive — they ripen, oxidize, ferment, decay. Cooks preserve by **arresting change**: pickling halts decay with acid, curing pulls water out with salt, freezing suspends biological time, fermentation guides change to a desired endpoint, canning seals a sterile state. Each method trades one property (fresh texture, raw enzymes, immediate flavor) for another (shelf life, portability, predictability). In software, preservation is the same trade: snapshots, immutable archives, pinned dependencies, frozen schemas, append-only logs. You give up live evolution to gain stability, repeatability, and the ability to look back at exactly what was true on a given day.

Success looks like: a frozen artifact that can be thawed years later and still represent what it represented; a pinned dependency that compiles tomorrow the way it compiled today; an audit log you can replay byte-for-byte. Failure looks like: a "snapshot" that depends on a service that no longer exists; a pinned version whose transitive deps drifted; a "frozen" schema whose semantics quietly migrated under it.

## When to Use This

- Designing snapshot, backup, or archive strategies
- Choosing between mutable and immutable storage formats
- Pinning dependencies and reasoning about reproducible builds
- Designing audit logs, event stores, or append-only ledgers
- Versioning APIs, schemas, contracts, or wire protocols
- Deciding when a working artifact should be "frozen" — a release tag, a published model, a stamped report
- Reviewing whether a preservation strategy actually preserves what it claims

**Escape hatch**: For ephemeral state nobody will look back at, preservation is over-engineering. Use this skill when something must be reproducible, auditable, or recoverable across time.

## Core Mindset

Two questions sit at the center of preservation:

1. **What property am I preserving, and what am I willing to lose?** A pickle is not a fresh cucumber — it is a pickle. A snapshot is not the live system — it is a snapshot. Pretend otherwise and you will be surprised when the thawed artifact behaves differently from the live one.
2. **What does it depend on to *stay* preserved?** Salt curing depends on dry storage. A snapshot depends on the format being readable. A pinned version depends on the registry serving it. Preservation that depends on living infrastructure is only as durable as that infrastructure.

Ask:

- What is the *exact* property I want to be true a year from now?
- What is the perishable thing I'm trying to stabilize?
- Which method best matches the perishability?
- What am I trading away (queryability, freshness, schema flexibility)?
- What does the preserved form *depend on* to remain meaningful?
- Is "best by" enough, or do I need "use by" — soft expiry vs hard expiry?
- How will I know the preservation has failed?

## Preservation Methods and Their Trade-offs

Each cooking method maps to a software pattern with the same trade-off shape.

| Method | Cooking | Software | Preserves | Loses | Depends on |
| --- | --- | --- | --- | --- | --- |
| **Pickling** | Acid arrests microbes | Versioned snapshot in immutable store (S3 with object lock) | Exact bytes at a moment | Live updates; current schema may not match | Storage durability + format stability |
| **Curing** | Salt removes water | Compaction / dehydration (Parquet, columnar) | Structure + queryability | Row-level liveness; some precision | Schema evolution discipline |
| **Drying** | Remove moisture | Static export (CSV, JSON dump) | Portability | Indexes, relationships, types | The reader's tooling |
| **Freezing** | Suspend biological time | Container image, AMI, frozen ML model | Whole running state | Ability to evolve incrementally | Runtime compatibility |
| **Canning** | Sterile sealed state | Signed release tarball, reproducible build | Hermetic reproducibility | Patchability — open it and it's no longer sealed | Cryptographic integrity |
| **Fermentation** | Guided microbial change | Append-only event log; CRDT log | History of every change | Compactness | Replay determinism |
| **Smoking** | Surface preservation + flavor | Hash-anchored record (Merkle, blockchain) | Tamper evidence | Storage cost | Hash function durability |
| **Live cultures** | Sourdough starter, kefir grains | Reproducible build inputs (lockfile + deps) | Continuity, derivability | Exact identity (each generation differs) | The chain of custody |

Match the method to the property. A nightly mysqldump (drying) does not give you point-in-time replay (fermentation). A container image (freezing) does not give you queryability over time (curing).

## Best By vs Use By

Cooking distinguishes:

- **Best by**: quality starts to degrade; still safe
- **Use by**: hard safety/quality cutoff; do not consume past this

Software needs the same distinction:

| Artifact | "Best by" example | "Use by" example |
| --- | --- | --- |
| Snapshot | Schema older than 2 quarters → readers may be lossy | Format unsupported by current tooling → unreadable |
| Pinned dep | Security advisory issued → upgrade soon | CVE actively exploited → must upgrade |
| Cert / token | Approaching expiry → rotate | Past expiry → invalid |
| Cached data | TTL exceeded → refresh preferred | Schema changed upstream → must invalidate |
| Frozen contract | Deprecated → migrate when convenient | Removed → callers must move |

Mark every preserved artifact with both dates when applicable.

## The Process

### Step 1: Name the Perishable

Before choosing a method, identify *what changes over time* and what about it you want to fix.

```
PERISHABLE:
- Live thing:
- What about it changes:
- What I want to fix in time:
- What I am willing to let drift:
- Earliest moment it must be preservable from:
- Latest moment it must remain readable until:
```

Weak: "Snapshot the database."
Strong: "Preserve the exact contents of the `orders` table as of 2025-Q4 close, including row-level data and current schema, queryable for 7 years for audit, OK to lose live indexes and replication state."

### Step 2: Choose the Method by Trade-off, Not Convenience

Default-pickling everything (mysqldump cron, S3 dump) is the equivalent of pickling steaks. Wrong tool.

Decision sketch:

| If you need... | Pick |
| --- | --- |
| Bit-exact reproducibility of a moment | Pickling (immutable object store) |
| Queryability over time | Curing (columnar archive) |
| Portability / movability | Drying (open static formats) |
| Whole running state | Freezing (image/AMI) |
| Audit trail of every change | Fermentation (append-only log) |
| Hermetic, signed, tamper-evident release | Canning (signed tarball + Merkle) |
| Reproducible derivation, not exact bytes | Live culture (lockfile + sources) |

Combine when needed: a release is often **canned** (signed tarball) + **fermented** (commit history) + **frozen** (container image).

### Step 3: Decide What is Lost — and Document It

Every preservation loses something. Make the loss explicit so future readers don't expect what isn't there.

```
LOSS NOTICE for [artifact]:
- Preserved:
- Lost / not recoverable:
- Approximated (and how):
- Format assumptions readers must satisfy:
```

A snapshot README that lists only what is *included* is misleading. List what is *excluded*.

### Step 4: Identify the Dependencies of Preservation

Preservation that depends on living infrastructure is fragile.

For each artifact, ask:

- What software must exist to read it? (Parquet readers, custom proto definitions)
- What credentials / KMS / signing keys are needed?
- What schema registry or external metadata must remain available?
- What format spec, if revised, would render this unreadable?

Reduce dependencies. Prefer:

- Open, widely-implemented formats over proprietary ones
- Self-describing formats (Avro, Parquet with embedded schema) over external schema lookup
- Embedded metadata over registry lookups
- Hash-anchored integrity over signature trust chains that require live CAs

### Step 5: Stamp the Artifact

A preserved artifact must carry its own provenance. At minimum:

- Source identifier (system, version, table, time range)
- Creation timestamp + creating tool version
- Schema or format version
- Hash / checksum
- Best-by and use-by dates
- A pointer to the LOSS NOTICE

A snapshot without metadata is a jar of pickles with no label.

### Step 6: Test the Thaw

Cooks taste their preserves. Software teams almost never do, then are surprised when restore fails.

- Take a snapshot, then **immediately restore it to a scratch environment** and run a smoke check
- Pin dependencies, then build from a clean cache
- Sign a release, then verify the signature with a fresh keychain
- Replay the event log into an empty store and diff against expected
- Open the archive with a clean tool install

Schedule periodic thaw drills. A frozen artifact you have never thawed is a hope, not a backup.

### Step 7: Plan for Schema Drift

Freezing data does not freeze the schema's *meaning* in the rest of the world. The `email` column you snapshotted in 2022 may have a different validation, a different masking rule, or a renamed semantic in 2025.

Mitigations:

- Embed schema *and* schema version in the artifact
- Preserve a copy of the validation/transformation code alongside the data
- For long-lived archives, store a human-readable data dictionary
- Use schema-evolution-aware formats (Avro, Protobuf with field numbers)

### Step 8: Decide When to Stop Preserving

Larders aren't infinite. Define expiry.

- Retention policy by artifact type and regulatory requirement
- Tiering: hot → warm → cold → expire
- Rotation of signing keys with key-roll procedure
- Re-canning: periodically migrate old artifacts to current formats *while* readers still exist for both

The discipline of *purge* is part of preservation. Forever-storage with no purge plan accumulates unreadable artifacts.

## Output Format

```
PRESERVATION PLAN

Perishable:
- ...

Properties to preserve:
- ...

Properties willingly lost:
- ...

Method chosen: [pickling / curing / drying / freezing / canning / fermentation / live culture]
Justification: ...

Format & dependencies:
- Format:
- Reader requirements:
- External dependencies:

Stamp / metadata included:
- ...

Best-by / use-by:
- Best by: ...
- Use by: ...

Thaw test:
- Plan: ...
- Frequency: ...

Retention / purge policy:
- ...

Loss notice:
- ...
```

## Anti-Patterns to Avoid

- **Pickling steak**: using a preservation method that destroys the property you cared about
- **Unstamped jar**: artifact with no provenance metadata
- **Untested thaw**: backups that have never been restored
- **Live-infra dependency**: "preserved" artifact that requires a running service to interpret
- **Schema drift blindness**: assuming today's code can read yesterday's data correctly
- **Forever-storage**: no retention or purge plan; larder fills with unreadable jars
- **Confusing fresh and preserved**: treating a 9-month-old snapshot as if it were live state
- **Sealed-then-patched**: opening a "canned" artifact for a tweak; it is no longer hermetic
- **One-method-fits-all**: defaulting every preservation need to nightly dumps

## Relationship to Other Skills

- `formal-invariants` defines what *must* be true in the preserved artifact (schema, integrity properties).
- `assumption-audit` surfaces hidden assumptions about reader environments, formats, and dependencies.
- `code-forensics` is the consumer of preserved artifacts — its quality depends on what was preserved.
- `incident-review` often reveals that an essential property went un-preserved; feed those findings back here.
- `sequencing-and-temperature` matters for *when* preservation happens (often a lock-in step itself).
- `mise-en-place` should ensure the preserved artifact is staged and reachable before any operation that might need to thaw it.
