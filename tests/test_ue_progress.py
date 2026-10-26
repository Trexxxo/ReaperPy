"""Progress indicator and genuine UE object indexing callback tests (no PS5 required)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import ghost_tk
ghost_tk.install()

from tools_progress import TaskProgress
import ue_quick as Q
from ue_world import Proj, tgt, world


class ProgressTests(unittest.TestCase):
    def test_widget_shows_real_percent_and_finishes(self):
        widget = TaskProgress(None)
        widget.start("Connecting")
        self.assertEqual(widget.message.get(), "Connecting")
        widget.update(2500, 10000, "Indexing")
        self.assertEqual(widget.value.get(), 25)
        self.assertIn("2,500/10,000 (25%)", widget.message.get())
        widget.finish("Scan complete")
        self.assertEqual(widget.value.get(), 100)
        self.assertEqual(widget.message.get(), "Scan complete")

    def test_widget_can_report_failure(self):
        widget = TaskProgress(None)
        widget.start("Scanning")
        widget.fail("Scan failed: disconnected")
        self.assertIn("disconnected", widget.message.get())
        self.assertEqual(widget.value.get(), 0)

    def test_find_instances_reports_actual_index_completion(self):
        _mem, _ref, sdk, client = world()
        live = Q.connect_live(client, Proj(sdk), log=lambda message: None)
        reports = []
        hits = Q.find_instances(
            live, tgt(sdk, "Health"), progress=lambda done, total: reports.append((done, total))
        )
        self.assertTrue(hits)
        self.assertTrue(reports)
        self.assertEqual(reports[-1], (live.num_elements, live.num_elements))
        self.assertIsNotNone(live.index)


if __name__ == "__main__":
    unittest.main()
