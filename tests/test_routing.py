from __future__ import annotations

import unittest

from my_agent_girlfriend.routing import choose_preset


class RoutingTests(unittest.TestCase):
    def test_bashful_keywords_route_to_bashful_blush(self) -> None:
        self.assertEqual(choose_preset("수줍게 말해줘"), "bashful_blush")

    def test_apology_and_look_up_route_to_apology_preset(self) -> None:
        self.assertEqual(choose_preset("미안해, 화났어? 올려다보면서 사과해"), "apology_look_up")

    def test_dont_leave_routes_to_pleading(self) -> None:
        self.assertEqual(choose_preset("날 버리지 말아줘. 가지마."), "pleading_look_up")

    def test_unmatched_defaults_to_neutral(self) -> None:
        self.assertEqual(choose_preset("오늘도 같이 있어줘"), "neutral_smile")


if __name__ == "__main__":
    unittest.main()

