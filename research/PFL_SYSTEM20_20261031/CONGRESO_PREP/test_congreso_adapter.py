"""Synthetic-only boundary tests; never request Congress or any remote host."""

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import unittest

import congreso_adapter as a


def synthetic_pages():
    root = Path(__file__).parent / "fixtures"
    return {number: (root / f"page_{number}.json").read_bytes() for number in (1, 2)}


def adjusted(change, *, page=1):
    pages = synthetic_pages()
    data = json.loads(pages[page])
    change(data)
    pages[page] = json.dumps(data).encode()
    return pages


class SyntheticBoundaryTests(unittest.TestCase):
    def test_fixture_pagination_and_exact_dedup(self):
        corpus = a.ingest_paginated_pages(synthetic_pages())
        self.assertEqual(corpus["page_numbers"], [1, 2])
        self.assertEqual(corpus["distinct_initiatives"], 3)
        self.assertEqual(corpus["duplicate_identical_rows"], 1)
        self.assertEqual(corpus["index_claimed_total"], 3)
        self.assertFalse(corpus["source_population_complete"])
        self.assertEqual(corpus["real_source_records"], 0)

    def test_first_public_is_never_inferred_from_registration_or_bocg_day(self):
        corpus = a.ingest_paginated_pages(synthetic_pages())
        self.assertTrue(all(row["first_public_at"] is None for row in corpus["records"]))
        states = {row["expediente"]: row["publication_gate"] for row in corpus["records"]}
        self.assertEqual(states["121/900001"], "DATED_BOCG_REFERENCE_BEFORE_CUTOFF_UNATTESTED")
        self.assertEqual(states["121/900002"], "UNKNOWN_FIRST_PUBLIC_DAY")
        self.assertEqual(states["121/900003"], "SAME_DAY_TIME_UNKNOWN")

    def test_cutoff_all_rows_censored_without_outcomes(self):
        corpus = a.ingest_paginated_pages(synthetic_pages())
        for row in corpus["records"]:
            self.assertEqual(row["censor_at"], "2026-10-31")
            self.assertIn("RIGHT_CENSORED", row["censoring_kind"])
            self.assertNotIn("outcome", row)
            self.assertNotIn("status", row)

    def test_missing_page_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "MISSING_PAGINATION_PAGE"):
            a.ingest_paginated_pages({1: synthetic_pages()[1]})

    def test_referenced_and_unreferenced_pages_rejected(self):
        def remove_next(p):
            p["next_page"] = None
        with self.assertRaisesRegex(ValueError, "UNREFERENCED_PAGES"):
            a.ingest_paginated_pages(adjusted(remove_next))

    def test_backward_cursor_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_OR_CYCLIC_NEXT_PAGE"):
            a.ingest_paginated_pages(adjusted(lambda p: p.update(next_page=1)))

    def test_reported_total_mismatch(self):
        with self.assertRaisesRegex(ValueError, "INCONSISTENT_REPORTED_TOTAL"):
            a.ingest_paginated_pages(adjusted(lambda p: p.update(reported_total=4)))

    def test_missing_record_detected_against_index_total(self):
        with self.assertRaisesRegex(ValueError, "PAGINATED_INDEX_TOTAL_MISMATCH"):
            a.ingest_paginated_pages(adjusted(lambda p: p["records"].pop(), page=2))

    def test_conflicting_duplicate_fails_closed(self):
        def change(p):
            p["records"][0]["presented_on"] = "2026-10-19"
        with self.assertRaisesRegex(ValueError, "CONFLICTING_DUPLICATE_RECORD"):
            a.ingest_paginated_pages(adjusted(change, page=2))

    def test_wrong_legislature_not_merged(self):
        def change(p):
            p["legislature"] = "XIV"
        with self.assertRaisesRegex(ValueError, "PAGE_STRATUM_OR_NUMBER_CONFLICT"):
            a.ingest_paginated_pages(adjusted(change, page=2))

    def test_outcomes_and_full_status_forbidden(self):
        for banned in ("outcome", "resultado_tramitacion", "status_final", "votes_yes", "approved"):
            with self.subTest(banned=banned):
                def change(p):
                    p["records"][0][banned] = "fictional"
                with self.assertRaisesRegex(ValueError, "FORBIDDEN_OUTCOME_OR_FUTURE_FIELD"):
                    a.ingest_paginated_pages(adjusted(change))

    def test_unexpected_future_registration(self):
        with self.assertRaisesRegex(ValueError, "FUTURE_INITIATIVE_IN_SNAPSHOT"):
            a.ingest_paginated_pages(adjusted(lambda p: p["records"][0].update(presented_on="2026-12-01", qualified_on="2026-12-02", first_bocg_day="2026-12-03")))

    def test_qualification_before_presentation(self):
        with self.assertRaisesRegex(ValueError, "QUALIFICATION_BEFORE_PRESENTATION"):
            a.ingest_paginated_pages(adjusted(lambda p: p["records"][0].update(qualified_on="2026-08-19")))

    def test_first_bocg_before_registration(self):
        with self.assertRaisesRegex(ValueError, "BOCG_BEFORE_PRESENTATION"):
            a.ingest_paginated_pages(adjusted(lambda p: p["records"][0].update(first_bocg_day="2026-08-19")))

    def test_url_validation_rejects_lookalike_hosts_and_credentials(self):
        for url in (
            "https://www.congreso.es.evil.test/public_oficiales/fake.pdf",
            "https://evil.test@www.congreso.es/public_oficiales/fake.pdf",
            "http://www.congreso.es/public_oficiales/fake.pdf",
            "https://www.congreso.es/private/fake.pdf",
        ):
            with self.subTest(url=url):
                self.assertFalse(a.good_official_document_url(url))

    def test_synthetic_csv_adapter(self):
        raw = ("legislature,expediente,presented_on,qualified_on,first_bocg_day,first_bocg_url\n"
               "XV,121/900001,2026-08-20,2026-08-25,2026-08-28,https://www.congreso.es/public_oficiales/SYNTHETIC.csv\n")
        payload = a.parse_offline_csv(raw.encode(), legislature="XV", type_code="121", page=1, next_page=None, reported_total=1)
        self.assertEqual(a.ingest_paginated_pages({1: payload})["distinct_initiatives"], 1)

    def test_csv_rejects_unexpected_outcome_column(self):
        raw = "legislature,expediente,presented_on,qualified_on,first_bocg_day,first_bocg_url,outcome\n"
        with self.assertRaisesRegex(ValueError, "CSV_UNKNOWN_SCHEMA"):
            a.parse_offline_csv(raw.encode(), legislature="XV", type_code="121", page=1, next_page=None, reported_total=0)

    def test_csv_rejects_duplicate_headers(self):
        raw = "legislature,legislature,expediente,presented_on,qualified_on,first_bocg_day,first_bocg_url\n"
        with self.assertRaisesRegex(ValueError, "DUPLICATE_OR_MISSING_CSV_HEADERS"):
            a.parse_offline_csv(raw.encode(), legislature="XV", type_code="121", page=1, next_page=None, reported_total=0)

    def test_unrecognized_official_export_schema_never_assumed(self):
        pages = adjusted(lambda p: p.update(schema="UNKNOWN_OFFICIAL_API"))
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_FORMAT"):
            a.ingest_paginated_pages(pages)

    def test_absent_first_day_may_not_claim_a_bocg_url(self):
        with self.assertRaisesRegex(ValueError, "BOCG_URL_WITHOUT_DAY"):
            a.ingest_paginated_pages(adjusted(lambda p: p["records"][1].update(first_bocg_url="https://www.congreso.es/public_oficiales/FAKE.pdf")))


if __name__ == "__main__":
    unittest.main()
