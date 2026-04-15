from pathlib import Path
import re
import unittest


HTML_PATH = Path(r"d:\IdeaProjects\working_note\leyo\文档\sql-review-tool-vibe-coding-share.html")


class SqlReviewToolShareTest(unittest.TestCase):
    def test_presentation_file_contains_required_structure(self):
        html = HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("SQL Review Tool", html)
        self.assertEqual(len(re.findall(r'<section class="slide', html)), 9)
        self.assertIn('data-title="封面"', html)
        self.assertIn('data-title="项目背景"', html)
        self.assertIn('data-title="工作流"', html)
        self.assertIn("Plan Mode", html)
        self.assertIn("Agent Mode", html)
        self.assertIn("Debug Mode", html)
        self.assertIn("page-indicator", html)
        self.assertIn("chapter-indicator", html)
        self.assertIn("keydown", html)
        self.assertIn("ArrowRight", html)
        self.assertIn("ArrowLeft", html)
        self.assertIn("Home", html)
        self.assertIn("End", html)
        self.assertIn("不是让 AI 代替开发", html)


if __name__ == "__main__":
    unittest.main()
