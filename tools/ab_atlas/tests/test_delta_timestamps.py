"""C01 (MAIN20B): validate batch time syntax without rewriting historical Atlas.
This is only metadata syntax; parent_batch, not wall clocks, orders patches.
"""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import atlas_delta as delta


class BatchTimestampTests(unittest.TestCase):
    def sample(self, timestamp):
        return {
            "schema": delta.PATCH_SCHEMA,
            "batch_id": "SYNTHETIC-TIMESTAMP-C01",
            "at": timestamp,
            "parent_batch": "",
            "reason": "Synthetic negative-control timestamp validation",
            "ops": [],
        }

    def test_reject_bad_calendar_naive_and_date_only(self):
        for at in (
            "not-a-timestamp",
            "2026-10-28T12:10:00",
            "2026-02-31T00:00:00Z",
            "2026-10-28",
            "",
            "2026-10-28T12:10:00+99:99",
            "2026-10-28T12:10:00+01:99",
            None,
        ):
            with self.subTest(at=at), self.assertRaisesRegex(ValueError, "Timestamp ISO-8601"):
                delta.batch_check(self.sample(at))

    def test_accept_timezone_aware_instants(self):
        for at in (
            "2026-10-28T12:10:00Z",
            "2026-10-28T12:10:00+01:00",
            "2026-10-28T12:10:00.123456+00:00",
        ):
            with self.subTest(at=at):
                delta.batch_check(self.sample(at))

    def test_all_committed_atlas_batch_timestamps_are_backward_compatible(self):
        root = Path(__file__).resolve().parents[2]
        folder = root / "proyectos" / "politics-fantasy-league" / "ab_atlas" / "updates"
        files = sorted(folder.glob("*.json"))
        self.assertGreaterEqual(len(files), 55)
        for file in files:
            with self.subTest(file=file.name):
                delta.batch_check(json.loads(file.read_text(encoding="utf-8")))

    def test_historical_patch_order_is_not_a_timing_claim(self):
        # Intentionally diagnostic, not a global monotonic-time invariant:
        # 0015 = 2026-10-27T14:21:01+01:00, while
        # 0016 = 2026-10-27T12:55:27+00:00 (25m34s earlier).
        self.assertTrue(delta.valid_batch_timestamp("2026-10-27T14:21:01+01:00"))
        self.assertTrue(delta.valid_batch_timestamp("2026-10-27T12:55:27+00:00"))


if __name__ == "__main__":
    unittest.main()
