#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

PROFILE = {'architecture': 'SR-CORE-5',
 'resolver': 'SR-RESOLVER-5-D01',
 'canonicalization': 'SR-CANON-1-D01',
 'dependency': 'SR-DEPENDENCY-1-D01',
 'authority': 'SR-AUTHORITY-1-D01',
 'lineage': 'SR-LINEAGE-1-D01',
 'lineage_graph': 'SR-LINEAGE-GRAPH-1-D01',
 'money': 'SR-MONEY-2DP-1-D01',
 'purpose': 'SR-PURPOSE-3',
 'purpose_receipt': 'SR-PURPOSE-RECEIPT-1-D01',
 'bundle': 'SR-EVIDENCE-BUNDLE-2-D01',
 'verifier': 'SR-VERIFIER-2-D01',
 'independent_verifier': 'SR-INDEPENDENT-VERIFIER-2-D01',
 'conformance': 'SR-CONFORMANCE-2-D01',
 'corpus': 'SR-CONFORMANCE-CORPUS-2-D01',
 'tamper_corpus': 'SR-TAMPER-CORPUS-2-D01',
 'adapter': 'SR-ADAPTER-1-D01',
 'schema': 'SR-RECEIPT-2-D02',
 'version': '0.5.3',
 'purpose_manifest': 'SR-PURPOSE-MANIFEST-1-D01',
 'evaluation_context': 'SR-EVALUATION-CONTEXT-1-D01',
 'trust_context': 'SR-TRUST-CONTEXT-1-D01',
 'money_context': 'SR-MONEY-CONTEXT-1-D01',
 'strict_json': 'SR-JSON-INPUT-1-D01',
 'hostile_corpus': 'SR-HOSTILE-INPUT-CORPUS-1-D01'}

PURPOSES = ['PURCHASE_DECLARATION',
 'ARITHMETIC_CHECK',
 'PAYMENT_MATCH',
 'EXPENSE_EVIDENCE',
 'WARRANTY_EVIDENCE',
 'RETURN_ELIGIBILITY_EVIDENCE',
 'LINEAGE_CURRENT_STATE',
 'ACCOUNTING_CLASSIFICATION',
 'AUDIT_TRACE']

PURPOSE_MANIFEST = {'PURCHASE_DECLARATION': {'profile': 'SR-PURCHASE-1-D01',
                          'question': 'Is the bounded purchase declaration structurally complete?',
                          'authority_state': 'DECLARATION_ONLY',
                          'required_dependencies': ['merchant', 'receipt_number', 'transaction_date', 'currency', 'item_lines', 'declared_total'],
                          'limitations': 'A complete declaration does not prove payment, delivery, issuer authenticity, or physical occurrence.',
                          'manifest_version': '1.0.0',
                          'context_requirements': [],
                          'execution_authority': 'NONE'},
 'ARITHMETIC_CHECK': {'profile': 'SR-ARITHMETIC-1-D01',
                      'question': 'Is the declared total arithmetically consistent with the declared monetary structure?',
                      'authority_state': 'CHECK_ONLY',
                      'required_dependencies': ['item_lines', 'discount', 'tax', 'charges', 'declared_total'],
                      'limitations': 'Arithmetic consistency does not establish authenticity or payment.',
                      'manifest_version': '1.0.0',
                      'context_requirements': [],
                      'execution_authority': 'NONE'},
 'PAYMENT_MATCH': {'profile': 'SR-PAYMENT-MATCH-1-D01',
                   'question': 'Does available independent payment evidence match the declared amount and currency?',
                   'authority_state': 'EVIDENCE_ONLY',
                   'required_dependencies': ['declared_total', 'transaction_currency', 'payment_reference', 'payment_amount', 'payment_currency'],
                   'limitations': 'A match is evidence compatibility only. It does not execute settlement or prove finality.',
                   'manifest_version': '1.0.0',
                   'context_requirements': [],
                   'execution_authority': 'NONE'},
 'EXPENSE_EVIDENCE': {'profile': 'SR-EXPENSE-EVIDENCE-1-D01',
                      'question': 'Does the receipt satisfy the bounded example expense-evidence profile?',
                      'authority_state': 'EVIDENCE_ONLY',
                      'required_dependencies': ['purchase_declaration', 'business_purpose'],
                      'limitations': 'This is not a universal reimbursement policy and does not approve payment.',
                      'manifest_version': '1.0.0',
                      'context_requirements': [],
                      'execution_authority': 'NONE'},
 'WARRANTY_EVIDENCE': {'profile': 'SR-WARRANTY-EVIDENCE-1-D01',
                       'question': 'Is bounded proof-of-purchase evidence available for a declared item reference?',
                       'authority_state': 'EVIDENCE_ONLY',
                       'required_dependencies': ['purchase_declaration', 'warranty_item_reference', 'referenced_item_exists'],
                       'limitations': 'This does not establish manufacturer coverage, claim eligibility, or warranty approval.',
                       'manifest_version': '1.0.0',
                       'context_requirements': ['as_of'],
                       'execution_authority': 'NONE'},
 'RETURN_ELIGIBILITY_EVIDENCE': {'profile': 'SR-RETURN-EVIDENCE-1-D01',
                                 'question': 'Does the bounded receipt and lineage structure support the requested return amount?',
                                 'authority_state': 'EVIDENCE_ONLY',
                                 'required_dependencies': ['purchase_declaration', 'lineage_consistency', 'return_request_amount', 'remaining_returnable_value'],
                                 'limitations': 'This does not approve a merchant return or override external return policy.',
                                 'manifest_version': '1.0.0',
                                 'context_requirements': ['as_of'],
                                 'execution_authority': 'NONE'},
 'LINEAGE_CURRENT_STATE': {'profile': 'SR-LINEAGE-STATE-1-D01',
                           'question': 'What bounded current transaction state follows from compatible linked adjustments?',
                           'authority_state': 'STATE_ONLY',
                           'required_dependencies': ['declared_total', 'lineage_events'],
                           'limitations': 'The current state is resolved only within the supported return, refund, and credit model.',
                           'manifest_version': '1.0.0',
                           'context_requirements': ['as_of'],
                           'execution_authority': 'NONE'},
 'ACCOUNTING_CLASSIFICATION': {'profile': 'SR-ACCOUNTING-PROPOSAL-1-D01',
                               'question': 'Can the available transaction evidence support a bounded accounting-classification proposal?',
                               'authority_state': 'PROPOSAL_ONLY',
                               'required_dependencies': ['purchase_declaration'],
                               'limitations': 'RESOLVED means the proposal question was resolved. It never means APPROVED, POSTED, or authoritative accounting treatment.',
                               'manifest_version': '1.0.0',
                               'context_requirements': [],
                               'execution_authority': 'NONE'},
 'AUDIT_TRACE': {'profile': 'SR-AUDIT-TRACE-1-D01',
                 'question': 'Can the structural identities and linked events be reconstructed into a bounded audit trace?',
                 'authority_state': 'TRACE_ONLY',
                 'required_dependencies': ['receipt_identity', 'structure_identity', 'origin_class', 'lineage_event_identities'],
                 'limitations': 'A reconstructable trace is producer-side evidence, not independent audit assurance or certification.',
                 'manifest_version': '1.0.0',
                 'context_requirements': [],
                 'execution_authority': 'NONE'}}

CURRENCY_EXPONENTS = {'USD': 2, 'INR': 2, 'EUR': 2, 'GBP': 2, 'AUD': 2, 'SGD': 2, 'JPY': 0, 'KWD': 3}


def canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NON_FINITE_NUMBER")
        if value == 0:
            return 0
        if value.is_integer():
            return int(value)
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(canonicalize(value), ensure_ascii=False, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_value(value: Any) -> str:
    return sha256_text(canonical_json(value))


def parse_minor(value: Any) -> int:
    text = str(value if value is not None else "").strip()
    import re
    if not re.fullmatch(r"-?\d+(\.\d{1,2})?", text):
        raise ValueError("INVALID_MONEY")
    negative = text.startswith("-")
    if negative:
        text = text[1:]
    whole, _, frac = text.partition(".")
    minor = int(whole) * 100 + int((frac + "00")[:2])
    return -minor if negative else minor


def format_minor(value: int) -> str:
    negative = value < 0
    value = abs(value)
    return f"{'-' if negative else ''}{value // 100}.{value % 100:02d}"


def purchase_core(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": r["profile"],
        "schema_version": r["schema_version"],
        "ruleset_version": r["ruleset_version"],
        "origin": r["origin"],
        "transaction": r["transaction"],
    }


def full_core(r: dict[str, Any]) -> dict[str, Any]:
    core = purchase_core(r)
    core.update({"evidence": r["evidence"], "purpose_context": r["purpose_context"], "lineage": r["lineage"]})
    return core


def receipt_id(r: dict[str, Any]) -> str:
    return hash_value(purchase_core(r))


def structure_id(r: dict[str, Any]) -> str:
    return hash_value(full_core(r))


def lineage_event_id(event: dict[str, Any]) -> str:
    return hash_value(event)


def computed_subtotal(r: dict[str, Any]) -> int:
    return sum(int(item["qty"]) * parse_minor(item["unit_price"]) for item in r["transaction"]["items"])


def expected_total(r: dict[str, Any]) -> int:
    tx = r["transaction"]
    return computed_subtotal(r) - parse_minor(tx["discount"]) + parse_minor(tx["tax"]) + parse_minor(tx["charges"])


def dependency_coverage(required: list[str], satisfied: list[str]) -> int:
    if not required:
        return 100
    return round(len(set(satisfied)) / len(required) * 100)


def canonical_bigint_metrics(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical_bigint_metrics(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical_bigint_metrics(item) for item in value]
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    return value


def result_hash_value(result: dict[str, Any]) -> dict[str, Any]:
    output = copy.deepcopy(result)
    if "metrics" in output:
        output["metrics"] = canonical_bigint_metrics(output["metrics"])
    return output


def make_result(purpose: str, resolution_state: str, purpose_outcome: str, *, reasons=None, evidence_refs=None, satisfied_dependencies=None, missing_dependencies=None, conflicting_dependencies=None, coverage=None, metrics=None, authority_state=None) -> dict[str, Any]:
    reasons = reasons or []
    evidence_refs = evidence_refs or []
    satisfied_dependencies = satisfied_dependencies or []
    missing_dependencies = missing_dependencies or []
    conflicting_dependencies = conflicting_dependencies or []
    manifest = PURPOSE_MANIFEST[purpose]
    required = list(manifest["required_dependencies"])
    result = {
        "evaluation_status": "EVALUATED",
        "resolution_state": resolution_state,
        "purpose_outcome": purpose_outcome,
        "authority_state": authority_state or manifest["authority_state"],
        "execution_authority": "NONE",
        "reasons": reasons,
        "evidence_refs": evidence_refs,
        "required_dependencies": required,
        "satisfied_dependencies": satisfied_dependencies,
        "missing_dependencies": missing_dependencies,
        "conflicting_dependencies": conflicting_dependencies,
        "coverage": dependency_coverage(required, satisfied_dependencies) if coverage is None else coverage,
    }
    if metrics is not None:
        result["metrics"] = metrics
    return result


def resolve_purchase(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "PURCHASE_DECLARATION"
    sat, missing = [], []
    tx = r["transaction"]
    for present, dep in [
        (str(tx.get("merchant", "")).strip(), "merchant"),
        (str(tx.get("receipt_number", "")).strip(), "receipt_number"),
        (tx.get("date"), "transaction_date"),
        (tx.get("currency"), "currency"),
    ]:
        (sat if present else missing).append(dep)
    items_ok = isinstance(tx.get("items"), list) and len(tx["items"]) > 0
    if items_ok:
        for item in tx["items"]:
            try:
                qty = item.get("qty")
                qty_num = float(qty)
                if not str(item.get("description", "")).strip() or not qty_num.is_integer() or qty_num <= 0:
                    items_ok = False
                    break
                parse_minor(item.get("unit_price"))
            except Exception:
                items_ok = False
                break
    (sat if items_ok else missing).append("item_lines")
    try:
        parse_minor(tx.get("declared_total"))
        sat.append("declared_total")
    except Exception:
        missing.append("declared_total")
    if missing:
        return make_result(purpose, "INCOMPLETE", "PURCHASE_DECLARATION_INCOMPLETE", reasons=["Missing or invalid required purchase structure: " + ", ".join(missing)], satisfied_dependencies=sat, missing_dependencies=missing)
    return make_result(purpose, "RESOLVED", "PURCHASE_DECLARED", reasons=["All required bounded purchase declaration fields are present."], evidence_refs=[receipt_id(r)], satisfied_dependencies=sat)


def resolve_arithmetic(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "ARITHMETIC_CHECK"
    sat, missing = [], []
    try:
        if r["transaction"].get("items"):
            computed_subtotal(r)
            sat.append("item_lines")
        else:
            missing.append("item_lines")
    except Exception:
        missing.append("item_lines")
    for dep, key in [("discount", "discount"), ("tax", "tax"), ("charges", "charges"), ("declared_total", "declared_total")]:
        try:
            parse_minor(r["transaction"].get(key))
            sat.append(dep)
        except Exception:
            missing.append(dep)
    if missing:
        return make_result(purpose, "INCOMPLETE", "ARITHMETIC_INPUT_INCOMPLETE", reasons=["One or more required monetary fields are invalid."], satisfied_dependencies=sat, missing_dependencies=missing)
    exp = expected_total(r)
    dec = parse_minor(r["transaction"]["declared_total"])
    if dec == exp:
        return make_result(purpose, "RESOLVED", "ARITHMETIC_CONSISTENT", reasons=[f"Declared total {format_minor(dec)} equals computed total {format_minor(exp)}."], satisfied_dependencies=sat)
    return make_result(purpose, "RESOLVED", "ARITHMETIC_INCONSISTENT", reasons=[f"Declared total {format_minor(dec)} does not equal computed total {format_minor(exp)}."], satisfied_dependencies=sat)


def resolve_payment(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "PAYMENT_MATCH"
    sat = ["declared_total", "transaction_currency"]
    missing = []
    payments = r.get("evidence", {}).get("payment", [])
    if not payments:
        return make_result(purpose, "INCOMPLETE", "PAYMENT_EVIDENCE_MISSING", reasons=["No independent payment evidence is attached."], satisfied_dependencies=sat, missing_dependencies=["payment_reference", "payment_amount", "payment_currency"])
    normalized = [f"{x.get('reference')}|{x.get('amount')}|{x.get('currency')}" for x in payments]
    amount_currency = [f"{x.get('amount')}|{x.get('currency')}" for x in payments]
    if len(set(normalized)) > 1 and len(set(amount_currency)) > 1:
        return make_result(purpose, "CONFLICT", "PAYMENT_EVIDENCE_CONFLICT", reasons=["Attached payment evidence contains incompatible amount or currency declarations."], satisfied_dependencies=sat + ["payment_reference"], conflicting_dependencies=["payment_amount", "payment_currency"], evidence_refs=[x.get("reference") for x in payments if x.get("reference")])
    x = payments[0]
    if x.get("reference"):
        sat.append("payment_reference")
    else:
        missing.append("payment_reference")
    try:
        parse_minor(x.get("amount"))
        sat.append("payment_amount")
    except Exception:
        missing.append("payment_amount")
    if x.get("currency"):
        sat.append("payment_currency")
    else:
        missing.append("payment_currency")
    if missing:
        return make_result(purpose, "INCOMPLETE", "PAYMENT_EVIDENCE_INVALID", reasons=["Payment evidence is missing one or more required matching fields."], satisfied_dependencies=sat, missing_dependencies=missing, evidence_refs=[x["reference"]] if x.get("reference") else [])
    same_currency = x["currency"] == r["transaction"]["currency"]
    same_amount = parse_minor(x["amount"]) == parse_minor(r["transaction"]["declared_total"])
    if same_currency and same_amount:
        return make_result(purpose, "RESOLVED", "MATCHED", reasons=["Independent payment amount and currency match the declared transaction."], satisfied_dependencies=list(PURPOSE_MANIFEST[purpose]["required_dependencies"]), evidence_refs=[x["reference"]])
    return make_result(purpose, "RESOLVED", "NOT_MATCHED", reasons=[f"{'Amount matches' if same_amount else 'Amount does not match'}; {'currency matches' if same_currency else 'currency does not match'}."], satisfied_dependencies=list(PURPOSE_MANIFEST[purpose]["required_dependencies"]), evidence_refs=[x["reference"]])


def resolve_expense(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "EXPENSE_EVIDENCE"
    sat, missing = [], []
    if resolve_purchase(r)["resolution_state"] == "RESOLVED":
        sat.append("purchase_declaration")
    else:
        missing.append("purchase_declaration")
    business_purpose = str(r.get("purpose_context", {}).get("expense", {}).get("business_purpose", "")).strip()
    if business_purpose:
        sat.append("business_purpose")
    else:
        missing.append("business_purpose")
    if missing:
        return make_result(purpose, "INCOMPLETE", "EXPENSE_EVIDENCE_INCOMPLETE", reasons=["The bounded example expense profile is missing: " + ", ".join(missing) + "."], satisfied_dependencies=sat, missing_dependencies=missing)
    return make_result(purpose, "RESOLVED", "EVIDENCE_SUFFICIENT_FOR_EXAMPLE_PROFILE", reasons=["The bounded example profile has a complete purchase declaration and declared business purpose."], satisfied_dependencies=sat)


def resolve_warranty(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "WARRANTY_EVIDENCE"
    sat, missing = [], []
    if resolve_purchase(r)["resolution_state"] == "RESOLVED":
        sat.append("purchase_declaration")
    else:
        missing.append("purchase_declaration")
    ref = str(r.get("purpose_context", {}).get("warranty", {}).get("item_reference", "")).strip()
    if ref:
        sat.append("warranty_item_reference")
    else:
        missing.append("warranty_item_reference")
    if ref and any(item.get("id") == ref for item in r["transaction"].get("items", [])):
        sat.append("referenced_item_exists")
    elif ref:
        missing.append("referenced_item_exists")
    if missing:
        return make_result(purpose, "INCOMPLETE", "WARRANTY_EVIDENCE_INCOMPLETE", reasons=["The bounded warranty-evidence profile is missing: " + ", ".join(missing) + "."], satisfied_dependencies=sat, missing_dependencies=missing)
    return make_result(purpose, "RESOLVED", "PURCHASE_EVIDENCE_AVAILABLE", reasons=[f"The purchase structure contains the declared item reference {ref}. This is proof-of-purchase evidence only."], satisfied_dependencies=sat, evidence_refs=[ref])


def resolve_return_eligibility(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "RETURN_ELIGIBILITY_EVIDENCE"
    sat, missing = [], []
    purchase = resolve_purchase(r)
    lineage = resolve_lineage(r)
    if purchase["resolution_state"] == "RESOLVED":
        sat.append("purchase_declaration")
    else:
        missing.append("purchase_declaration")
    if lineage["resolution_state"] == "RESOLVED":
        sat.append("lineage_consistency")
    elif lineage["resolution_state"] == "CONFLICT":
        return make_result(purpose, "CONFLICT", "RETURN_EVIDENCE_CONFLICT", reasons=["Return evidence cannot resolve while lineage is conflicting."], satisfied_dependencies=sat, conflicting_dependencies=["lineage_consistency"])
    else:
        missing.append("lineage_consistency")
    try:
        requested = parse_minor(r.get("purpose_context", {}).get("return_eligibility", {}).get("requested_amount"))
        if requested >= 0:
            sat.append("return_request_amount")
        else:
            missing.append("return_request_amount")
    except Exception:
        requested = 0
        missing.append("return_request_amount")
    if lineage.get("metrics") and lineage["metrics"].get("remaining_returnable", -1) >= 0:
        sat.append("remaining_returnable_value")
    else:
        missing.append("remaining_returnable_value")
    if missing:
        return make_result(purpose, "INCOMPLETE", "RETURN_EVIDENCE_INCOMPLETE", reasons=["The bounded return-evidence profile is missing: " + ", ".join(missing) + "."], satisfied_dependencies=sat, missing_dependencies=missing)
    remaining = lineage["metrics"]["remaining_returnable"]
    if requested <= remaining:
        return make_result(purpose, "RESOLVED", "STRUCTURE_SUPPORTS_REQUESTED_AMOUNT", reasons=[f"Requested return amount {format_minor(requested)} is within the remaining structurally returnable value {format_minor(remaining)}."], satisfied_dependencies=sat, metrics={"requested": requested, "remaining_returnable": remaining})
    return make_result(purpose, "RESOLVED", "STRUCTURE_DOES_NOT_SUPPORT_REQUESTED_AMOUNT", reasons=[f"Requested return amount {format_minor(requested)} exceeds the remaining structurally returnable value {format_minor(remaining)}."], satisfied_dependencies=sat, metrics={"requested": requested, "remaining_returnable": remaining})


def resolve_accounting(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "ACCOUNTING_CLASSIFICATION"
    if resolve_purchase(r)["resolution_state"] != "RESOLVED":
        return make_result(purpose, "INCOMPLETE", "ACCOUNTING_PROPOSAL_UNAVAILABLE", reasons=["A complete purchase declaration is required before producing a bounded classification proposal."], missing_dependencies=["purchase_declaration"])
    return make_result(purpose, "RESOLVED", "PROPOSED", reasons=["A transaction-evidence structure is available. Any accounting classification remains a proposal under external policy authority."], satisfied_dependencies=["purchase_declaration"], coverage=100)


def resolve_audit_trace(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "AUDIT_TRACE"
    sat = []
    if len(receipt_id(r)) == 64:
        sat.append("receipt_identity")
    if len(structure_id(r)) == 64:
        sat.append("structure_identity")
    if r.get("origin", {}).get("class") in {"NATIVE", "WRAPPED", "DERIVED"}:
        sat.append("origin_class")
    if isinstance(r.get("lineage"), list) and all(len(lineage_event_id(event)) == 64 for event in r["lineage"]):
        sat.append("lineage_event_identities")
    missing = [dep for dep in PURPOSE_MANIFEST[purpose]["required_dependencies"] if dep not in sat]
    if missing:
        return make_result(purpose, "INCOMPLETE", "TRACE_INCOMPLETE", reasons=["The bounded audit trace is missing: " + ", ".join(missing) + "."], satisfied_dependencies=sat, missing_dependencies=missing)
    return make_result(purpose, "RESOLVED", "TRACE_RECONSTRUCTABLE", reasons=["Receipt identity, full-structure identity, origin class, and lineage event identities are reconstructable."], satisfied_dependencies=sat, evidence_refs=[lineage_event_id(event) for event in r.get("lineage", [])])


def lineage_graph_id(r: dict[str, Any]) -> str:
    nodes = [{"event_id": lineage_event_id(event), "event": event} for event in r.get("lineage", [])]
    nodes.sort(key=lambda item: item["event_id"])
    return hash_value({"profile": PROFILE["lineage_graph"], "root_receipt_id": receipt_id(r), "nodes": nodes})


def adapter_contract(r: dict[str, Any]) -> dict[str, Any]:
    origin = migrate_receipt(r)["origin"]
    origin_class = origin.get("class")
    origin_authority = "DECLARED_AT_ORIGIN" if origin_class == "NATIVE" else "TRANSFORMED_FROM_DECLARED_SOURCE" if origin_class == "WRAPPED" else "DERIVED_NOT_ORIGIN_DECLARED"
    return {
        "profile": PROFILE["adapter"], "origin_class": origin_class, "source_profile": origin.get("source_profile", ""),
        "source_artifact_id": origin.get("source_artifact_id") or None, "unmapped_fields": list(origin.get("unmapped_fields", [])),
        "warnings": list(origin.get("warnings", [])), "origin_authority": origin_authority, "semantic_equivalence": "NOT_ASSUMED",
    }


def print_result(title: str, result: dict[str, Any], verbose: bool = False) -> None:
    print(title)
    print(f"STATUS: {result.get('status')}")
    if "pass" in result:
        print(f"RESULT: {result['pass']}/{result['total']} PASS" if result.get("status") == "PASS" else f"RESULT: {result['pass']}/{result['total']}")
    if result.get("verification_scope"):
        print(f"VERIFICATION SCOPE: {result['verification_scope']}")
    if result.get("independent_implementation"):
        print(f"SEPARATE IMPLEMENTATION PATH: {result['independent_implementation']}")
    if result.get("third_party_verification"):
        print(f"THIRD-PARTY VERIFICATION: {result['third_party_verification']}")
    if verbose:
        for check in result.get("checks", []):
            print(f"{check['status']}  {check['name']}  {check.get('detail', '')}")


def _migrate_receipt_base(obj: dict[str, Any]) -> dict[str, Any]:
    r = copy.deepcopy(obj)
    if r.get("profile") == "SR-RECEIPT-1-D01":
        r["profile"] = PROFILE["schema"]
        r["schema_version"] = "2.0.0"
        r["ruleset_version"] = "SR-RULES-2.0.0"
    r.setdefault("origin", {"class": "DERIVED", "source_profile": "Legacy import"})
    r["origin"].setdefault("source_artifact_id", "")
    if not isinstance(r["origin"].get("unmapped_fields"), list):
        r["origin"]["unmapped_fields"] = []
    if not isinstance(r["origin"].get("warnings"), list):
        r["origin"]["warnings"] = []
    r.setdefault("evidence", {"payment": []})
    r["evidence"].setdefault("payment", [])
    r.setdefault("purpose_context", {})
    r["purpose_context"].setdefault("expense", {"business_purpose": "", "claimant_role": ""})
    r["purpose_context"].setdefault("warranty", {"item_reference": ""})
    r["purpose_context"].setdefault("return_eligibility", {"requested_amount": ""})
    r.setdefault("lineage", [])
    return r


def _resolve_lineage_base(r: dict[str, Any]) -> dict[str, Any]:
    purpose = "LINEAGE_CURRENT_STATE"
    returned = refunded = credited = 0
    issues, refs = [], []
    for event in r.get("lineage", []):
        try:
            amount = parse_minor(event.get("amount"))
        except Exception:
            issues.append(f"Invalid {event.get('type')} amount at {event.get('reference') or 'unreferenced event'}.")
            continue
        if amount < 0:
            issues.append(f"Negative {event.get('type')} amount is not supported.")
        if event.get("reference"):
            refs.append(event["reference"])
        if event.get("type") == "RETURN":
            returned += amount
        elif event.get("type") == "REFUND":
            refunded += amount
        elif event.get("type") == "CREDIT":
            credited += amount
    try:
        total = parse_minor(r["transaction"]["declared_total"])
    except Exception:
        return make_result(purpose, "INCOMPLETE", "LINEAGE_BASE_INCOMPLETE", reasons=["Declared transaction total is invalid."], missing_dependencies=["declared_total"], satisfied_dependencies=["lineage_events"], metrics={"returned": returned, "refunded": refunded, "credited": credited, "net": 0})
    if returned > total:
        issues.append("Returned amount exceeds the declared transaction total.")
    if refunded > returned:
        issues.append("Refunded amount exceeds the supported returned amount.")
    metrics = {"returned": returned, "refunded": refunded, "credited": credited, "net": total - refunded - credited, "remaining_returnable": total - returned}
    if issues:
        return make_result(purpose, "CONFLICT", "LINEAGE_CONFLICT", reasons=issues, satisfied_dependencies=["declared_total", "lineage_events"], conflicting_dependencies=["lineage_events"], evidence_refs=refs, metrics=metrics)
    status = "ACTIVE"
    if returned == total and total > 0:
        status = "FULLY_RETURNED"
    elif returned > 0:
        status = "PARTIALLY_RETURNED"
    if refunded == total and total > 0:
        status = "FULLY_REFUNDED"
    elif refunded > 0 and status == "ACTIVE":
        status = "PARTIALLY_REFUNDED"
    elif refunded > 0 and status == "PARTIALLY_RETURNED":
        status = "PARTIALLY_RETURNED_AND_REFUNDED"
    return make_result(purpose, "RESOLVED", status, reasons=["Linked events reconcile under the bounded lineage profile."], satisfied_dependencies=["declared_total", "lineage_events"], evidence_refs=refs, metrics=metrics)


def purpose_profile_subject(purpose: str) -> dict[str, Any]:
    manifest = PURPOSE_MANIFEST[purpose]
    return {
        "profile_family": PROFILE["purpose_manifest"],
        "purpose": purpose,
        "profile": manifest["profile"],
        "manifest_version": manifest["manifest_version"],
        "question": manifest["question"],
        "authority_state": manifest["authority_state"],
        "execution_authority": manifest["execution_authority"],
        "required_dependencies": manifest["required_dependencies"],
        "context_requirements": manifest["context_requirements"],
        "limitations": manifest["limitations"],
    }


def purpose_profile_id(purpose: str) -> str:
    return hash_value(purpose_profile_subject(purpose))


def purpose_manifest_set_id() -> str:
    purposes = [{"purpose": purpose, "purpose_profile_id": purpose_profile_id(purpose)} for purpose in PURPOSES]
    purposes.sort(key=lambda item: item["purpose"])
    return hash_value({"profile": PROFILE["purpose_manifest"], "purposes": purposes})


def money_profile_for_currency(currency: Any) -> str:
    return PROFILE["money"] if CURRENCY_EXPONENTS.get(currency) == 2 else "UNSUPPORTED_CURRENCY_EXPONENT"


def validate_imported_quantities(obj: dict[str, Any]) -> None:
    items = obj.get("transaction", {}).get("items", []) if isinstance(obj, dict) else []
    if not isinstance(items, list):
        raise ValueError("INVALID_ITEM_QUANTITY")
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("INVALID_ITEM_QUANTITY")
        qty = item.get("qty")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("INVALID_ITEM_QUANTITY")


def migrate_receipt(obj: dict[str, Any]) -> dict[str, Any]:
    r = _migrate_receipt_base(obj)
    r["profile"] = PROFILE["schema"]
    r["schema_version"] = "2.1.0"
    r["ruleset_version"] = "SR-RULES-3.0.0"
    validate_imported_quantities(r)
    context = r.setdefault("evaluation_context", {})
    context["profile"] = PROFILE["evaluation_context"]
    if "as_of" not in context:
        context["as_of"] = r.get("transaction", {}).get("date", "")
    context.setdefault("jurisdiction_profile", "UNSPECIFIED")
    context.setdefault("currency_profile", money_profile_for_currency(r.get("transaction", {}).get("currency")))
    return r


def evaluation_context(r: dict[str, Any]) -> dict[str, Any]:
    receipt = migrate_receipt(r)
    context = receipt.get("evaluation_context", {})
    return {
        "profile": PROFILE["evaluation_context"],
        "as_of": context.get("as_of", ""),
        "jurisdiction_profile": context.get("jurisdiction_profile") or "UNSPECIFIED",
        "currency_profile": context.get("currency_profile") or money_profile_for_currency(receipt.get("transaction", {}).get("currency")),
    }


def evaluation_context_id(r: dict[str, Any]) -> str:
    return hash_value(evaluation_context(r))


def trust_context(r: dict[str, Any]) -> dict[str, Any]:
    adapter = adapter_contract(r)
    return {
        "profile": PROFILE["trust_context"],
        "structural_integrity_state": "RECONSTRUCTABLE",
        "provenance_state": adapter["origin_authority"],
        "issuer_authenticity_state": "NOT_ESTABLISHED",
        "physical_occurrence_state": "NOT_ESTABLISHED",
        "execution_authority": "NONE",
    }


def money_support(r: dict[str, Any]) -> dict[str, Any]:
    receipt = migrate_receipt(r)
    currency = receipt.get("transaction", {}).get("currency")
    exponent = CURRENCY_EXPONENTS.get(currency)
    if exponent is None:
        return {"supported": False, "reason": "UNKNOWN_CURRENCY", "currency": currency, "exponent": None}
    if exponent != 2:
        return {"supported": False, "reason": "CURRENCY_EXPONENT_UNSUPPORTED", "currency": currency, "exponent": exponent}
    context = evaluation_context(receipt)
    if context["currency_profile"] != PROFILE["money"]:
        return {"supported": False, "reason": "CURRENCY_PROFILE_UNSUPPORTED", "currency": currency, "exponent": exponent}
    return {"supported": True, "currency": currency, "exponent": exponent, "profile": PROFILE["money"]}


def resolve_lineage(r: dict[str, Any]) -> dict[str, Any]:
    ids = [lineage_event_id(event) for event in r.get("lineage", [])]
    if len(set(ids)) != len(ids):
        return make_result(
            "LINEAGE_CURRENT_STATE", "CONFLICT", "LINEAGE_DUPLICATE_EVENT_ID",
            reasons=["Duplicate lineage event identity detected; replayed events are not counted twice."],
            satisfied_dependencies=["declared_total"], conflicting_dependencies=["lineage_events"], evidence_refs=ids,
            metrics={"returned": 0, "refunded": 0, "credited": 0, "net": 0, "remaining_returnable": 0},
        )
    return _resolve_lineage_base(r)


def context_incomplete_result(purpose: str, r: dict[str, Any], missing: list[str]) -> dict[str, Any]:
    manifest = PURPOSE_MANIFEST[purpose]
    tc = trust_context(r)
    return {
        "evaluation_status": "EVALUATED", "resolution_state": "INCOMPLETE", "purpose_outcome": "EVALUATION_CONTEXT_INCOMPLETE",
        "authority_state": manifest["authority_state"], "execution_authority": "NONE",
        "reasons": ["Required declared evaluation context is missing: " + ", ".join(missing) + "."], "evidence_refs": [],
        "required_dependencies": list(manifest["required_dependencies"]), "satisfied_dependencies": [], "missing_dependencies": [],
        "conflicting_dependencies": [], "coverage": 0, "missing_context": missing,
        "trust_context": tc, "authenticity_state": "NOT_ESTABLISHED", "occurrence_state": "NOT_ESTABLISHED",
    }


def unsupported_money_result(purpose: str, r: dict[str, Any], support: dict[str, Any]) -> dict[str, Any]:
    manifest = PURPOSE_MANIFEST[purpose]
    tc = trust_context(r)
    exponent = "UNKNOWN" if support.get("exponent") is None else str(support["exponent"])
    return {
        "evaluation_status": "EVALUATED", "resolution_state": "UNSUPPORTED", "purpose_outcome": support["reason"],
        "authority_state": manifest["authority_state"], "execution_authority": "NONE",
        "reasons": [f"Currency {support.get('currency') or 'UNKNOWN'} uses exponent {exponent}; the current reference money profile supports exponent 2 only."],
        "evidence_refs": [], "required_dependencies": list(manifest["required_dependencies"]), "satisfied_dependencies": [],
        "missing_dependencies": [], "conflicting_dependencies": [], "coverage": 0,
        "trust_context": tc, "authenticity_state": "NOT_ESTABLISHED", "occurrence_state": "NOT_ESTABLISHED",
    }


def resolve_all(r: dict[str, Any]) -> dict[str, Any]:
    receipt = migrate_receipt(r)
    support = money_support(receipt)
    raw: dict[str, dict[str, Any]] = {}
    for purpose in PURPOSES:
        missing_context = [name for name in PURPOSE_MANIFEST[purpose]["context_requirements"] if not evaluation_context(receipt).get(name)]
        if missing_context:
            item = context_incomplete_result(purpose, receipt, missing_context)
        elif purpose != "AUDIT_TRACE" and not support["supported"]:
            item = unsupported_money_result(purpose, receipt, support)
        else:
            item = (
                resolve_purchase(receipt) if purpose == "PURCHASE_DECLARATION" else
                resolve_arithmetic(receipt) if purpose == "ARITHMETIC_CHECK" else
                resolve_payment(receipt) if purpose == "PAYMENT_MATCH" else
                resolve_expense(receipt) if purpose == "EXPENSE_EVIDENCE" else
                resolve_warranty(receipt) if purpose == "WARRANTY_EVIDENCE" else
                resolve_return_eligibility(receipt) if purpose == "RETURN_ELIGIBILITY_EVIDENCE" else
                resolve_lineage(receipt) if purpose == "LINEAGE_CURRENT_STATE" else
                resolve_accounting(receipt) if purpose == "ACCOUNTING_CLASSIFICATION" else
                resolve_audit_trace(receipt)
            )
        tc = trust_context(receipt)
        result_subject = copy.deepcopy(item)
        result_subject["trust_context"] = tc
        result_subject["authenticity_state"] = tc["issuer_authenticity_state"]
        result_subject["occurrence_state"] = tc["physical_occurrence_state"]
        subject = {
            "purpose": purpose,
            "profile": PURPOSE_MANIFEST[purpose]["profile"],
            "purpose_profile_id": purpose_profile_id(purpose),
            "structure_id": structure_id(receipt),
            "evaluation_context_id": evaluation_context_id(receipt),
            "result": result_hash_value(result_subject),
        }
        bound = copy.deepcopy(result_subject)
        bound["purpose_profile"] = PURPOSE_MANIFEST[purpose]["profile"]
        bound["purpose_profile_id"] = purpose_profile_id(purpose)
        bound["evaluation_context"] = evaluation_context(receipt)
        bound["evaluation_context_id"] = evaluation_context_id(receipt)
        bound["purpose_result_id"] = hash_value(subject)
        raw[purpose] = bound
    return raw


def current_lineage_state_id(r: dict[str, Any]) -> str:
    result = resolve_all(r)["LINEAGE_CURRENT_STATE"]
    return hash_value({
        "profile": PROFILE["lineage_graph"],
        "lineage_graph_id": lineage_graph_id(r),
        "evaluation_context_id": evaluation_context_id(r),
        "resolution_state": result["resolution_state"],
        "purpose_outcome": result["purpose_outcome"],
        "metrics": canonical_bigint_metrics(result.get("metrics")),
    })


def purpose_receipt(r: dict[str, Any], purpose: str) -> dict[str, Any]:
    receipt = migrate_receipt(r)
    result = resolve_all(receipt).get(purpose)
    if result is None:
        subject = {
            "profile": PROFILE["purpose_receipt"], "purpose": purpose, "purpose_profile": None, "purpose_profile_id": None,
            "structure_id": structure_id(receipt), "evaluation_context_id": evaluation_context_id(receipt),
            "resolution_state": "UNSUPPORTED", "purpose_outcome": "PURPOSE_PROFILE_UNSUPPORTED", "authority_state": "NONE",
            "execution_authority": "NONE", "authenticity_state": "NOT_ESTABLISHED", "occurrence_state": "NOT_ESTABLISHED",
            "trust_context": trust_context(receipt), "required_dependencies": [], "satisfied_dependencies": [],
            "missing_dependencies": ["purpose_profile"], "conflicting_dependencies": [], "evidence_refs": [], "purpose_result_id": None,
        }
        output = copy.deepcopy(subject)
        output["purpose_receipt_id"] = hash_value(subject)
        return output
    subject = {
        "profile": PROFILE["purpose_receipt"], "purpose": purpose, "purpose_profile": result["purpose_profile"],
        "purpose_profile_id": result["purpose_profile_id"], "structure_id": structure_id(receipt),
        "evaluation_context_id": result["evaluation_context_id"], "resolution_state": result["resolution_state"],
        "purpose_outcome": result["purpose_outcome"], "authority_state": result["authority_state"],
        "execution_authority": result["execution_authority"], "authenticity_state": result["authenticity_state"],
        "occurrence_state": result["occurrence_state"], "trust_context": result["trust_context"],
        "required_dependencies": result["required_dependencies"], "satisfied_dependencies": result["satisfied_dependencies"],
        "missing_dependencies": result["missing_dependencies"], "conflicting_dependencies": result["conflicting_dependencies"],
        "evidence_refs": result["evidence_refs"], "purpose_result_id": result["purpose_result_id"],
    }
    output = copy.deepcopy(subject)
    output["purpose_receipt_id"] = hash_value(subject)
    return output


def bundle_subject(bundle: dict[str, Any]) -> dict[str, Any]:
    return {key: bundle[key] for key in [
        "format", "profile_manifest", "purpose_profile_manifest_set_id", "purpose_profile_manifests", "evaluation_context",
        "trust_context", "adapter_contract", "receipt", "identities", "lineage", "purpose_receipts",
    ]}


def build_evidence_bundle(receipt_input: dict[str, Any]) -> dict[str, Any]:
    receipt = migrate_receipt(receipt_input)
    receipts = [purpose_receipt(receipt, purpose) for purpose in PURPOSES]
    bundle = {
        "format": PROFILE["bundle"], "producer": "Structural Receipt Browser Reference v0.5.3", "verification_scope": "PRODUCER_EXPORT",
        "independent_verification": "NOT_CLAIMED", "profile_manifest": copy.deepcopy(PROFILE),
        "purpose_profile_manifest_set_id": purpose_manifest_set_id(),
        "purpose_profile_manifests": {purpose: {**purpose_profile_subject(purpose), "purpose_profile_id": purpose_profile_id(purpose)} for purpose in PURPOSES},
        "evaluation_context": evaluation_context(receipt), "trust_context": trust_context(receipt), "adapter_contract": adapter_contract(receipt),
        "receipt": receipt,
        "identities": {"receipt_id": receipt_id(receipt), "structure_id": structure_id(receipt), "evaluation_context_id": evaluation_context_id(receipt), "purpose_manifest_set_id": purpose_manifest_set_id()},
        "lineage": {"event_ids": sorted(lineage_event_id(event) for event in receipt.get("lineage", [])), "lineage_graph_id": lineage_graph_id(receipt), "current_lineage_state_id": current_lineage_state_id(receipt)},
        "purpose_receipts": receipts,
        "producer_checks": {"receipt_identity_reconstructed": True, "structure_identity_reconstructed": True, "purpose_receipts_generated": len(receipts) == len(PURPOSES), "lineage_graph_reconstructed": True, "profile_manifest_reconstructed": True, "evaluation_context_reconstructed": True},
    }
    bundle["bundle_id"] = hash_value(bundle_subject(bundle))
    return bundle


def _verify_bundle_core(bundle: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    if not isinstance(bundle, dict) or bundle.get("format") != PROFILE["bundle"]:
        return {"status": "UNSUPPORTED", "verification_scope": "SEPARATE_IMPLEMENTATION_RECONSTRUCTION", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED", "checks": [{"name": "Bundle profile", "status": "FAIL", "detail": "Unsupported or missing evidence-bundle profile."}], "reconstructed": None}
    manifest = bundle.get("profile_manifest")
    if not isinstance(manifest, dict) or manifest.get("bundle") != PROFILE["bundle"] or manifest.get("verifier") != PROFILE["verifier"]:
        return {"status": "UNSUPPORTED", "verification_scope": "SEPARATE_IMPLEMENTATION_RECONSTRUCTION", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED", "checks": [{"name": "Profile manifest", "status": "FAIL", "detail": "Required verifier-facing profiles are missing or unsupported."}], "reconstructed": None}
    try:
        receipt = migrate_receipt(bundle["receipt"])
    except Exception:
        return {"status": "FAIL", "verification_scope": "SEPARATE_IMPLEMENTATION_RECONSTRUCTION", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED", "checks": [{"name": "Receipt payload", "status": "FAIL", "detail": "Receipt payload could not be reconstructed."}], "reconstructed": None}
    reconstructed = {
        "receipt_id": receipt_id(receipt), "structure_id": structure_id(receipt), "evaluation_context_id": evaluation_context_id(receipt),
        "purpose_manifest_set_id": purpose_manifest_set_id(), "lineage_graph_id": lineage_graph_id(receipt),
        "current_lineage_state_id": current_lineage_state_id(receipt), "purpose_receipts": [purpose_receipt(receipt, purpose) for purpose in PURPOSES],
    }
    def check(name: str, condition: bool, ok_detail: str, fail_detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": ok_detail if condition else fail_detail})
    identities = bundle.get("identities", {})
    check("Receipt identity", reconstructed["receipt_id"] == identities.get("receipt_id"), "Reconstructed from receipt payload.", "Claimed receipt identity does not match reconstruction.")
    check("Structure identity", reconstructed["structure_id"] == identities.get("structure_id"), "Reconstructed from full structural payload.", "Claimed structure identity does not match reconstruction.")
    check("Evaluation context identity", reconstructed["evaluation_context_id"] == identities.get("evaluation_context_id"), "Reconstructed from declared evaluation context.", "Declared evaluation context does not match its claimed identity.")
    check("Purpose manifest set identity", reconstructed["purpose_manifest_set_id"] == identities.get("purpose_manifest_set_id") == bundle.get("purpose_profile_manifest_set_id"), "Frozen purpose profile manifests reconstruct.", "Purpose profile manifest set does not reconstruct.")
    manifests = bundle.get("purpose_profile_manifests", {})
    check("Purpose profile identities", all(manifests.get(purpose, {}).get("purpose_profile_id") == purpose_profile_id(purpose) for purpose in PURPOSES), "All frozen purpose profile manifests match their identified data.", "One or more purpose profile manifests do not match.")
    check("Evaluation context", canonical_json(evaluation_context(receipt)) == canonical_json(bundle.get("evaluation_context")), "Declared evaluation context reconstructs.", "Evaluation context payload differs from the receipt context.")
    check("Trust context", canonical_json(trust_context(receipt)) == canonical_json(bundle.get("trust_context")), "Bounded trust context reconstructs.", "Trust context overstates or differs from the reconstructed boundary.")
    check("Lineage graph identity", reconstructed["lineage_graph_id"] == bundle.get("lineage", {}).get("lineage_graph_id"), "Reconstructed from root receipt and linked event set.", "Claimed lineage graph identity does not match reconstruction.")
    check("Current lineage state identity", reconstructed["current_lineage_state_id"] == bundle.get("lineage", {}).get("current_lineage_state_id"), "Reconstructed from current bounded lineage state and evaluation context.", "Claimed lineage state identity does not match reconstruction.")
    claimed = {item.get("purpose"): item for item in bundle.get("purpose_receipts", []) if isinstance(item, dict)}
    for item in reconstructed["purpose_receipts"]:
        other = claimed.get(item["purpose"])
        check(f"Purpose receipt {item['purpose']}", bool(other) and other.get("purpose_receipt_id") == item["purpose_receipt_id"], "Reconstructed purpose receipt identity matches.", "Purpose receipt is missing or does not match reconstruction.")
    check("Bundle identity", hash_value(bundle_subject(bundle)) == bundle.get("bundle_id"), "Bundle subject reconstructs to the claimed identity.", "Bundle subject has changed or the claimed bundle identity is incorrect.")
    check("Adapter contract", canonical_json(adapter_contract(receipt)) == canonical_json(bundle.get("adapter_contract")), "Declared transformation boundary reconstructs.", "Adapter contract does not match the receipt provenance fields.")
    return {"status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "verification_scope": "SEPARATE_IMPLEMENTATION_RECONSTRUCTION", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED", "checks": checks, "reconstructed": reconstructed}


def verify_conformance_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    if corpus.get("format") != PROFILE["corpus"] or corpus.get("conformance_profile") != PROFILE["conformance"]:
        return {"status": "UNSUPPORTED", "pass": 0, "fail": 1, "total": 1, "checks": [{"name": "Corpus profile", "status": "FAIL", "detail": "Unsupported conformance corpus profile."}]}
    checks: list[dict[str, str]] = []
    passed = failed = 0
    def add(name: str, condition: bool, detail: str) -> None:
        nonlocal passed, failed
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
        if condition:
            passed += 1
        else:
            failed += 1
    subject = {"format": corpus["format"], "profile_manifest": corpus["profile_manifest"], "purpose_profile_manifest_set_id": corpus["purpose_profile_manifest_set_id"], "vectors": corpus["vectors"]}
    add("Corpus identity", hash_value(subject) == corpus.get("corpus_id"), "Frozen corpus subject reconstructs.")
    add("Purpose manifest set identity", corpus.get("purpose_profile_manifest_set_id") == purpose_manifest_set_id(), "Frozen purpose profile manifest set reconstructs.")
    for vector in corpus.get("vectors", []):
        r = migrate_receipt(vector["receipt"])
        exp = vector["expected"]
        prefix = vector["id"]
        add(f"{prefix} receipt identity", receipt_id(r) == exp["receipt_id"], "Receipt identity matches frozen expectation.")
        add(f"{prefix} structure identity", structure_id(r) == exp["structure_id"], "Structure identity matches frozen expectation.")
        add(f"{prefix} evaluation context identity", evaluation_context_id(r) == exp["evaluation_context_id"], "Evaluation context identity matches frozen expectation.")
        add(f"{prefix} purpose manifest set identity", purpose_manifest_set_id() == exp["purpose_manifest_set_id"], "Purpose manifest set identity matches frozen expectation.")
        add(f"{prefix} lineage graph identity", lineage_graph_id(r) == exp["lineage_graph_id"], "Lineage graph identity matches frozen expectation.")
        add(f"{prefix} lineage state identity", current_lineage_state_id(r) == exp["current_lineage_state_id"], "Current lineage state identity matches frozen expectation.")
        add(f"{prefix} bundle identity", build_evidence_bundle(r)["bundle_id"] == exp["bundle_id"], "Evidence bundle identity matches frozen expectation.")
        results = resolve_all(r)
        for purpose in PURPOSES:
            actual = results[purpose]
            expected = exp["purpose_results"].get(purpose, {})
            pr = purpose_receipt(r, purpose)
            condition = all([
                actual["resolution_state"] == expected.get("resolution_state"), actual["purpose_outcome"] == expected.get("purpose_outcome"),
                actual["authority_state"] == expected.get("authority_state"), actual["execution_authority"] == expected.get("execution_authority"),
                actual["authenticity_state"] == expected.get("authenticity_state"), actual["purpose_profile_id"] == expected.get("purpose_profile_id"),
                actual["evaluation_context_id"] == expected.get("evaluation_context_id"), actual["purpose_result_id"] == expected.get("purpose_result_id"),
                pr["purpose_receipt_id"] == exp["purpose_receipt_ids"].get(purpose),
            ])
            add(f"{prefix} {purpose}", condition, "Purpose state, profile, trust boundary, context, and identities match frozen expectation.")
        unsupported = purpose_receipt(r, "UNSUPPORTED_TEST_PURPOSE")
        expected_unsupported = exp["unsupported_purpose"]
        add(f"{prefix} unsupported purpose", unsupported["resolution_state"] == expected_unsupported["resolution_state"] and unsupported["purpose_outcome"] == expected_unsupported["purpose_outcome"] and unsupported["purpose_receipt_id"] == expected_unsupported["purpose_receipt_id"], "Unsupported-purpose behavior matches frozen expectation.")
    return {"status": "PASS" if failed == 0 else "FAIL", "pass": passed, "fail": failed, "total": passed + failed, "checks": checks, "corpus_id": corpus.get("corpus_id"), "vector_count": len(corpus.get("vectors", [])), "verification_scope": "SEPARATE_IMPLEMENTATION_FROZEN_CONFORMANCE", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED"}


def verify_tamper_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    if corpus.get("format") != PROFILE["tamper_corpus"]:
        return {"status": "UNSUPPORTED", "pass": 0, "fail": 1, "total": 1, "checks": [{"name": "Tamper corpus profile", "status": "FAIL", "detail": "Unsupported tamper corpus profile."}]}
    checks = []
    passed = failed = 0
    for case in corpus.get("cases", []):
        actual = verify_bundle(case["bundle"])["status"]
        expected = case["expected_status"]
        ok = actual == expected
        checks.append({"name": case["id"], "status": "PASS" if ok else "FAIL", "detail": f"Expected {expected}; reconstructed {actual}."})
        if ok:
            passed += 1
        else:
            failed += 1
    return {"status": "PASS" if failed == 0 else "FAIL", "pass": passed, "fail": failed, "total": passed + failed, "checks": checks, "case_count": len(corpus.get("cases", [])), "verification_scope": "SEPARATE_IMPLEMENTATION_TAMPER_CORPUS", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED"}


def strict_json_loads(text: str) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("DUPLICATE_OBJECT_KEY")
            out[key] = value
        return out
    return json.loads(text, object_pairs_hook=pairs_hook, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NON_FINITE_NUMBER")))


def verify_hostile_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    if corpus.get("format") != PROFILE["hostile_corpus"]:
        return {"status": "UNSUPPORTED", "pass": 0, "fail": 1, "total": 1, "checks": [{"name": "Hostile corpus profile", "status": "FAIL", "detail": "Unsupported hostile-input corpus profile."}]}
    def duplicate_json_keys_rejected() -> bool:
        try:
            strict_json_loads('{"a":1,"a":2}')
            return False
        except ValueError as exc:
            return str(exc) == "DUPLICATE_OBJECT_KEY"
    def trailing_json_data_rejected() -> bool:
        try:
            strict_json_loads('{"a":1} true')
            return False
        except Exception:
            return True
    def excess_decimal_rejected() -> bool:
        try:
            parse_minor("1.001")
            return False
        except Exception:
            return True
    def jpy_unsupported() -> bool:
        r = migrate_receipt(corpus_reference_receipt())
        r["transaction"]["currency"] = "JPY"
        r["evaluation_context"]["currency_profile"] = money_profile_for_currency("JPY")
        return resolve_all(r)["ARITHMETIC_CHECK"]["resolution_state"] == "UNSUPPORTED"
    def kwd_unsupported() -> bool:
        r = migrate_receipt(corpus_reference_receipt())
        r["transaction"]["currency"] = "KWD"
        r["evaluation_context"]["currency_profile"] = money_profile_for_currency("KWD")
        return resolve_all(r)["PAYMENT_MATCH"]["resolution_state"] == "UNSUPPORTED"
    def missing_as_of() -> bool:
        r = migrate_receipt(corpus_reference_receipt())
        r["evaluation_context"]["as_of"] = ""
        return resolve_all(r)["LINEAGE_CURRENT_STATE"]["purpose_outcome"] == "EVALUATION_CONTEXT_INCOMPLETE"
    def duplicate_lineage() -> bool:
        r = migrate_receipt(corpus_reference_receipt())
        event = {"profile": "SR-LINEAGE-EVENT-1-D01", "type": "RETURN", "amount": "10.00", "reference": "R-DUP", "description": "Replay"}
        r["lineage"] = [event, copy.deepcopy(event)]
        return resolve_all(r)["LINEAGE_CURRENT_STATE"]["purpose_outcome"] == "LINEAGE_DUPLICATE_EVENT_ID"
    def empty_items() -> bool:
        r = migrate_receipt(corpus_reference_receipt())
        r["transaction"]["items"] = []
        return resolve_all(r)["PURCHASE_DECLARATION"]["resolution_state"] == "INCOMPLETE"

    def invalid_item_quantity_rejected() -> bool:
        r = corpus_reference_receipt()
        r["transaction"]["items"][0]["qty"] = '1" autofocus onfocus="window.__SR_UI_INJECTED=1'
        try:
            validate_imported_quantities(r)
            return False
        except ValueError as exc:
            return str(exc) == "INVALID_ITEM_QUANTITY"

    cases = {
        "unicode_nfc_nfd_distinct": lambda: hash_value({"merchant": "Café"}) != hash_value({"merchant": "Cafe\u0301"}),
        "duplicate_json_keys_rejected": duplicate_json_keys_rejected,
        "trailing_json_data_rejected": trailing_json_data_rejected,
        "zero_amount_exact": lambda: parse_minor("0.00") == 0,
        "negative_amount_exact": lambda: parse_minor("-0.01") == -1,
        "excess_decimal_rejected": excess_decimal_rejected,
        "extreme_magnitude_exact": lambda: format_minor(parse_minor("999999999999999999999999.99")) == "999999999999999999999999.99",
        "jpy_explicitly_unsupported": jpy_unsupported,
        "kwd_explicitly_unsupported": kwd_unsupported,
        "missing_as_of_abstains": missing_as_of,
        "duplicate_lineage_event_rejected": duplicate_lineage,
        "empty_item_lines_incomplete": empty_items,
        "invalid_item_quantity_rejected": invalid_item_quantity_rejected,
    }
    checks = []
    passed = failed = 0
    for case in corpus.get("cases", []):
        ok = bool(cases.get(case.get("id"), lambda: False)())
        checks.append({"name": case.get("id"), "status": "PASS" if ok else "FAIL", "detail": case.get("detail", "")})
        if ok:
            passed += 1
        else:
            failed += 1
    return {"status": "PASS" if failed == 0 else "FAIL", "pass": passed, "fail": failed, "total": passed + failed, "checks": checks, "case_count": len(corpus.get("cases", [])), "corpus_id": corpus.get("corpus_id"), "verification_scope": "SEPARATE_IMPLEMENTATION_HOSTILE_INPUT_CORPUS", "independent_implementation": "PASS", "third_party_verification": "NOT_CLAIMED"}


RELEASE_VERSION = "0.5.3"
PUBLISHED_CORPUS_IDS = {
    "conformance": "9f1d59ce40ab2c4a56e0d4f3753ae41d13844cd580377bbf565ef54330df889e",
    "tamper": "3c681d0d3b3a20a16796fea0273cab0a6412ad17ecd2da433ad470a8bdc9c0e5",
    "hostile": "1bc1a5a52719025c9d092df825d500c7b883e0a84bd695726163798323ef6603",
}


def _check_status(result: dict[str, Any], name: str) -> str:
    for check in result.get("checks", []):
        if check.get("name") == name:
            return check.get("status", "NOT_CHECKED")
    return "NOT_CHECKED"


def _purpose_receipt_status(result: dict[str, Any]) -> str:
    checks = [check for check in result.get("checks", []) if str(check.get("name", "")).startswith("Purpose receipt ")]
    if not checks:
        return "NOT_CHECKED"
    return "PASS" if all(check.get("status") == "PASS" for check in checks) else "FAIL"


def _aggregate_check_status(result: dict[str, Any], names: list[str]) -> str:
    values = [_check_status(result, name) for name in names]
    if all(value == "PASS" for value in values):
        return "PASS"
    if any(value == "FAIL" for value in values):
        return "FAIL"
    return "NOT_CHECKED"


def verification_result_contract(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": "SR-VERIFICATION-RESULT-1-D01",
        "release_version": RELEASE_VERSION,
        "verification_status": result.get("status", "FAIL"),
        "receipt_identity_status": _check_status(result, "Receipt identity"),
        "structure_identity_status": _check_status(result, "Structure identity"),
        "profile_status": _aggregate_check_status(result, ["Purpose manifest set identity", "Purpose profile identities"]),
        "lineage_status": _aggregate_check_status(result, ["Lineage graph identity", "Current lineage state identity"]),
        "purpose_receipt_status": _purpose_receipt_status(result),
        "bundle_identity_status": _check_status(result, "Bundle identity"),
        "unsupported_conditions": [] if result.get("status") != "UNSUPPORTED" else ["UNSUPPORTED_BUNDLE_OR_PROFILE"],
        "claim_boundary": {
            "separate_implementation": "PROJECT_PRODUCED",
            "third_party_verification": "NOT_CLAIMED",
            "execution_authority": "NONE",
        },
    }


def verify_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    try:
        result = _verify_bundle_core(bundle)
    except Exception as exc:
        result = {
            "status": "FAIL",
            "verification_scope": "SEPARATE_IMPLEMENTATION_RECONSTRUCTION",
            "independent_implementation": "PASS",
            "third_party_verification": "NOT_CLAIMED",
            "checks": [{"name": "Receipt payload", "status": "FAIL", "detail": f"Receipt payload could not be reconstructed: {type(exc).__name__}."}],
            "reconstructed": None,
        }
    result["result_contract"] = verification_result_contract(result)
    return result


def verify_tamper_corpus_release(corpus: dict[str, Any]) -> dict[str, Any]:
    result = verify_tamper_corpus(corpus)
    result["corpus_id"] = corpus.get("corpus_id")
    return result


def enforce_release_corpus_pin(kind: str, result: dict[str, Any]) -> dict[str, Any]:
    expected = PUBLISHED_CORPUS_IDS[kind]
    actual = result.get("corpus_id")
    pinned = actual == expected
    out = copy.deepcopy(result)
    pin_check = {
        "name": f"Published {kind} corpus identity",
        "status": "PASS" if pinned else "FAIL",
        "detail": f"Expected {expected}; reconstructed {actual}.",
    }
    out.setdefault("checks", []).insert(0, pin_check)
    if not pinned:
        out["status"] = "FAIL"
        out["fail"] = int(out.get("fail", 0)) + 1
        out["total"] = int(out.get("total", 0)) + 1
    out["published_corpus_id"] = expected
    out["published_corpus_id_match"] = pinned
    return out


def resolve_release_file(base: Path, filename: str) -> Path:
    candidates = [
        base.parent / "verify" / filename,
        base / filename,
        Path.cwd() / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def corpus_reference_receipt() -> dict[str, Any]:
    return {
        "profile": PROFILE["schema"], "schema_version": "2.1.0", "ruleset_version": "SR-RULES-3.0.0",
        "origin": {"class": "NATIVE", "source_profile": "Native browser reference", "source_artifact_id": "", "unmapped_fields": [], "warnings": []},
        "transaction": {"merchant": "Northstar Office Store", "receipt_number": "SR-1001", "date": "2026-07-18", "currency": "USD", "items": [{"id": "ITEM-1", "description": "Portable document scanner", "qty": 1, "unit_price": "240.00"}, {"id": "ITEM-2", "description": "USB-C cable", "qty": 2, "unit_price": "15.00"}], "discount": "10.00", "tax": "20.80", "charges": "0.00", "declared_total": "280.80"},
        "evidence": {"payment": [{"kind": "INDEPENDENT_PAYMENT", "reference": "PAY-1001", "amount": "280.80", "currency": "USD"}]},
        "purpose_context": {"expense": {"business_purpose": "Office document digitization", "claimant_role": "Employee"}, "warranty": {"item_reference": "ITEM-1"}, "return_eligibility": {"requested_amount": "40.00"}},
        "lineage": [], "evaluation_context": {"profile": PROFILE["evaluation_context"], "as_of": "2026-07-18", "jurisdiction_profile": "UNSPECIFIED", "currency_profile": PROFILE["money"]},
    }


def load_json(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def input_failure_result(error_code: str, detail: str) -> dict[str, Any]:
    result = {
        "status": "FAIL",
        "verification_scope": "SEPARATE_IMPLEMENTATION_INPUT",
        "independent_implementation": "PASS",
        "third_party_verification": "NOT_CLAIMED",
        "error_code": error_code,
        "checks": [{"name": "Input parsing", "status": "FAIL", "detail": detail}],
        "reconstructed": None,
    }
    result["result_contract"] = verification_result_contract(result)
    return result


def load_and_run(path: Path, runner, error_scope: str) -> dict[str, Any]:
    try:
        payload = load_json(path)
    except UnicodeDecodeError:
        return input_failure_result("INPUT_NOT_UTF8", f"{error_scope} input is not valid UTF-8.")
    except json.JSONDecodeError:
        return input_failure_result("MALFORMED_JSON", f"{error_scope} input is not valid JSON.")
    except ValueError as exc:
        code = str(exc) or "INVALID_JSON_INPUT"
        return input_failure_result(code, f"{error_scope} input was rejected by the strict JSON boundary: {code}.")
    except OSError as exc:
        return input_failure_result("INPUT_READ_ERROR", f"{error_scope} input could not be read: {exc}.")
    try:
        return runner(payload)
    except Exception as exc:
        return input_failure_result("STRUCTURAL_RECONSTRUCTION_ERROR", f"{error_scope} input could not be reconstructed: {type(exc).__name__}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Structural Receipt v0.5.3 separate Python verification implementation")
    parser.add_argument("bundle_path", nargs="?", type=Path, help="Evidence bundle JSON to verify.")
    parser.add_argument("--bundle", type=Path, help="Evidence bundle JSON to verify.")
    parser.add_argument("--conformance", type=Path)
    parser.add_argument("--tamper-corpus", type=Path)
    parser.add_argument("--hostile-corpus", type=Path)
    parser.add_argument("--all", action="store_true", help="Verify the complete v0.5.3 frozen release corpus set.")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if args.bundle_path and args.bundle:
        parser.error("provide the bundle either positionally or with --bundle, not both")

    base = Path(__file__).resolve().parent
    tasks: list[tuple[str, dict[str, Any]]] = []
    bundle_path = args.bundle or args.bundle_path

    if args.all:
        conformance_path = args.conformance or resolve_release_file(base, "Structural_Receipt_Conformance_Corpus_v0_5_3.json")
        tamper_path = args.tamper_corpus or resolve_release_file(base, "Structural_Receipt_Tamper_Corpus_v0_5_3.json")
        hostile_path = args.hostile_corpus or resolve_release_file(base, "Structural_Receipt_Hostile_Input_Corpus_v0_5_3.json")
        tasks.append(("FROZEN CONFORMANCE", load_and_run(conformance_path, lambda p: enforce_release_corpus_pin("conformance", verify_conformance_corpus(p)), "Conformance corpus")))
        tasks.append(("TAMPER CORPUS", load_and_run(tamper_path, lambda p: enforce_release_corpus_pin("tamper", verify_tamper_corpus_release(p)), "Tamper corpus")))
        tasks.append(("HOSTILE INPUT CORPUS", load_and_run(hostile_path, lambda p: enforce_release_corpus_pin("hostile", verify_hostile_corpus(p)), "Hostile-input corpus")))
    else:
        if bundle_path:
            tasks.append(("EVIDENCE BUNDLE", load_and_run(bundle_path, verify_bundle, "Evidence bundle")))
        if args.conformance:
            tasks.append(("FROZEN CONFORMANCE", load_and_run(args.conformance, lambda p: enforce_release_corpus_pin("conformance", verify_conformance_corpus(p)), "Conformance corpus")))
        if args.tamper_corpus:
            tasks.append(("TAMPER CORPUS", load_and_run(args.tamper_corpus, lambda p: enforce_release_corpus_pin("tamper", verify_tamper_corpus_release(p)), "Tamper corpus")))
        if args.hostile_corpus:
            tasks.append(("HOSTILE INPUT CORPUS", load_and_run(args.hostile_corpus, lambda p: enforce_release_corpus_pin("hostile", verify_hostile_corpus(p)), "Hostile-input corpus")))

    if not tasks:
        parser.error("provide a bundle path, --bundle, --conformance, --tamper-corpus, --hostile-corpus, or --all")

    if args.json_output:
        print(json.dumps({title: result for title, result in tasks}, ensure_ascii=False, indent=2))
    else:
        print(f"Structural Receipt v{RELEASE_VERSION} Separate Verification")
        print("Adopt on one side. Verify on the other. Integrate only when useful.")
        print()
        for index, (title, result) in enumerate(tasks):
            if index:
                print()
            print_result(title, result, args.verbose)
            if title == "EVIDENCE BUNDLE":
                contract = result.get("result_contract", {})
                print(f"MACHINE RESULT PROFILE: {contract.get('profile', 'NOT_AVAILABLE')}")
                print(f"EXECUTION AUTHORITY: {contract.get('claim_boundary', {}).get('execution_authority', 'NONE')}")

    return 0 if all(result.get("status") == "PASS" for _, result in tasks) else 1


if __name__ == "__main__":
    sys.exit(main())
