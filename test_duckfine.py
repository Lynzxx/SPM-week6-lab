import unittest

from duckfine import DuckFine


class DuckFineTests(unittest.TestCase):
    def test_stores_member_id_and_starts_with_no_balance(self):
        fine = DuckFine("member-123")

        self.assertEqual(fine.member_id, "member-123")
        self.assertEqual(fine.total_owed, 0.0)

    def test_rejects_negative_days_late(self):
        fine = DuckFine("member-123")

        with self.assertRaisesRegex(ValueError, "days_late must not be negative"):
            fine.charge(-1)

    def test_forgives_the_grace_period(self):
        fine = DuckFine("member-123")

        self.assertEqual(fine.charge(2), 0.0)

    def test_charges_daily_fee_after_grace_period(self):
        fine = DuckFine("member-123")

        self.assertEqual(fine.charge(4), 1.0)

    def test_deluxe_charge_is_doubled(self):
        fine = DuckFine("member-123")

        self.assertEqual(fine.charge(4, deluxe=True), 2.0)

    def test_each_charge_is_capped_at_maximum_fee(self):
        fine = DuckFine("member-123")

        self.assertEqual(fine.charge(20), 5.0)

    def test_accumulates_each_charge_in_total_owed(self):
        fine = DuckFine("member-123")

        fine.charge(3)
        fine.charge(4, deluxe=True)

        self.assertEqual(fine.total_owed, 2.5)


if __name__ == "__main__":
    unittest.main()