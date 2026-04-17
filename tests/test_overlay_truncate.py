from __future__ import annotations

import unittest

from my_agent_girlfriend.app_bridge import OVERLAY_MAX_CHARS, _truncate_for_overlay


class OverlayTruncateTests(unittest.TestCase):
    def test_short_text_passes_through(self) -> None:
        text = "응! 알렉스~ 오늘도 옆에 있어줄게."
        self.assertEqual(_truncate_for_overlay(text), text)

    def test_exact_limit_passes_through(self) -> None:
        text = "가" * OVERLAY_MAX_CHARS
        self.assertEqual(_truncate_for_overlay(text), text)

    def test_over_limit_gets_ellipsis(self) -> None:
        text = "가" * (OVERLAY_MAX_CHARS + 20)
        result = _truncate_for_overlay(text)
        self.assertTrue(result.endswith("..."))
        self.assertEqual(len(result), OVERLAY_MAX_CHARS + 3)

    def test_trailing_whitespace_stripped_before_ellipsis(self) -> None:
        text = "가" * (OVERLAY_MAX_CHARS - 1) + " " + "나" * 10
        result = _truncate_for_overlay(text)
        self.assertFalse(" ..." in result)
        self.assertTrue(result.endswith("..."))


if __name__ == "__main__":
    unittest.main()
