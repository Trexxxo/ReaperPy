"""Reusable, thread-safe-by-dispatch progress display for Tools tabs.

Call these methods on the Tk UI thread (workers must use win.ui).
Real fractions are shown only when the underlying operation reports work.
"""

import tkinter as tk
from tkinter import ttk

from tools_common import BG, FONT_LABEL, TEXT_DIM


class TaskProgress(tk.Frame):
    """Compact progress bar: indeterminate during setup, real percent during measurable work."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.message = tk.StringVar(value="")
        self.value = tk.DoubleVar(value=0)
        tk.Label(self, textvariable=self.message, bg=BG, fg=TEXT_DIM,
                 font=FONT_LABEL, anchor="w").pack(fill="x")
        self.bar = ttk.Progressbar(self, orient="horizontal", mode="determinate",
                                   maximum=100, variable=self.value,
                                   style="Horizontal.TProgressbar")
        self.bar.pack(fill="x", pady=(2, 0))

    def start(self, message):
        """Unknown duration, e.g. a network connection or a class lookup."""
        self.bar.stop()
        self.value.set(0)
        self.message.set(message)
        self.bar.configure(mode="indeterminate")
        self.bar.start(12)

    def activity(self, message):
        """Switch back to an unknown-duration operation between measured phases."""
        self.start(message)

    def update(self, done, total, stage):
        """Display completed units of real work, not an estimated percentage."""
        done, total = max(0, int(done)), max(1, int(total))
        done = min(done, total)
        self.bar.stop()
        self.bar.configure(mode="determinate")
        percent = 100 * done / total
        self.value.set(percent)
        self.message.set(f"{stage}: {done:,}/{total:,} ({percent:.0f}%)")

    def finish(self, message):
        self.bar.stop()
        self.bar.configure(mode="determinate")
        self.value.set(100)
        self.message.set(message)

    def fail(self, message):
        self.bar.stop()
        self.bar.configure(mode="determinate")
        self.message.set(message)
