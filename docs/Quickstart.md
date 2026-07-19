# ⭐ Structural Receipt — Quickstart

## Portable, Purpose-Resolvable and Reconstructable Evidence for Purchases and Financial Transactions

**Release:** `v0.5.3`  
**Architecture:** `SR-CORE-5`  
**Resolver:** `SR-RESOLVER-5-D01`  
**Canonicalization:** `SR-CANON-1-D01`

**Deterministic • Purpose-Resolved • Lineage-Preserving • Verification-Oriented**

---

# What Structural Receipt Demonstrates

Structural Receipt is a deterministic reference architecture for representing purchase and financial transaction evidence as a portable, purpose-resolvable structure.

Its primary principle is:

`Declare once. Resolve by purpose. Preserve through change. Verify independently.`

Its adoption principle is:

`Adopt on one side. Verify on the other. Integrate only when useful.`

The core structural model is:

`SR = (C, E, D, L, O, V)`

The current release demonstrates:

- nine identified purpose profiles;
- explicit `RESOLVED`, `INCOMPLETE`, `CONFLICT`, and `UNSUPPORTED` outcomes;
- declared identified evaluation context;
- trust and authority separation;
- exact supported money handling;
- non-destructive transaction lineage;
- separate receipt, structure, lineage-graph, and current-state identities;
- portable purpose receipts;
- portable evidence bundles;
- standalone local verification;
- separate Python reconstruction;
- frozen conformance, tamper, and hostile-input corpora;
- bridge-based one-sided adoption;
- standalone purpose-profile artifacts;
- reproducible cross-boundary examples.

---

# Choose Your Starting Path

You do not need to use every part of the repository.

Choose the path that matches what you already have.

## Path A — Explore Structural Receipt

Open:

`demo/Structural_Receipt_Reference_Demo_v0_5_3.html`

Use the browser reference to inspect purpose resolution, lineage, identities, evidence export, and producer-side audit behavior.

---

## Path B — Verify a Structural Receipt Evidence Bundle

Open:

`verify/Structural_Receipt_Standalone_Verifier_v0_5_3.html`

Load a supported Structural Receipt evidence bundle.

The path is:

`receive bundle -> open verifier -> load bundle -> reconstruct`

No shared account, server, central registry, API integration, shared database, or live producer connection is required for the supported local verification path.

---

## Path C — Adopt from Existing JSON

Use:

`bridge/Structural_Receipt_Bridge_v0_5_3.py`

with:

`bridge/Structural_Receipt_Generic_Adapter_Manifest_v0_5_3.json`

The path is:

`existing JSON -> declared adapter -> WRAPPED Structural Receipt`

The source system does not need to be replaced.

---

# 60-Second Browser Start

Open:

`demo/Structural_Receipt_Reference_Demo_v0_5_3.html`

in a current browser.

Then:

1. Inspect the current Structural Receipt.
2. Review the nine purpose results.
3. Change the supported evidence state and observe purpose-specific outcomes.
4. Add supported return or refund lineage.
5. Observe the distinction between:
   - `receipt_id`
   - `structure_id`
   - `lineage_graph_id`
   - `current_lineage_state_id`
6. Export an evidence bundle.
7. Open the standalone verifier.
8. Load the exported bundle.
9. Return to the reference demo and run the full browser audit.

Open the developer console and run:

```javascript
await SR_AUDIT.runAll()
```

Expected principal result:

```text
221/221 PASS
```

Current quick regression:

`72/72 PASS`

Current permanent regression checks:

`122`

This browser result is producer-side assurance.

It is not third-party verification.

---

# Minimum Requirements

For the browser reference and standalone verifier:

- a current browser;
- JavaScript enabled;
- local file access sufficient to open the HTML files.

For the Python verifier and bridge:

- Python 3;
- access to the local repository files.

The current local reference paths do not require:

- a server;
- a database;
- a Structural Receipt account;
- a central registry;
- a cloud dependency;
- an external AI model;
- a network connection for ordinary local execution.

---

# Current Repository Layout

The intended v0.5.3 public repository layout is:

```text
STRUCTURAL RECEIPT/
│
├── README.md
├── LICENSE
├── SHA256SUMS.txt
│
├── bridge/
│   ├── Structural_Receipt_Bridge_v0_5_3.py
│   └── Structural_Receipt_Generic_Adapter_Manifest_v0_5_3.json
│
├── demo/
│   └── Structural_Receipt_Reference_Demo_v0_5_3.html
│
├── docs/
│   ├── FAQ.md
│   ├── Quickstart.md
│   ├── Structural-Receipt-Architecture-Diagram.png
│   ├── Structural_Receipt_Adoption_and_Interchange_Guide_v0_5_3.txt
│   ├── Structural_Receipt_Canonicalization_Profile_SR_CANON_1_D01_v0_5_3.txt
│   ├── Structural_Receipt_Core_Architecture_and_Deployment_Direction_v0_5_3.txt
│   ├── Structural_Receipt_Documentation_Index_v0_5_3.txt
│   ├── Structural_Receipt_Entry_Document_v0_5_3.txt
│   ├── Structural_Receipt_Purpose_Profile_Manifest_and_Evaluation_Context_v0_5_3.txt
│   └── Structural_Receipt_Verification_Guide_v0_5_3.txt
│
├── examples/
│   ├── Structural_Receipt_Examples_Index_v0_5_3.txt
│   │
│   ├── browser_to_verifier_roundtrip/
│   │   ├── Structural_Receipt_Browser_to_Verifier_Expected_Results_v0_5_3.json
│   │   ├── Structural_Receipt_Browser_to_Verifier_Roundtrip_Guide_v0_5_3.txt
│   │   ├── Structural_Receipt_Evidence_Bundle_SR-1001_Tampered_v0_5_3.json
│   │   └── Structural_Receipt_Evidence_Bundle_SR-1001_v0_5_3.json
│   │
│   └── legacy_json_to_structural_receipt/
│       ├── Structural_Receipt_Bridge_Example_Guide_v0_5_3.txt
│       ├── Structural_Receipt_Bridge_Example_Result_v0_5_3.json
│       ├── Structural_Receipt_Bridge_to_Verifier_Result_v0_5_3.json
│       ├── Structural_Receipt_Legacy_Transaction_Input_v0_5_3.json
│       ├── Structural_Receipt_WRAPPED_Evidence_Bundle_v0_5_3.json
│       └── Structural_Receipt_WRAPPED_Output_v0_5_3.json
│
├── profiles/
│   ├── Structural_Receipt_Purpose_Profile_ACCOUNTING_CLASSIFICATION_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_ARITHMETIC_CHECK_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_AUDIT_TRACE_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_EXPENSE_EVIDENCE_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_LINEAGE_CURRENT_STATE_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_PAYMENT_MATCH_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_PURCHASE_DECLARATION_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_RETURN_ELIGIBILITY_EVIDENCE_v0_5_3.json
│   ├── Structural_Receipt_Purpose_Profile_Set_Summary_v0_5_3.txt
│   ├── Structural_Receipt_Purpose_Profile_Set_v0_5_3.json
│   └── Structural_Receipt_Purpose_Profile_WARRANTY_EVIDENCE_v0_5_3.json
│
└── verify/
    ├── Structural_Receipt_Conformance_Corpus_v0_5_3.json
    ├── Structural_Receipt_Hostile_Input_Corpus_v0_5_3.json
    ├── Structural_Receipt_Independent_Verifier_v0_5_3.py
    ├── Structural_Receipt_Standalone_Verifier_v0_5_3.html
    ├── Structural_Receipt_Tamper_Corpus_v0_5_3.json
    ├── Structural_Receipt_Verification_Summary_v0_5_3.txt
    │
    └── evidence/
        ├── Structural_Receipt_Browser_Audit_Result_v0_5_3.json
        ├── Structural_Receipt_Cross_Boundary_Verification_v0_5_3.json
        └── Structural_Receipt_Separate_Implementation_Verification_v0_5_3.json
```

All paths in this Quickstart are relative to the repository root.

The root `SHA256SUMS.txt` is the authoritative exact-file checkpoint for the four selected executable artifacts.

Folder-level checksum manifests are not required.

---

# The Nine Current Purpose Profiles

The current purpose-profile family is:

`SR-PURPOSE-3`

The current release includes:

`PURCHASE_DECLARATION`

`ARITHMETIC_CHECK`

`PAYMENT_MATCH`

`EXPENSE_EVIDENCE`

`WARRANTY_EVIDENCE`

`RETURN_ELIGIBILITY_EVIDENCE`

`LINEAGE_CURRENT_STATE`

`ACCOUNTING_CLASSIFICATION`

`AUDIT_TRACE`

The same receipt may legitimately produce different outcomes for different purposes.

For example:

`PURCHASE_DECLARATION -> RESOLVED + PURCHASE_DECLARED`

`ARITHMETIC_CHECK -> RESOLVED + ARITHMETIC_CONSISTENT`

`PAYMENT_MATCH -> INCOMPLETE`

`WARRANTY_EVIDENCE -> RESOLVED + PURCHASE_EVIDENCE_AVAILABLE`

`ACCOUNTING_CLASSIFICATION -> RESOLVED + PROPOSED`

These results answer different questions.

They are not one universal receipt-validity flag.

---

# Resolution States

The current main states are:

`RESOLVED`

`INCOMPLETE`

`CONFLICT`

`UNSUPPORTED`

The evaluation layer may also report:

`NOT_EVALUATED`

The core laws are:

`missing required evidence -> INCOMPLETE`

`incompatible required evidence -> CONFLICT`

`unsupported declared boundary -> UNSUPPORTED`

The architecture preserves:

`resolved negative outcome != unresolved state`

---

# Authority Boundary

The current authority states include:

`DECLARATION_ONLY`

`CHECK_ONLY`

`EVIDENCE_ONLY`

`STATE_ONLY`

`PROPOSAL_ONLY`

`TRACE_ONLY`

For every current purpose profile:

`execution_authority = NONE`

Therefore:

`RESOLVED != APPROVED`

`RESOLVED != EXECUTED`

`producer assertion != verification authority`

---

# Trust Boundary

The current trust context separates:

`structural_integrity_state`

`provenance_state`

`issuer_authenticity_state`

`physical_occurrence_state`

`execution_authority`

For the current unauthenticated reference path:

`structural_integrity_state = RECONSTRUCTABLE`

`issuer_authenticity_state = NOT_ESTABLISHED`

`physical_occurrence_state = NOT_ESTABLISHED`

`execution_authority = NONE`

The governing principle is:

`integrity != authenticity`

`authenticity != truth`

`truth != fitness for every purpose`

---

# Lineage Quickstart

Structural Receipt preserves supported transaction change through linked lineage events.

The law is:

`change -> linked lineage event`

not:

`change -> silent historical replacement`

The current architecture separates:

`receipt_id`

`structure_id`

`lineage_graph_id`

`current_lineage_state_id`

This allows the original purchase declaration to remain addressable while later lifecycle evidence changes the bounded current state.

---

# Time and Local UI Identity Boundary

Normative time-relative resolution does not depend on the ambient wall clock.

Required time-relative context is declared explicitly through the evaluation context, including `as_of` where required.

The browser reference uses a local monotonic counter for transient new-item UI identifiers.

Those transient UI identifiers do not enter the normative Structural Receipt identity subjects.

---

# Verify an Exported Bundle in the Browser

Open:

`verify/Structural_Receipt_Standalone_Verifier_v0_5_3.html`

Choose a supported evidence bundle.

A clean supported bundle should reconstruct as:

`PASS`

A materially tampered bundle should reconstruct as:

`FAIL`

The standalone verifier also exposes a dedicated verifier audit.

Open the developer console and run:

```javascript
await SR_AUDIT.runAll()
```

Expected:

`35/35 PASS`

Quick verifier regression:

```javascript
await SR_AUDIT.quick()
```

Expected:

`12/12 PASS`

The current standalone verification boundary preserves:

`third-party verification = NOT_CLAIMED`

and:

`execution_authority = NONE`

---

# Verify an Exported Bundle with Python

From the repository root on Windows:

```bat
cd /d "D:\path\to\STRUCTURAL RECEIPT\verify"
```

Then verify one bundle:

```bat
python Structural_Receipt_Independent_Verifier_v0_5_3.py --bundle "C:\path\to\evidence_bundle.json"
```

Verbose form:

```bat
python Structural_Receipt_Independent_Verifier_v0_5_3.py --bundle "C:\path\to\evidence_bundle.json" --verbose
```

Machine-readable result:

```bat
python Structural_Receipt_Independent_Verifier_v0_5_3.py --bundle "C:\path\to\evidence_bundle.json" --json
```

Malformed JSON, duplicate object keys, unreadable input paths, and other input-stage failures return controlled `FAIL` results rather than raw Python tracebacks.

Expected principal clean-bundle output includes:

```text
STATUS: PASS
VERIFICATION SCOPE: SEPARATE_IMPLEMENTATION_RECONSTRUCTION
SEPARATE IMPLEMENTATION PATH: PASS
THIRD-PARTY VERIFICATION: NOT_CLAIMED
EXECUTION AUTHORITY: NONE
```

---

# Run the Complete Frozen Python Verification Set

From the `verify` folder:

```bat
python Structural_Receipt_Independent_Verifier_v0_5_3.py --all --verbose
```

Expected principal results:

```text
CONFORMANCE = 308/308 PASS
TAMPER = 12/12 PASS
HOSTILE INPUT = 13/13 PASS
```

The published corpus semantic identities are:

Conformance:

`9f1d59ce40ab2c4a56e0d4f3753ae41d13844cd580377bbf565ef54330df889e`

Tamper:

`3c681d0d3b3a20a16796fea0273cab0a6412ad17ecd2da433ad470a8bdc9c0e5`

Hostile Input:

`1bc1a5a52719025c9d092df825d500c7b883e0a84bd695726163798323ef6603`

These are semantic corpus identities.

They are not ordinary file checksums.

---

# Bridge Existing JSON into a WRAPPED Structural Receipt

From the `bridge` folder:

```bat
python Structural_Receipt_Bridge_v0_5_3.py --self-test
```

Expected:

```text
RESULT: 21/21 PASS
```

To convert a source JSON file:

```bat
python Structural_Receipt_Bridge_v0_5_3.py "source.json" --manifest Structural_Receipt_Generic_Adapter_Manifest_v0_5_3.json --output "Structural_Receipt_Output.json"
```

For machine-readable bridge summary output:

```bat
python Structural_Receipt_Bridge_v0_5_3.py "source.json" --manifest Structural_Receipt_Generic_Adapter_Manifest_v0_5_3.json --output "Structural_Receipt_Output.json" --summary-json
```

The current bridge preserves:

`origin_class = WRAPPED`

`semantic_equivalence = NOT_ASSUMED`

along with source provenance and unmapped-field information.

A successful bridge transformation does not establish issuer authenticity or real-world occurrence.

---

# Reproduce the Browser-to-Verifier Example

Open:

`examples/browser_to_verifier_roundtrip/`

The folder contains:

- a clean Structural Receipt evidence bundle;
- a deliberately tampered bundle;
- expected results;
- a round-trip guide.

The published clean SR-1001 reference bundle carries:

`bundle_id = 736be993cf8811d66efbfba8f8891fc396846f89188972d7d81b6769e2b8260f`

Use the standalone verifier or Python verifier to confirm:

`clean bundle -> 20/20 PASS`

`materially tampered bundle -> FAIL`

---

# Reproduce the Legacy-JSON Adoption Example

Open:

`examples/legacy_json_to_structural_receipt/`

The example demonstrates:

`existing JSON -> bridge -> WRAPPED Structural Receipt -> evidence bundle -> verification`

The example preserves:

`origin = WRAPPED`

`semantic_equivalence = NOT_ASSUMED`

and demonstrates one-sided adoption without requiring the source system to become a native Structural Receipt producer.

---

# Inspect the Published Purpose Profiles

Open:

`profiles/`

Each current purpose has a standalone JSON manifest.

The complete set is represented by:

`Structural_Receipt_Purpose_Profile_Set_v0_5_3.json`

The current purpose-manifest set identity is:

`20c55cd83bce5eb9590c757fc972880c11126249a2ed033f1f3b49249de6e381`

The governing principle is:

`the rules governing the question are themselves declared identified structure`

---

# Canonicalization Boundary

The current canonicalization profile is:

`SR-CANON-1-D01`

The current strict JSON input profile is:

`SR-JSON-INPUT-1-D01`

The strict input boundary includes:

`duplicate object key -> rejected`

`trailing non-whitespace data -> rejected`

`malformed JSON -> rejected`

`non-finite numeric value -> rejected`

The current canonicalization profile:

- deterministically orders supported object keys;
- preserves array order;
- preserves strings as supplied;
- does not perform Unicode normalization;
- uses UTF-8 bytes where hashing is required.

Canonicalization does not decide which fields belong to an identity subject.

`identity subject selection != canonicalization`

---

# Money Boundary

The current exact-money profile is:

`SR-MONEY-2DP-1-D01`

The current supported two-decimal path uses exact decimal strings.

Unsupported monetary exponents are explicit.

The law is:

`unsupported monetary scale -> UNSUPPORTED`

not:

`unsupported monetary scale -> silent coercion`

---

# Main Release Verification Sequence

A practical final local verification sequence is:

## 1. Browser reference audit

Open the demo and run:

```javascript
await SR_AUDIT.runAll()
```

Expected:

`221/221 PASS`

## 2. Standalone verifier audit

Open the standalone verifier and run:

```javascript
await SR_AUDIT.runAll()
```

Expected:

`35/35 PASS`

## 3. Python frozen release verification

From `verify/`:

```bat
python Structural_Receipt_Independent_Verifier_v0_5_3.py --all --verbose
```

Expected:

`308/308 conformance PASS`

`12/12 tamper PASS`

`13/13 hostile-input PASS`

## 4. Bridge regression test

From `bridge/`:

```bat
python Structural_Receipt_Bridge_v0_5_3.py --self-test
```

Expected:

`21/21 PASS`

## 5. Cross-boundary bundle verification

Export a bundle from the browser demo and verify it through:

`standalone browser verifier`

and:

`separate Python verifier`

A clean supported bundle should pass both paths.

A material mutation should fail reconstruction.

---

# File Checksum Verification

The root:

`SHA256SUMS.txt`

is the sole authoritative file-byte checksum manifest for the four selected executable artifacts:

`demo/Structural_Receipt_Reference_Demo_v0_5_3.html`

`verify/Structural_Receipt_Standalone_Verifier_v0_5_3.html`

`verify/Structural_Receipt_Independent_Verifier_v0_5_3.py`

`bridge/Structural_Receipt_Bridge_v0_5_3.py`

On Windows, compute one file hash with:

```bat
certutil -hashfile "demo\Structural_Receipt_Reference_Demo_v0_5_3.html" SHA256
```

Compare the resulting digest with the corresponding line in the root `SHA256SUMS.txt`.

The distinction remains:

`file checksum -> exact release bytes`

`Structural Receipt semantic identity -> profile-defined canonical subject`

---

# Recommended Reading Order

For a complete review:

1. `README.md`
2. `docs/Quickstart.md`
3. `docs/Structural_Receipt_Entry_Document_v0_5_3.txt`
4. `docs/Structural_Receipt_Adoption_and_Interchange_Guide_v0_5_3.txt`
5. `docs/Structural_Receipt_Core_Architecture_and_Deployment_Direction_v0_5_3.txt`
6. `docs/Structural_Receipt_Canonicalization_Profile_SR_CANON_1_D01_v0_5_3.txt`
7. `docs/Structural_Receipt_Purpose_Profile_Manifest_and_Evaluation_Context_v0_5_3.txt`
8. `docs/Structural_Receipt_Verification_Guide_v0_5_3.txt`
9. `docs/FAQ.md`

---

# What the Current Release Demonstrates

Within the declared v0.5.3 profile boundary:

- purpose-specific deterministic resolution;
- explicit absence, conflict, and unsupported conditions;
- identified purpose-profile manifests;
- declared identified evaluation context;
- exact supported money behavior;
- trust and authority separation;
- origin-class preservation;
- non-destructive lineage;
- portable purpose receipts;
- portable evidence bundles;
- local standalone verification;
- separate Python reconstruction;
- frozen conformance and adversarial corpora;
- one-sided bridge adoption;
- reproducible cross-boundary examples.

---

# What the Current Release Does Not Claim

The current release does not establish:

- universal financial truth;
- issuer authenticity from structural reconstruction alone;
- real-world occurrence from structural reconstruction alone;
- legal validity;
- tax correctness;
- accounting correctness;
- payment settlement authority;
- warranty approval;
- reimbursement approval;
- operational execution authority;
- production readiness by default;
- universal interoperability;
- jurisdiction-wide acceptance;
- third-party certification;
- absence of all defects;
- implemented selective disclosure.

---

# Final Summary

Start with the path that matches your situation.

To explore:

`demo/ -> open the browser reference`

To verify:

`verify/ -> load the evidence bundle locally`

To adopt from existing structured data:

`bridge/ -> produce a provenance-preserving WRAPPED Structural Receipt`

The core release principle is:

`Declare once. Resolve by purpose. Preserve through change. Verify independently.`

The adoption principle is:

`Adopt on one side. Verify on the other. Integrate only when useful.`

This is the Structural Receipt v0.5.3 Quickstart.
