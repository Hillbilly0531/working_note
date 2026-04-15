# SQL Review Tool Vibe Coding Share Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a single-file HTML presentation that turns the SQL Review Tool Vibe Coding retrospective into a 9-slide, fullscreen, keyboard-driven share page.

**Architecture:** The deliverable will be one standalone HTML file with inline CSS and JavaScript. A lightweight Python unittest will verify structural requirements such as slide count, required labels, page metadata, and keyboard control hooks so the presentation is not validated only by visual inspection.

**Tech Stack:** HTML, CSS, vanilla JavaScript, Python unittest

---

### Task 1: Create the presentation structure test

**Files:**
- Create: `tests/test_sql_review_tool_share.py`
- Test: `tests/test_sql_review_tool_share.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import re
import unittest


HTML_PATH = Path(r"d:\IdeaProjects\working_note\leyo\文档\sql-review-tool-vibe-coding-share.html")


class SqlReviewToolShareTest(unittest.TestCase):
    def test_presentation_file_contains_required_structure(self):
        html = HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("SQL Review Tool", html)
        self.assertEqual(len(re.findall(r'<section class="slide', html)), 9)
        self.assertIn("Plan Mode", html)
        self.assertIn("Agent Mode", html)
        self.assertIn("Debug Mode", html)
        self.assertIn("page-indicator", html)
        self.assertIn("chapter-indicator", html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: FAIL because the HTML presentation file does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create the single-file HTML with 9 slides and the required indicator elements.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_sql_review_tool_share.py leyo/文档/sql-review-tool-vibe-coding-share.html
git commit -m "feat: add sql review tool html share"
```

### Task 2: Implement the slideshow shell and visual system

**Files:**
- Modify: `leyo/文档/sql-review-tool-vibe-coding-share.html`
- Test: `tests/test_sql_review_tool_share.py`

- [ ] **Step 1: Extend the failing test for slide metadata**

```python
self.assertIn('data-title="封面"', html)
self.assertIn('data-title="项目背景"', html)
self.assertIn('data-title="工作流"', html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: FAIL until all slide metadata is present.

- [ ] **Step 3: Write minimal implementation**

Add:
- fixed fullscreen slide layout
- 16:9 presentation frame behavior
- background grid and glow system
- slide-level `data-title` metadata
- page and chapter indicators

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_sql_review_tool_share.py leyo/文档/sql-review-tool-vibe-coding-share.html
git commit -m "feat: add slideshow shell and visual system"
```

### Task 3: Implement slide content and keyboard navigation

**Files:**
- Modify: `leyo/文档/sql-review-tool-vibe-coding-share.html`
- Modify: `tests/test_sql_review_tool_share.py`
- Test: `tests/test_sql_review_tool_share.py`

- [ ] **Step 1: Extend the failing test for interaction hooks**

```python
self.assertIn("keydown", html)
self.assertIn("ArrowRight", html)
self.assertIn("ArrowLeft", html)
self.assertIn("Home", html)
self.assertIn("End", html)
self.assertIn("不是让 AI 代替开发", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: FAIL until navigation logic and final copy are added.

- [ ] **Step 3: Write minimal implementation**

Add:
- all 9 slides with condensed presentation copy
- keyboard navigation logic
- active slide state updates
- page count display and chapter label updates
- restrained animation classes for slide entry

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_sql_review_tool_share.py leyo/文档/sql-review-tool-vibe-coding-share.html
git commit -m "feat: complete sql review tool share presentation"
```

### Task 4: Verify local delivery quality

**Files:**
- Modify: `leyo/文档/sql-review-tool-vibe-coding-share.html` (only if verification reveals an issue)
- Test: `tests/test_sql_review_tool_share.py`

- [ ] **Step 1: Run the automated test suite**

Run: `python -m unittest tests.test_sql_review_tool_share -v`
Expected: PASS

- [ ] **Step 2: Run a static parse check**

Run: `python -m py_compile tests/test_sql_review_tool_share.py`
Expected: PASS

- [ ] **Step 3: Inspect the generated file size and timestamp**

Run: `Get-Item 'd:\IdeaProjects\working_note\leyo\文档\sql-review-tool-vibe-coding-share.html' | Select-Object FullName, Length, LastWriteTime`
Expected: file exists with a recent timestamp and non-trivial size

- [ ] **Step 4: Commit**

```bash
git add tests/test_sql_review_tool_share.py leyo/文档/sql-review-tool-vibe-coding-share.html
git commit -m "chore: verify sql review tool share delivery"
```
