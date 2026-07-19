# ⭐ FAQ — Structural Receipt

## Portable, Purpose-Resolvable and Reconstructable Evidence for Purchases and Financial Transactions

**Deterministic • Purpose-Resolved • Lineage-Preserving • Verification-Oriented**

---

## SECTION A — Purpose & Positioning

### A1. What is Structural Receipt?

Structural Receipt is a deterministic reference architecture for representing purchase and financial transaction evidence as a portable, purpose-resolvable structure.

Its primary question is:

`what is this exact available structure sufficient to establish for this exact declared purpose?`

Its core relation is:

`result_P = resolve(SR, purpose_profile_P, evaluation_context)`

where:

`SR = (C, E, D, L, O, V)`

and:

`C = declared claims and purchase structure`

`E = available evidence`

`D = declared purpose dependencies`

`L = linked transaction lineage`

`O = origin and provenance class`

`V = versioned schemas, rules, profiles, contexts, and identities`

---

### A2. What is the central principle?

`Declare once. Resolve by purpose. Preserve through change. Verify independently.`

The current adoption principle is:

`Adopt on one side. Verify on the other. Integrate only when useful.`

---

### A3. What problem does Structural Receipt address?

The same transaction is often interpreted repeatedly by different downstream systems.

The recurring pattern is:

`transaction evidence -> local reconstruction -> local interpretation -> local conclusion`

Repeated across systems, this can produce multiple application-specific versions of transaction meaning.

Structural Receipt explores a different authority model:

`declared evidence structure + identified purpose profile + declared evaluation context -> bounded supported result`

The goal is not to eliminate downstream applications.

The goal is to prevent repeated application-specific interpretation from remaining the sole authority over what the transaction evidence supports.

---

### A4. Is Structural Receipt just a digital receipt format?

No.

A visual or machine-readable receipt format primarily answers:

`what transaction data is represented?`

Structural Receipt additionally asks:

`what does this available evidence support for this declared purpose?`

Its current architecture combines:

`portable transaction evidence`

`+ explicit dependencies`

`+ identified purpose profiles`

`+ declared evaluation context`

`+ authority boundaries`

`+ non-destructive lineage`

`+ reconstructable identities`

---

### A5. Is Structural Receipt a new receipt layout?

No.

The human-readable receipt is one possible projection.

Structural Receipt is not defined by a picture, PDF, page layout, or screen presentation.

The architecture separates:

`presentation != structural identity`

---

### A6. Is Structural Receipt a payment network?

No.

It does not execute payments or establish settlement authority.

The current profiles preserve:

`payment evidence != settlement authority`

and:

`execution_authority = NONE`

---

### A7. Is Structural Receipt an accounting or tax engine?

No.

The current accounting profile may produce a bounded deterministic proposal.

It does not approve or post an accounting entry.

The current architecture preserves:

`RESOLVED + PROPOSED != APPROVED OR POSTED`

Tax correctness, legal correctness, accounting correctness, and jurisdiction-wide acceptance are not claimed.

---

### A8. Is Structural Receipt a blockchain?

No.

The current architecture uses deterministic identities, lineage, evidence bundles, and reconstruction.

It does not require a blockchain or distributed ledger.

---

### A9. Is Structural Receipt a universal truth oracle?

No.

The project explicitly separates:

`integrity != authenticity`

`authenticity != truth`

`truth != fitness for every purpose`

A structurally reconstructable receipt is not automatically proof that the real-world transaction occurred.

---

### A10. What is the architectural contribution?

The bounded contribution is the combined architecture:

`purpose-specific deterministic resolution`

`+ explicit incompleteness`

`+ explicit conflict`

`+ origin-aware evidence`

`+ identified purpose profiles`

`+ declared evaluation context`

`+ non-destructive lineage`

`+ presentation-independent identity`

`+ portable bounded verification`

`+ adapter-first interoperability`

No claim is made that every individual mechanism is new.

---

## SECTION B — Adoption & Verification Without Integration

### B1. Do both sides of a transaction need to adopt Structural Receipt at the same time?

No.

The current release is explicitly designed around one-sided adoption.

The adoption progression is:

`one adopting side -> immediate bounded utility`

`two adopting sides -> richer interoperability`

`many adopting sides -> broader portability`

---

### B2. What should I do if I receive a Structural Receipt evidence bundle?

Open:

`verify/Structural_Receipt_Standalone_Verifier_v0_5_3.html`

Then load the bundle.

The supported path is:

`receive bundle -> open verifier -> load bundle -> reconstruct`

No shared account, server, API integration, shared database, or live producer connection is required for the bounded local verification path.

---

### B3. What should I do if I already have transaction data in JSON?

Use the bridge.

The adoption path is:

`existing JSON -> declared adapter -> WRAPPED Structural Receipt`

The bridge is:

`bridge/Structural_Receipt_Bridge_v0_5_3.py`

The default adapter manifest is:

`bridge/Structural_Receipt_Generic_Adapter_Manifest_v0_5_3.json`

---

### B4. Do I need to replace my current receipt system?

No.

The recommended producer-side adoption model is a sidecar.

`existing transaction system -> Structural Receipt sidecar -> portable evidence bundle`

The existing receipt, application, workflow, PDF, email, or other operational artifact may remain.

---

### B5. What is verification without integration?

It means a recipient can reconstruct the bounded structural claims carried by a supported evidence bundle without relying on the producer application or producer PASS assertions as verification authority.

The current release supports:

`portable bundle -> standalone browser verifier`

and:

`portable bundle -> separate Python verifier`

---

### B6. Does Structural Receipt require a central registry?

No.

The current local verification path does not require a central Structural Receipt registry.

---

### B7. Does Structural Receipt require a cloud service?

No.

The current browser demo, standalone verifier, Python verifier, and bridge are designed for local use.

---

### B8. Does the bridge claim that an existing source format is semantically identical to Structural Receipt?

No.

The bridge explicitly preserves:

`semantic_equivalence = NOT_ASSUMED`

Successful conversion does not silently become a claim of complete semantic equivalence.

---

### B9. What does the bridge preserve?

The current bridge preserves information including:

`source artifact identity`

`source profile`

`origin_class = WRAPPED`

`unmapped source fields`

`declared warnings`

`semantic_equivalence = NOT_ASSUMED`

---

### B10. What are the three main adoption paths?

Producer-side:

`existing system -> Structural Receipt sidecar -> portable evidence bundle -> recipient verifier`

Verifier-side:

`existing structured source -> bridge -> WRAPPED Structural Receipt -> verification or purpose resolution`

Native end-to-end:

`native Structural Receipt producer -> portable evidence bundle -> Structural Receipt-aware verifier`

---

## SECTION C — Purpose Resolution

### C1. Why not ask only whether a receipt is valid?

Because one universal validity flag is too broad.

The same receipt may be:

- complete as a purchase declaration;
- arithmetically consistent;
- unmatched to independent payment evidence;
- sufficient as bounded proof-of-purchase evidence;
- incomplete for one expense purpose;
- affected by a later return or refund;
- structurally intact but unauthenticated as to issuer.

Those conditions may all exist at the same time.

---

### C2. What purpose profiles are included in v0.5.3?

The current release contains nine purpose profiles:

`PURCHASE_DECLARATION`

`ARITHMETIC_CHECK`

`PAYMENT_MATCH`

`EXPENSE_EVIDENCE`

`WARRANTY_EVIDENCE`

`RETURN_ELIGIBILITY_EVIDENCE`

`LINEAGE_CURRENT_STATE`

`ACCOUNTING_CLASSIFICATION`

`AUDIT_TRACE`

---

### C3. What does `PURCHASE_DECLARATION` answer?

It asks whether the supported receipt structure contains a complete bounded purchase declaration under the current profile.

Its authority is declaration-only.

It does not establish independent payment proof or issuer authenticity.

---

### C4. What does `ARITHMETIC_CHECK` answer?

It checks the supported arithmetic relation among declared item values, discounts, tax, charges, and total.

A resolved arithmetic result is a bounded consistency result.

It is not proof that the transaction occurred.

---

### C5. What does `PAYMENT_MATCH` answer?

It evaluates the declared payment evidence required by the current profile.

It may resolve as matched, not matched, incomplete, or conflicting depending on the available supported structure.

Payment matching does not establish delivery, accounting approval, tax treatment, or settlement authority.

---

### C6. What does `WARRANTY_EVIDENCE` answer?

It asks whether the supported purchase structure provides the bounded proof-of-purchase evidence required by the current example profile.

It does not approve a warranty claim.

---

### C7. What does `RETURN_ELIGIBILITY_EVIDENCE` answer?

It evaluates the supported return-related dependencies under the declared evaluation context and current lineage state.

It does not execute a return or refund.

---

### C8. What does `LINEAGE_CURRENT_STATE` answer?

It resolves the bounded current transaction state from supported linked lineage events.

The result is not a universal legal or accounting state.

---

### C9. What does `ACCOUNTING_CLASSIFICATION` answer?

The current profile can produce a deterministic bounded proposal.

The authority state is:

`PROPOSAL_ONLY`

The execution authority is:

`NONE`

---

### C10. What does `AUDIT_TRACE` answer?

It evaluates whether the supported structural trace can be reconstructed under the current profile.

It is not third-party certification.

---

## SECTION D — Resolution States, Authority & Trust

### D1. What are the current main resolution states?

The current architecture uses:

`RESOLVED`

`INCOMPLETE`

`CONFLICT`

`UNSUPPORTED`

The evaluation layer may also report:

`NOT_EVALUATED`

---

### D2. What does `INCOMPLETE` mean?

A required dependency for the declared purpose is missing.

The governing law is:

`missing required evidence -> INCOMPLETE`

The system does not silently assume the missing fact is true.

---

### D3. What does `CONFLICT` mean?

Required supported evidence is incompatible under the current profile.

The governing law is:

`incompatible required evidence -> CONFLICT`

The resolver does not silently choose whichever record arrived last.

---

### D4. What does `UNSUPPORTED` mean?

The requested evaluation falls outside the current implemented profile boundary.

For example:

`unsupported monetary scale -> UNSUPPORTED`

rather than silent coercion.

---

### D5. Is a resolved negative result the same as incomplete?

No.

The architecture preserves:

`resolved negative outcome != unresolved state`

A deterministic negative answer is different from missing evidence.

---

### D6. What authority states are used?

Current authority states include:

`DECLARATION_ONLY`

`CHECK_ONLY`

`EVIDENCE_ONLY`

`STATE_ONLY`

`PROPOSAL_ONLY`

`TRACE_ONLY`

---

### D7. What is the execution authority of the current purpose profiles?

`NONE`

A resolved purpose result is evidence.

It is not an operational permission to execute a payment, reimbursement, posting, refund, warranty action, or other downstream operation.

---

### D8. Does `RESOLVED` mean `AUTHENTICATED`?

No.

The architecture preserves:

`RESOLVED != AUTHENTICATED`

---

### D9. Does structural integrity prove real-world occurrence?

No.

The current unauthenticated reference path preserves:

`structural_integrity_state = RECONSTRUCTABLE`

`issuer_authenticity_state = NOT_ESTABLISHED`

`physical_occurrence_state = NOT_ESTABLISHED`

`execution_authority = NONE`

---

### D10. What is the central trust principle?

`do not claim more than the declared and reconstructed structure can support`

---

## SECTION E — Lineage & Identity

### E1. Why does Structural Receipt use lineage?

A transaction may change after the original purchase through:

- return;
- partial return;
- refund;
- partial refund;
- credit;
- correction;
- another supported lifecycle event.

The architecture preserves change as linked events rather than silently rewriting history.

---

### E2. What is the core lineage law?

`change -> linked lineage event`

not:

`change -> silent historical replacement`

---

### E3. What is `receipt_id`?

It identifies the canonical purchase declaration subject under the applicable profile.

Later supported lineage events do not silently rewrite the original receipt identity.

---

### E4. What is `structure_id`?

It identifies the complete current Structural Receipt subject under the current identity profile.

---

### E5. What is `lineage_graph_id`?

It identifies the supported root receipt and canonical linked lineage event set.

It changes when the supported lineage graph changes.

---

### E6. What is `current_lineage_state_id`?

It identifies the bounded resolved current lineage state.

It may change when supported lifecycle events change the current economic state.

---

### E7. Why are these identities separate?

Because they answer different questions.

The architecture preserves:

`original declaration identity`

separately from:

`complete current structure identity`

separately from:

`lineage graph identity`

separately from:

`bounded current state identity`

---

### E8. Does a refund erase the original purchase?

No.

The original purchase remains addressable.

The refund becomes linked lineage evidence.

---

## SECTION F — Purpose Profiles, Context & Canonicalization

### F1. Are purpose rules identified?

Yes.

Each current purpose profile is published as a canonical identified manifest.

The governing relation is:

`the rules governing the question are themselves declared identified structure`

---

### F2. What is `purpose_profile_id`?

It is the deterministic identity of one canonical purpose-profile manifest subject.

Conceptually:

`purpose_profile_id = SHA256(canonical(purpose_profile_manifest_subject))`

---

### F3. What is `purpose_manifest_set_id`?

It identifies the complete current set of purpose profiles.

The current v0.5.3 set identity is:

`20c55cd83bce5eb9590c757fc972880c11126249a2ed033f1f3b49249de6e381`

---

### F4. Why is evaluation context explicit?

Some questions depend on declared context such as an `as_of` date.

The architecture avoids hidden dependence on the ambient current clock.

The governing relation is:

`time-relative question + explicit as_of -> deterministic supported result`

---

### F5. What does the current evaluation context contain?

The current evaluation-context identity subject contains:

`profile = SR-EVALUATION-CONTEXT-1-D01`

`as_of`

`jurisdiction_profile`

`currency_profile`.

---

### F6. Does the resolver silently use the wall clock?

Not for normative identity construction or the current time-relative purpose profiles.

Required time-relative context must be explicit.

The browser reference also uses a local monotonic counter for transient new-item UI identifiers. Those identifiers do not enter the normative Structural Receipt identity subjects.

---

### F7. What canonicalization profile is used?

`SR-CANON-1-D01`

The companion strict input profile is:

`SR-JSON-INPUT-1-D01`

---

### F8. Are duplicate JSON object keys accepted?

No.

The current strict input boundary preserves:

`duplicate object key -> rejected input`

---

### F9. Does the current canonicalization profile normalize Unicode?

No.

The current profile preserves strings as supplied to the canonical subject.

Therefore:

`different Unicode code-point sequences -> potentially different canonical subjects`

even where rendering appears similar.

---

### F10. Does Structural Receipt use ordinary floating-point values for normative money?

No.

The current exact-money path uses exact decimal strings.

The current supported profile is:

`SR-MONEY-2DP-1-D01`

---

### F11. What happens with an unsupported currency exponent?

The current architecture preserves:

`unsupported monetary scale -> UNSUPPORTED`

It does not silently reinterpret the value using the two-decimal profile.

---

## SECTION G — Origin & Provenance

### G1. What origin classes are used?

The current architecture distinguishes:

`NATIVE`

`WRAPPED`

`DERIVED`

---

### G2. What is `NATIVE`?

A native Structural Receipt is created from declared transaction structure at origin.

---

### G3. What is `WRAPPED`?

A wrapped Structural Receipt is created from an existing structured source through a declared adapter.

The current bridge produces the `WRAPPED` origin class.

---

### G4. What is `DERIVED`?

A derived Structural Receipt is reconstructed from a presentation or manually supplied source.

Derived structure does not silently become native structure.

---

### G5. Why preserve origin class?

Because provenance affects what can honestly be claimed about the resulting structure.

The architecture preserves:

`NATIVE != WRAPPED != DERIVED`

---

### G6. Are imported origin classes free-form?

No.

The active receipt boundary accepts only:

`NATIVE`

`WRAPPED`

`DERIVED`

An unsupported imported origin class is rejected before admission into active receipt state.

Displayed origin labels are also escaped defensively at the presentation boundary.

---

## SECTION H — Verification & Assurance

### H1. What verification paths are included?

The current release includes:

- producer-side browser audit;
- standalone browser bundle verification;
- separate Python reconstruction;
- frozen conformance corpus;
- tamper corpus;
- hostile-input corpus;
- bridge self-test;
- published verification evidence.

---

### H2. What is the current browser audit result?

The current demonstrated full browser release audit is:

`221/221 PASS`

The current quick regression result is:

`72/72 PASS`

The browser release also carries:

`122 permanent regression checks`

The standalone verifier has its own dedicated audit:

`35/35 PASS`

with a quick verifier regression gate of:

`12/12 PASS`

and:

`23 permanent verifier regressions`

---

### H3. What is the current conformance result?

The current frozen conformance result is:

`308/308 PASS`

on the browser path and:

`308/308 PASS`

on the separate Python path.

---

### H4. What is the current tamper result?

The current tamper corpus result is:

`12/12 PASS`

on both the browser and separate Python paths.

---

### H5. What is the current hostile-input result?

The current hostile-input corpus result is:

`13/13 PASS`

on both the browser and separate Python paths.

---

### H6. What is the current bridge self-test result?

`21/21 PASS`

---

### H7. Has a browser-exported bundle been verified through the standalone verifier?

Yes.

The demonstrated path is:

`browser producer -> exported evidence bundle -> standalone verifier -> PASS`

---

### H8. Has a browser-exported bundle been verified through the Python verifier?

Yes.

The demonstrated path is:

`browser producer -> exported evidence bundle -> separate Python verifier -> PASS`

---

### H9. Is the separate Python verifier third-party verification?

No.

It is a separate implementation path within the project release.

The correct claim is:

`separate implementation reconstruction = demonstrated`

The project preserves:

`third-party verification = NOT_CLAIMED`

---

### H10. Why distinguish producer assertion from verification authority?

Because a producer can incorrectly label its own output as valid.

The governing principle is:

`producer assertion != verification authority`

The verifier reconstructs supported identities and checks rather than trusting a producer-generated PASS label.

---

### H11. What does the standalone verifier prove?

Within the current supported profiles, it reconstructs the declared Structural Receipt evidence bundle identities and checks.

It does not establish issuer authenticity, physical occurrence, legal validity, tax correctness, accounting correctness, or execution authority.

The current verifier paths also reject malformed JSON, duplicate object keys, unsupported input boundaries, and invalid imported item quantities rather than silently accepting them.

The browser producer additionally rejects unsupported imported origin classes before active-state admission.

---

### H12. What does the root `SHA256SUMS.txt` verify?

The root checksum file is the authoritative exact-byte checkpoint for the four selected executable artifacts:

`demo/Structural_Receipt_Reference_Demo_v0_5_3.html`

`verify/Structural_Receipt_Standalone_Verifier_v0_5_3.html`

`verify/Structural_Receipt_Independent_Verifier_v0_5_3.py`

`bridge/Structural_Receipt_Bridge_v0_5_3.py`

This is separate from semantic Structural Receipt identities.

The distinction is:

`semantic identity != file checksum`

---

### H13. Why are folder-level checksum files not required?

The release uses one maintainable root checksum manifest for the primary executable artifacts.

The frozen corpora and purpose profiles already carry their own semantic identities under the project profiles.

---

## SECTION I — Current Repository & Practical Use

### I1. Where is the main browser reference?

`demo/Structural_Receipt_Reference_Demo_v0_5_3.html`

---

### I2. Where is the standalone verifier?

`verify/Structural_Receipt_Standalone_Verifier_v0_5_3.html`

---

### I3. Where is the Python verifier?

`verify/Structural_Receipt_Independent_Verifier_v0_5_3.py`

---

### I4. Where is the bridge?

`bridge/Structural_Receipt_Bridge_v0_5_3.py`

---

### I5. Where are the purpose profiles?

`profiles/`

The folder contains all nine standalone purpose-profile manifests and the complete identified purpose-profile set.

---

### I6. Where are reproducible examples?

`examples/`

The current examples demonstrate:

`browser -> verifier`

and:

`existing JSON -> bridge -> WRAPPED Structural Receipt`

---

### I7. Where should I start reading?

Recommended order:

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

## SECTION J — Boundaries & Future Work

### J1. Is Structural Receipt production-certified?

No.

Production readiness is not claimed by default.

Operational deployment requires appropriate domain-specific review, testing, security assessment, policy review, and integration validation.

---

### J2. Does Structural Receipt establish issuer authenticity?

Not under the current unauthenticated reference profiles.

The current state is:

`issuer_authenticity_state = NOT_ESTABLISHED`

---

### J3. Does Structural Receipt establish that a real-world transaction occurred?

Not from structural reconstruction alone.

The current state is:

`physical_occurrence_state = NOT_ESTABLISHED`

---

### J4. Does Structural Receipt provide execution authority?

No.

The current purpose profiles preserve:

`execution_authority = NONE`

---

### J5. Is selective disclosure implemented?

No.

Purpose-limited disclosure remains a future architecture direction.

The current release does not claim implementation of:

`SR-COMMIT-1-D01`

`SR-DISCLOSE-1-D01`

`SR-PDC-1-D01`

---

### J6. What is the future disclosure direction?

The proposed direction is:

`purpose-scoped resolution -> purpose-scoped disclosure`

with:

`full-document disclosure -> no longer the sole path to purpose-specific verification`

This remains a future architecture direction.

---

### J7. Does a future commitment prove authenticity?

No.

The future direction preserves:

`committed != authenticated`

---

### J8. Is disclosed-subset verification the same as full-receipt verification?

No.

The future direction preserves:

`disclosed-subset verification != full-receipt verification`

---

### J9. What is the strongest current bounded claim?

Within the declared frozen v0.5.3 profiles, Structural Receipt demonstrates that claims, evidence, dependencies, origin, purpose, context, lineage, authority, and verification identities can be represented explicitly enough for supported downstream questions to be resolved deterministically and reconstructed across separate project-produced implementation paths without relying on producer-generated PASS assertions as verification authority.

---

## ⭐ Final Summary

Structural Receipt asks:

`what does this declared transaction evidence support for this declared purpose?`

Its core model is:

`SR = (C, E, D, L, O, V)`

Its resolution relation is:

`result_P = resolve(SR, purpose_profile_P, evaluation_context)`

Its absence law is:

`missing required evidence -> INCOMPLETE`

Its conflict law is:

`incompatible required evidence -> CONFLICT`

Its lineage law is:

`change -> linked lineage event`

Its trust boundary is:

`integrity != authenticity != truth`

Its authority boundary is:

`purpose result != execution authority`

Its adoption principle is:

`Adopt on one side. Verify on the other. Integrate only when useful.`

Its release principle is:

`Declare once. Resolve by purpose. Preserve through change. Verify independently.`

**This is Structural Receipt.**
