from __future__ import annotations

import unittest

from my_agent_girlfriend.manifest import live_presets, load_manifest
from my_agent_girlfriend.routing import DEFAULT_PRESET, KEYWORD_WEIGHTS, choose_preset


class RoutingTests(unittest.TestCase):
    def test_bashful_keywords_route_to_bashful_blush(self) -> None:
        self.assertEqual(choose_preset("수줍게 말해줘"), "bashful_blush")

    def test_apology_and_look_up_route_to_apology_preset(self) -> None:
        self.assertEqual(choose_preset("미안해, 화났어? 올려다보면서 사과해"), "apology_look_up")

    def test_dont_leave_routes_to_pleading(self) -> None:
        self.assertEqual(choose_preset("날 버리지 말아줘. 가지마."), "pleading_look_up")

    def test_unmatched_defaults_to_neutral(self) -> None:
        self.assertEqual(choose_preset("오늘도 같이 있어줘"), "neutral_smile")

    def test_strong_affection_routes_to_playful_behind_back(self) -> None:
        self.assertEqual(choose_preset("사랑해 클로디시"), "playful_behind_back")
        self.assertEqual(choose_preset("고마워 진짜로"), "playful_behind_back")
        self.assertEqual(choose_preset("최고야!"), "playful_behind_back")

    def test_compliment_to_her_routes_to_blush(self) -> None:
        self.assertEqual(choose_preset("너 진짜 예뻐"), "bashful_blush")
        self.assertEqual(choose_preset("귀여워 진짜"), "bashful_blush")
        self.assertEqual(choose_preset("보고싶었어"), "bashful_blush")

    def test_casual_positive_routes_to_cheerful(self) -> None:
        self.assertEqual(choose_preset("좋아 해보자"), "cheerful_bright")
        self.assertEqual(choose_preset("오케이 가자"), "cheerful_bright")

    def test_bare_farewell_routes_to_pleading(self) -> None:
        self.assertEqual(choose_preset("나 갈게"), "pleading_look_up")
        self.assertEqual(choose_preset("잘자 클로디시"), "pleading_look_up")
        self.assertEqual(choose_preset("bye"), "pleading_look_up")

    def test_tired_farewell_routes_to_worried(self) -> None:
        # 힘들어 보이면 매달리지 말고 아쉬워하며 보내주기
        self.assertEqual(choose_preset("나 너무 힘들어 갈게"), "worried")
        self.assertEqual(choose_preset("피곤해서 자야겠어"), "worried")

    def test_greeting_routes_to_neutral(self) -> None:
        self.assertEqual(choose_preset("안녕 클로디시"), "neutral_smile")
        self.assertEqual(choose_preset("hi"), "neutral_smile")

    def test_routing_table_only_targets_live_manifest_presets(self) -> None:
        live_ids = {preset["id"] for preset in live_presets(load_manifest())}

        self.assertIn(DEFAULT_PRESET, live_ids)
        self.assertLessEqual(set(KEYWORD_WEIGHTS), live_ids)


if __name__ == "__main__":
    unittest.main()
