#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union

RELEASE_VERSION = "0.5.3"
RELEASE_FILE_VERSION = "v0_5_3"
RECEIPT_PROFILE = "SR-RECEIPT-2-D02"
SCHEMA_VERSION = "2.1.0"
RULESET_VERSION = "SR-RULES-3.0.0"
EVALUATION_CONTEXT_PROFILE = "SR-EVALUATION-CONTEXT-1-D01"
ADAPTER_PROFILE = "SR-ADAPTER-1-D01"
BRIDGE_PROFILE = "SR-BRIDGE-1-D01"
MANIFEST_PROFILE = "SR-BRIDGE-ADAPTER-MANIFEST-1-D01"
MONEY_PROFILE = "SR-MONEY-2DP-1-D01"
CURRENCY_EXPONENTS = {"USD": 2, "INR": 2, "EUR": 2, "GBP": 2, "AUD": 2, "SGD": 2, "JPY": 0, "KWD": 3}
MISSING = object()


class BridgeError(Exception):
    pass


def reject_duplicate_pairs(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise BridgeError(f"DUPLICATE_OBJECT_KEY: {key}")
        out[key] = value
    return out


def load_json_bytes(raw: bytes) -> Any:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BridgeError("INPUT_NOT_UTF8") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_float=Decimal,
            parse_int=Decimal,
        )
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError(f"INVALID_JSON: {exc}") from exc


def load_json_file(path: Path) -> Tuple[Any, bytes]:
    raw = path.read_bytes()
    return load_json_bytes(raw), raw


def json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return format(value, "f")
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    return value


def canonicalize(value: Any) -> Any:
    value = json_safe(value)
    if isinstance(value, list):
        return [canonicalize(v) for v in value]
    if isinstance(value, dict):
        return {k: canonicalize(value[k]) for k in sorted(value)}
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(canonicalize(value), ensure_ascii=False, separators=(",", ":"))


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_id(value: Any) -> str:
    return sha256_hex(canonical_json(value).encode("utf-8"))


def pointer(tokens: Sequence[Union[str, int]]) -> str:
    if not tokens:
        return "/"
    encoded = []
    for token in tokens:
        part = str(token).replace("~", "~0").replace("/", "~1")
        encoded.append(part)
    return "/" + "/".join(encoded)


def normalize_path(path: Any, label: str) -> List[Union[str, int]]:
    if not isinstance(path, list):
        raise BridgeError(f"INVALID_PATH: {label}")
    result: List[Union[str, int]] = []
    for token in path:
        if isinstance(token, bool):
            raise BridgeError(f"INVALID_PATH_TOKEN: {label}")
        if isinstance(token, Decimal):
            if token != token.to_integral_value():
                raise BridgeError(f"INVALID_PATH_TOKEN: {label}")
            result.append(int(token))
        elif isinstance(token, (str, int)):
            result.append(token)
        else:
            raise BridgeError(f"INVALID_PATH_TOKEN: {label}")
    return result


def get_path(root: Any, path: Sequence[Union[str, int]], consumed: set[str], base: Sequence[Union[str, int]] = ()) -> Any:
    cur = root
    walked = list(base)
    for token in path:
        walked.append(token)
        if isinstance(token, int):
            if not isinstance(cur, list) or token < 0 or token >= len(cur):
                return MISSING
            cur = cur[token]
        else:
            if not isinstance(cur, dict) or token not in cur:
                return MISSING
            cur = cur[token]
    consumed.add(pointer(walked))
    return cur


def spec_path(spec: Any, label: str) -> Tuple[List[Union[str, int]], bool, Any]:
    if isinstance(spec, list):
        return normalize_path(spec, label), False, MISSING
    if not isinstance(spec, dict):
        raise BridgeError(f"INVALID_MAPPING_SPEC: {label}")
    path = normalize_path(spec.get("path", []), label)
    required = bool(spec.get("required", False))
    default = spec.get("default", MISSING)
    return path, required, default


def mapped_value(root: Any, spec: Any, label: str, consumed: set[str], base: Sequence[Union[str, int]] = ()) -> Any:
    path, required, default = spec_path(spec, label)
    value = get_path(root, path, consumed, base)
    if value is MISSING or value is None:
        if default is not MISSING:
            return default
        if required:
            raise BridgeError(f"MISSING_REQUIRED_FIELD: {label}")
        return MISSING
    return value


def scalar_text(value: Any, label: str, allow_empty: bool = False) -> str:
    if isinstance(value, bool) or isinstance(value, (dict, list)):
        raise BridgeError(f"INVALID_SCALAR: {label}")
    if isinstance(value, Decimal):
        text = format(value, "f")
    else:
        text = str(value)
    text = text.strip()
    if not text and not allow_empty:
        raise BridgeError(f"EMPTY_REQUIRED_FIELD: {label}")
    return text


def money_text(value: Any, label: str, currency: str) -> str:
    text = scalar_text(value, label)
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        raise BridgeError(f"INVALID_MONEY: {label}")
    exponent = CURRENCY_EXPONENTS.get(currency)
    decimals = len(text.split(".", 1)[1]) if "." in text else 0
    if exponent is not None and decimals > exponent:
        raise BridgeError(f"MONEY_SCALE_EXCEEDS_CURRENCY_EXPONENT: {label}")
    try:
        Decimal(text)
    except InvalidOperation as exc:
        raise BridgeError(f"INVALID_MONEY: {label}") from exc
    return text


def integer_value(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise BridgeError(f"INVALID_INTEGER: {label}")
    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise BridgeError(f"INVALID_INTEGER: {label}") from exc
    if number != number.to_integral_value() or number <= 0:
        raise BridgeError(f"INVALID_POSITIVE_INTEGER: {label}")
    return int(number)


def leaf_paths(value: Any, base: Sequence[Union[str, int]] = ()) -> Iterable[str]:
    if isinstance(value, dict):
        if not value:
            yield pointer(base)
        for key, child in value.items():
            yield from leaf_paths(child, [*base, key])
    elif isinstance(value, list):
        if not value:
            yield pointer(base)
        for index, child in enumerate(value):
            yield from leaf_paths(child, [*base, index])
    else:
        yield pointer(base)


def currency_profile(currency: str) -> str:
    return MONEY_PROFILE if CURRENCY_EXPONENTS.get(currency) == 2 else "UNSUPPORTED_CURRENCY_EXPONENT"


def build_items(source: Any, spec: Dict[str, Any], consumed: set[str], currency: str) -> List[Dict[str, Any]]:
    path = normalize_path(spec.get("path", []), "items.path")
    array = get_path(source, path, consumed)
    if not isinstance(array, list) or not array:
        raise BridgeError("MISSING_REQUIRED_FIELD: items")
    fields = spec.get("fields")
    if not isinstance(fields, dict):
        raise BridgeError("INVALID_ITEMS_FIELDS")
    items: List[Dict[str, Any]] = []
    for index, row in enumerate(array):
        if not isinstance(row, dict):
            raise BridgeError(f"INVALID_ITEM_OBJECT: {index}")
        base = [*path, index]
        desc = mapped_value(row, fields.get("description"), f"items[{index}].description", consumed, base)
        qty = mapped_value(row, fields.get("qty"), f"items[{index}].qty", consumed, base)
        price = mapped_value(row, fields.get("unit_price"), f"items[{index}].unit_price", consumed, base)
        item_id_spec = fields.get("id")
        item_id_value = mapped_value(row, item_id_spec, f"items[{index}].id", consumed, base) if item_id_spec is not None else MISSING
        item_id = scalar_text(item_id_value, f"items[{index}].id") if item_id_value is not MISSING else f"ITEM-{index + 1}"
        items.append(
            {
                "id": item_id,
                "description": scalar_text(desc, f"items[{index}].description"),
                "qty": integer_value(qty, f"items[{index}].qty"),
                "unit_price": money_text(price, f"items[{index}].unit_price", currency),
            }
        )
    return items


def build_payments(source: Any, spec: Any, consumed: set[str], transaction_currency: str) -> List[Dict[str, Any]]:
    if not spec:
        return []
    if not isinstance(spec, dict):
        raise BridgeError("INVALID_PAYMENT_MAPPING")
    path = normalize_path(spec.get("path", []), "payments.path")
    rows = get_path(source, path, consumed)
    if rows is MISSING or rows is None:
        return []
    if not isinstance(rows, list):
        rows = [rows]
    fields = spec.get("fields", {})
    payments: List[Dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise BridgeError(f"INVALID_PAYMENT_OBJECT: {index}")
        base = [*path, index] if isinstance(get_path(source, path, set()), list) else path
        ref = mapped_value(row, fields.get("reference"), f"payments[{index}].reference", consumed, base)
        amount = mapped_value(row, fields.get("amount"), f"payments[{index}].amount", consumed, base)
        currency = mapped_value(row, fields.get("currency"), f"payments[{index}].currency", consumed, base)
        if ref is MISSING and amount is MISSING and currency is MISSING:
            continue
        pay_currency = scalar_text(currency, f"payments[{index}].currency") if currency is not MISSING else transaction_currency
        payments.append(
            {
                "kind": "INDEPENDENT_PAYMENT",
                "reference": scalar_text(ref, f"payments[{index}].reference"),
                "amount": money_text(amount, f"payments[{index}].amount", pay_currency),
                "currency": pay_currency,
            }
        )
    return payments


def build_lineage(source: Any, spec: Any, consumed: set[str], currency: str) -> List[Dict[str, Any]]:
    if not spec:
        return []
    if not isinstance(spec, dict):
        raise BridgeError("INVALID_LINEAGE_MAPPING")
    path = normalize_path(spec.get("path", []), "lineage.path")
    rows = get_path(source, path, consumed)
    if rows is MISSING or rows is None:
        return []
    if not isinstance(rows, list):
        raise BridgeError("INVALID_LINEAGE_ARRAY")
    fields = spec.get("fields", {})
    out: List[Dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise BridgeError(f"INVALID_LINEAGE_OBJECT: {index}")
        base = [*path, index]
        event_type = scalar_text(mapped_value(row, fields.get("type"), f"lineage[{index}].type", consumed, base), f"lineage[{index}].type").upper()
        if event_type not in {"RETURN", "REFUND", "CREDIT"}:
            raise BridgeError(f"UNSUPPORTED_LINEAGE_TYPE: {event_type}")
        amount = money_text(mapped_value(row, fields.get("amount"), f"lineage[{index}].amount", consumed, base), f"lineage[{index}].amount", currency)
        ref_value = mapped_value(row, fields.get("reference"), f"lineage[{index}].reference", consumed, base)
        desc_value = mapped_value(row, fields.get("description"), f"lineage[{index}].description", consumed, base)
        out.append(
            {
                "profile": "SR-LINEAGE-EVENT-1-D01",
                "type": event_type,
                "amount": amount,
                "reference": "" if ref_value is MISSING else scalar_text(ref_value, f"lineage[{index}].reference", True),
                "description": "" if desc_value is MISSING else scalar_text(desc_value, f"lineage[{index}].description", True),
            }
        )
    return out


def bridge(source: Any, source_raw: bytes, manifest: Dict[str, Any]) -> Dict[str, Any]:
    if manifest.get("profile") != MANIFEST_PROFILE:
        raise BridgeError("UNSUPPORTED_ADAPTER_MANIFEST_PROFILE")
    if manifest.get("release_version") != RELEASE_VERSION:
        raise BridgeError("ADAPTER_MANIFEST_RELEASE_MISMATCH")
    adapter_profile_id = scalar_text(manifest.get("adapter_profile_id", ""), "adapter_profile_id")
    mapping = manifest.get("mapping")
    if not isinstance(mapping, dict):
        raise BridgeError("MISSING_MAPPING")
    consumed: set[str] = set()

    merchant = scalar_text(mapped_value(source, mapping.get("merchant"), "merchant", consumed), "merchant")
    receipt_number = scalar_text(mapped_value(source, mapping.get("receipt_number"), "receipt_number", consumed), "receipt_number")
    transaction_date = scalar_text(mapped_value(source, mapping.get("transaction_date"), "transaction_date", consumed), "transaction_date")
    currency = scalar_text(mapped_value(source, mapping.get("currency"), "currency", consumed), "currency").upper()
    items = build_items(source, mapping.get("items", {}), consumed, currency)
    discount_value = mapped_value(source, mapping.get("discount"), "discount", consumed)
    tax_value = mapped_value(source, mapping.get("tax"), "tax", consumed)
    charges_value = mapped_value(source, mapping.get("charges"), "charges", consumed)
    total_value = mapped_value(source, mapping.get("declared_total"), "declared_total", consumed)

    payments = build_payments(source, mapping.get("payments"), consumed, currency)
    lineage = build_lineage(source, mapping.get("lineage"), consumed, currency)

    purpose_mapping = mapping.get("purpose_context", {}) if isinstance(mapping.get("purpose_context", {}), dict) else {}
    business = mapped_value(source, purpose_mapping.get("business_purpose"), "business_purpose", consumed) if purpose_mapping.get("business_purpose") is not None else MISSING
    claimant = mapped_value(source, purpose_mapping.get("claimant_role"), "claimant_role", consumed) if purpose_mapping.get("claimant_role") is not None else MISSING
    warranty = mapped_value(source, purpose_mapping.get("warranty_item_reference"), "warranty_item_reference", consumed) if purpose_mapping.get("warranty_item_reference") is not None else MISSING
    return_amount = mapped_value(source, purpose_mapping.get("requested_return_amount"), "requested_return_amount", consumed) if purpose_mapping.get("requested_return_amount") is not None else MISSING

    context_mapping = mapping.get("evaluation_context", {}) if isinstance(mapping.get("evaluation_context", {}), dict) else {}
    as_of = mapped_value(source, context_mapping.get("as_of"), "evaluation_context.as_of", consumed) if context_mapping.get("as_of") is not None else MISSING
    jurisdiction = mapped_value(source, context_mapping.get("jurisdiction_profile"), "evaluation_context.jurisdiction_profile", consumed) if context_mapping.get("jurisdiction_profile") is not None else MISSING

    warnings = list(manifest.get("declared_warnings", [])) if isinstance(manifest.get("declared_warnings", []), list) else []
    all_leaves = set(leaf_paths(source))
    consumed_leafs = {leaf for leaf in all_leaves if any(leaf == c or leaf.startswith(c + "/") for c in consumed)}
    unmapped = sorted(all_leaves - consumed_leafs)
    if unmapped:
        warnings.append("UNMAPPED_SOURCE_FIELDS_PRESERVED_AS_PATH_LIST")

    receipt = {
        "profile": RECEIPT_PROFILE,
        "schema_version": SCHEMA_VERSION,
        "ruleset_version": RULESET_VERSION,
        "origin": {
            "class": "WRAPPED",
            "source_profile": adapter_profile_id,
            "source_artifact_id": "SHA256:" + sha256_hex(source_raw),
            "unmapped_fields": unmapped,
            "warnings": sorted(set(str(x) for x in warnings)),
        },
        "transaction": {
            "merchant": merchant,
            "receipt_number": receipt_number,
            "date": transaction_date,
            "currency": currency,
            "items": items,
            "discount": money_text(discount_value, "discount", currency),
            "tax": money_text(tax_value, "tax", currency),
            "charges": money_text(charges_value, "charges", currency),
            "declared_total": money_text(total_value, "declared_total", currency),
        },
        "evidence": {"payment": payments},
        "purpose_context": {
            "expense": {
                "business_purpose": "" if business is MISSING else scalar_text(business, "business_purpose", True),
                "claimant_role": "" if claimant is MISSING else scalar_text(claimant, "claimant_role", True),
            },
            "warranty": {
                "item_reference": "" if warranty is MISSING else scalar_text(warranty, "warranty_item_reference", True)
            },
            "return_eligibility": {
                "requested_amount": "" if return_amount is MISSING else money_text(return_amount, "requested_return_amount", currency)
            },
        },
        "lineage": lineage,
        "evaluation_context": {
            "profile": EVALUATION_CONTEXT_PROFILE,
            "as_of": transaction_date if as_of is MISSING else scalar_text(as_of, "evaluation_context.as_of", True),
            "jurisdiction_profile": "UNSPECIFIED" if jurisdiction is MISSING else scalar_text(jurisdiction, "evaluation_context.jurisdiction_profile", True),
            "currency_profile": currency_profile(currency),
        },
    }
    return receipt


def safe_filename_segment(value: str) -> str:
    text = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", value).strip(" .")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    if not text:
        text = "receipt"
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if text.upper() in reserved:
        text = "_" + text
    return text[:96]


def bridge_summary(receipt: Dict[str, Any], manifest: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
    adapter_subject = {
        "profile": ADAPTER_PROFILE,
        "origin_class": receipt["origin"]["class"],
        "source_profile": receipt["origin"]["source_profile"],
        "source_artifact_id": receipt["origin"]["source_artifact_id"],
        "unmapped_fields": receipt["origin"]["unmapped_fields"],
        "warnings": receipt["origin"]["warnings"],
        "origin_authority": "TRANSFORMED_FROM_DECLARED_SOURCE",
        "semantic_equivalence": "NOT_ASSUMED",
    }
    return {
        "profile": BRIDGE_PROFILE,
        "release_version": RELEASE_VERSION,
        "status": "PASS",
        "origin_class": "WRAPPED",
        "semantic_equivalence": "NOT_ASSUMED",
        "source_artifact_id": receipt["origin"]["source_artifact_id"],
        "adapter_profile_id": manifest["adapter_profile_id"],
        "adapter_manifest_id": canonical_id(manifest),
        "adapter_contract_id": canonical_id(adapter_subject),
        "unmapped_field_count": len(receipt["origin"]["unmapped_fields"]),
        "warning_count": len(receipt["origin"]["warnings"]),
        "output": str(output_path),
        "execution_authority": "NONE",
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_output_path(source_path: Path, receipt: Dict[str, Any]) -> Path:
    receipt_no = safe_filename_segment(receipt["transaction"]["receipt_number"])
    return source_path.with_name(f"Structural_Receipt_{receipt_no}_{RELEASE_FILE_VERSION}.json")


def self_test() -> Dict[str, Any]:
    source_text = """{
  "seller": {"name": "Northstar Office Store"},
  "receipt": {"number": "SR-1001", "date": "2026-07-18", "currency": "USD"},
  "lines": [
    {"sku": "ITEM-1", "description": "Portable document scanner", "quantity": 1, "unit_price": "240.00"},
    {"sku": "ITEM-2", "description": "USB-C cable", "quantity": 2, "unit_price": "15.00"}
  ],
  "totals": {"discount": "10.00", "tax": "20.80", "charges": "0.00", "total": "280.80"},
  "payments": [{"reference": "PAY-1001", "amount": "280.80", "currency": "USD"}],
  "context": {"business_purpose": "Office document digitization", "claimant_role": "Employee"},
  "unused": {"legacy_code": "L-7"}
}"""
    manifest = {
        "profile": MANIFEST_PROFILE,
        "release_version": RELEASE_VERSION,
        "adapter_profile_id": "SR-GENERIC-JSON-ADAPTER-1-D01",
        "mapping": {
            "merchant": {"path": ["seller", "name"], "required": True},
            "receipt_number": {"path": ["receipt", "number"], "required": True},
            "transaction_date": {"path": ["receipt", "date"], "required": True},
            "currency": {"path": ["receipt", "currency"], "required": True},
            "items": {
                "path": ["lines"],
                "fields": {
                    "id": {"path": ["sku"]},
                    "description": {"path": ["description"], "required": True},
                    "qty": {"path": ["quantity"], "required": True},
                    "unit_price": {"path": ["unit_price"], "required": True},
                },
            },
            "discount": {"path": ["totals", "discount"], "default": "0.00"},
            "tax": {"path": ["totals", "tax"], "default": "0.00"},
            "charges": {"path": ["totals", "charges"], "default": "0.00"},
            "declared_total": {"path": ["totals", "total"], "required": True},
            "payments": {
                "path": ["payments"],
                "fields": {
                    "reference": {"path": ["reference"], "required": True},
                    "amount": {"path": ["amount"], "required": True},
                    "currency": {"path": ["currency"]},
                },
            },
            "purpose_context": {
                "business_purpose": {"path": ["context", "business_purpose"]},
                "claimant_role": {"path": ["context", "claimant_role"]},
            },
        },
    }
    raw = source_text.encode("utf-8")
    source = load_json_bytes(raw)
    receipt = bridge(source, raw, manifest)
    receipt2 = bridge(source, raw, manifest)
    checks: List[Tuple[str, bool]] = []
    checks.append(("profile", receipt["profile"] == RECEIPT_PROFILE))
    checks.append(("schema version", receipt["schema_version"] == SCHEMA_VERSION))
    checks.append(("ruleset version", receipt["ruleset_version"] == RULESET_VERSION))
    checks.append(("wrapped origin", receipt["origin"]["class"] == "WRAPPED"))
    checks.append(("source profile", receipt["origin"]["source_profile"] == manifest["adapter_profile_id"]))
    checks.append(("source artifact hash", receipt["origin"]["source_artifact_id"] == "SHA256:" + sha256_hex(raw)))
    checks.append(("merchant mapped", receipt["transaction"]["merchant"] == "Northstar Office Store"))
    checks.append(("two items mapped", len(receipt["transaction"]["items"]) == 2))
    checks.append(("quantity integer", receipt["transaction"]["items"][1]["qty"] == 2))
    checks.append(("payment mapped", receipt["evidence"]["payment"][0]["reference"] == "PAY-1001"))
    checks.append(("context mapped", receipt["purpose_context"]["expense"]["business_purpose"] == "Office document digitization"))
    checks.append(("as_of defaults transaction date", receipt["evaluation_context"]["as_of"] == "2026-07-18"))
    checks.append(("currency profile", receipt["evaluation_context"]["currency_profile"] == MONEY_PROFILE))
    checks.append(("unmapped path preserved", "/unused/legacy_code" in receipt["origin"]["unmapped_fields"]))
    checks.append(("deterministic output", canonical_json(receipt) == canonical_json(receipt2)))
    try:
        load_json_bytes(b'{"a":1,"a":2}')
        duplicate_rejected = False
    except BridgeError:
        duplicate_rejected = True
    checks.append(("duplicate JSON rejected", duplicate_rejected))
    broken = json.loads(json.dumps(json_safe(source)))
    del broken["receipt"]["number"]
    try:
        bridge(broken, raw, manifest)
        missing_rejected = False
    except BridgeError:
        missing_rejected = True
    checks.append(("missing required field rejected", missing_rejected))
    invalid_qty = json.loads(json.dumps(json_safe(source)))
    invalid_qty["lines"][0]["quantity"] = '1" autofocus onfocus="window.__SR_UI_INJECTED=1'
    try:
        bridge(invalid_qty, raw, manifest)
        invalid_qty_rejected = False
    except BridgeError:
        invalid_qty_rejected = True
    checks.append(("invalid quantity rejected", invalid_qty_rejected))
    jpy = json.loads(json.dumps(json_safe(source)))
    jpy["receipt"]["currency"] = "JPY"
    jpy["lines"][0]["unit_price"] = "240"
    jpy["lines"][1]["unit_price"] = "15"
    jpy["totals"] = {"discount": "10", "tax": "20", "charges": "0", "total": "280"}
    jpy["payments"][0]["amount"] = "280"
    jpy["payments"][0]["currency"] = "JPY"
    jpy_receipt = bridge(jpy, json.dumps(jpy, separators=(",", ":")).encode(), manifest)
    checks.append(("unsupported exponent explicit", jpy_receipt["evaluation_context"]["currency_profile"] == "UNSUPPORTED_CURRENCY_EXPONENT"))
    changed_raw = raw + b"\n"
    changed_receipt = bridge(source, changed_raw, manifest)
    checks.append(("byte identity changes", changed_receipt["origin"]["source_artifact_id"] != receipt["origin"]["source_artifact_id"]))
    checks.append(("semantic equivalence not assumed", bridge_summary(receipt, manifest, Path("out.json"))["semantic_equivalence"] == "NOT_ASSUMED"))
    passed = sum(1 for _, ok in checks if ok)
    return {"status": "PASS" if passed == len(checks) else "FAIL", "pass": passed, "total": len(checks), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="Structural_Receipt_Bridge_v0_5_3.py",
        description="Convert declared external JSON into a provenance-preserving WRAPPED Structural Receipt v0.5.3 sidecar.",
    )
    parser.add_argument("source", nargs="?", help="Source JSON file")
    parser.add_argument("--manifest", help="Adapter manifest JSON file")
    parser.add_argument("--output", help="Output Structural Receipt JSON file")
    parser.add_argument("--summary-json", action="store_true", help="Print the bridge result as JSON")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in deterministic bridge regression test")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        if args.summary_json:
            print(json.dumps({"status": result["status"], "pass": result["pass"], "total": result["total"]}, indent=2))
        else:
            print(f"Structural Receipt Bridge v{RELEASE_VERSION} Self-Test")
            for name, ok in result["checks"]:
                print(f"{'PASS' if ok else 'FAIL'}  {name}")
            print(f"\nRESULT: {result['pass']}/{result['total']} {result['status']}")
        return 0 if result["status"] == "PASS" else 1

    if not args.source or not args.manifest:
        parser.error("source and --manifest are required unless --self-test is used")

    source_path = Path(args.source)
    manifest_path = Path(args.manifest)
    try:
        source, source_raw = load_json_file(source_path)
        manifest, _ = load_json_file(manifest_path)
        if not isinstance(source, dict):
            raise BridgeError("SOURCE_ROOT_MUST_BE_OBJECT")
        if not isinstance(manifest, dict):
            raise BridgeError("MANIFEST_ROOT_MUST_BE_OBJECT")
        receipt = bridge(source, source_raw, manifest)
        output_path = Path(args.output) if args.output else default_output_path(source_path, receipt)
        write_json(output_path, receipt)
        summary = bridge_summary(receipt, manifest, output_path)
    except (OSError, BridgeError) as exc:
        if args.summary_json:
            print(json.dumps({"profile": BRIDGE_PROFILE, "release_version": RELEASE_VERSION, "status": "FAIL", "error": str(exc)}, indent=2))
        else:
            print(f"Structural Receipt Bridge v{RELEASE_VERSION}")
            print("STATUS: FAIL")
            print(f"ERROR: {exc}")
        return 1

    if args.summary_json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Structural Receipt Bridge v{RELEASE_VERSION}")
        print("Adopt on one side. Verify on the other. Integrate only when useful.")
        print()
        print("STATUS: PASS")
        print(f"OUTPUT: {output_path}")
        print("ORIGIN CLASS: WRAPPED")
        print(f"SOURCE PROFILE: {summary['adapter_profile_id']}")
        print(f"SOURCE ARTIFACT ID: {summary['source_artifact_id']}")
        print(f"UNMAPPED SOURCE FIELDS: {summary['unmapped_field_count']}")
        print("SEMANTIC EQUIVALENCE: NOT_ASSUMED")
        print("EXECUTION AUTHORITY: NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
