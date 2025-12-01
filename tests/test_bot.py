"""Basic integration tests for the hotel chatbot."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bot import HotelChatbot


class HotelChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bot = HotelChatbot(auto_train=True, max_training_rows=1000, confidence_threshold=0.25)

    def test_reservation_flow(self) -> None:
        result = self.bot.respond("Please book a deluxe room for 2 adults from 2025-12-10 to 2025-12-12")
        self.assertIn(result["intent"], {"make_reservation", "inquire_availability", "inquire_price", "unknown", "invalid_input"})
        self.assertTrue(result["response"])  # non-empty reply

    def test_unknown_intent(self) -> None:
        result = self.bot.respond("blargle zzz 12345")
        self.assertTrue(result["response"].strip())
        self.assertIn(result["intent"], {"unknown", "inquire_availability", "inquire_price", "make_reservation", "invalid_input"})


if __name__ == "__main__":
    unittest.main()
