"""Synthetic tests of primary-key, schema and date gates. No real outcomes."""

from __future__ import annotations

from io import StringIO
import csv
import unittest

import coverage_only as mod

SCOPE = {"year": 2024, "legislature": 11, "initiative_type": "PE"}


def make_csv(records, header=None):
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\r\n")
    writer.writerow(list(mod.EXPECTED_HEADERS) if header is None else header)
    writer.writerows(records)
    return stream.getvalue().encode("utf-8")


def one(ident, created, leg="XI", outcome="CONCLUDED", final="RESULT"):
    return [ident, leg, "Fictitious placeholder", created, outcome, "SYNTH", final, "SYNTH"]


class CoverageOnlyTests(unittest.TestCase):
    def test_no_rows_logged_and_outcomes_uninspected(self):
        raw = make_csv([
            one("SYNTH-A", "12/02/2024", outcome="PERSONALLY_SENSITIVE_ALPHA"),
            one("SYNTH-B", "17/03/2024", outcome="PERSONALLY_SENSITIVE_BETA"),
        ])
        summary = mod.audit_bytes(raw, scope=SCOPE)
        self.assertEqual(summary["records_read"], 2)
        self.assertEqual(summary["distinct_nonmissing_id_legislature_keys"], 2)
        self.assertEqual(summary["date_string_shape_counts"], {"dd/mm/yyyy": 2})
        self.assertTrue(summary["full_csv_rows_parsed_for_structure"])
        self.assertTrue(summary["outcome_values_not_inspected_or_aggregated"])
        self.assertNotIn("SYNTH-A", str(summary))
        self.assertNotIn("PERSONALLY_SENSITIVE", str(summary))
        self.assertIsNone(summary["first_public_at"])

    def test_exact_duplicate_and_conflicting_creation_are_separated(self):
        raw = make_csv([
            one("SYNTH-A", "12/02/2024"),
            one("SYNTH-A", "12/02/2024", outcome="DIFFERENT_OUTCOME_NOT_INTERPRETED"),
            one("SYNTH-A", "13/02/2024"),
            one("SYNTH-B", ""),
        ])
        data = mod.audit_bytes(raw, scope=SCOPE)
        self.assertEqual(data["records_read"], 4)
        self.assertEqual(data["distinct_nonmissing_id_legislature_keys"], 2)
        self.assertEqual(data["same_key_same_metadata_rows"], 1)
        self.assertEqual(data["same_key_conflicting_creation_date_rows"], 1)
        self.assertEqual(data["missing_creation_date"], 1)

    def test_missing_ids_and_legislature_are_never_miscounted(self):
        rows = [one("", "2024-09-01"), one("SYNTH", "2024-09-02", leg="")]
        result = mod.audit_bytes(make_csv(rows), scope=SCOPE)
        self.assertEqual(result["missing_primary_key_rows"], 2)
        self.assertEqual(result["distinct_nonmissing_id_legislature_keys"], 0)
        self.assertEqual(result["missing_id"], 1)
        self.assertEqual(result["missing_legislature"], 1)

    def test_unrecognized_or_duplicate_headers_rejected(self):
        rows = [one("SYNTH", "12/02/2024")]
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_CSV_HEADERS"):
            mod.audit_bytes(make_csv(rows, header=["ID_INICIATIVA"] * 8), scope=SCOPE)
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_CSV_HEADERS"):
            mod.audit_bytes(make_csv(rows, header=list(mod.EXPECTED_HEADERS[:-1]) + ["EXTRA"]), scope=SCOPE)

    def test_malformed_row_and_nul_rejected(self):
        with self.assertRaisesRegex(ValueError, "BAD_ROW_SHAPE"):
            mod.audit_bytes(make_csv([one("SYNTH", "12/02/2024")[:-1]]), scope=SCOPE)
        with self.assertRaisesRegex(ValueError, "EMBEDDED_NUL"):
            mod.audit_bytes(make_csv([one("SYNTH", "12/02/2024")]) + b"\x00", scope=SCOPE)

    def test_encoding_and_binary_and_oversize_rejected(self):
        with self.assertRaisesRegex(ValueError, "NON_UTF8"):
            mod.audit_bytes(b'ID_INICIATIVA,\xff', scope=SCOPE)
        with self.assertRaisesRegex(ValueError, "BAD_SIZE_OR_TYPE"):
            mod.audit_bytes(b"x" * (mod.MAX_BYTES + 1), scope=SCOPE)

    def test_date_shapes_do_not_imply_publish_time(self):
        self.assertEqual(mod.date_format("2024-01-03"), "yyyy-mm-dd")
        self.assertEqual(mod.date_format("03/01/2024 09:55"), "dd/mm/yyyy_hh_mm")
        self.assertEqual(mod.date_format("2024-01-03T09:55:11Z"), "iso8601")
        self.assertEqual(mod.date_format(""), "missing")
        self.assertEqual(mod.date_format("ayer"), "unrecognized")

    def test_different_legislatures_never_share_key(self):
        rows = [one("SYNTH-A", "2024-01-03", leg="X"), one("SYNTH-A", "2024-01-03", leg="XI")]
        result = mod.audit_bytes(make_csv(rows), scope=SCOPE)
        self.assertEqual(result["distinct_nonmissing_id_legislature_keys"], 2)
        self.assertEqual(result["distinct_legislature_labels"], 2)

    def test_bom_is_accepted(self):
        data = mod.audit_bytes(b"\xef\xbb\xbf" + make_csv([one("SYNTH", "2024-01-03")]), scope=SCOPE)
        self.assertEqual(data["records_read"], 1)
        self.assertFalse(data["complete_congress_population"])

    def test_headers_with_extra_output_feature_rejected(self):
        cols = list(mod.EXPECTED_HEADERS) + ["NEW_ESTIMATED_SUCCESS"]
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_CSV_HEADERS"):
            mod.audit_bytes(make_csv([one("SYNTH", "2024-01-03") + ["1"]], header=cols), scope=SCOPE)


if __name__ == "__main__":
    unittest.main()
