"""Regression test for translated right-click menus created after language switches."""
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import ghost_tk
ghost_tk.install()

import tools_common as common
import tools_i18n as i18n


class FakeTree:
    def __init__(self):
        self._selection = ()
        self.popup = None

    def bind(self, name, handler):
        if name == "<Button-3>":
            self.popup = handler

    def identify_row(self, y):
        return "0"

    def selection(self):
        return self._selection

    def selection_set(self, iid):
        self._selection = (iid,)


class MenuSpy:
    instances = []

    def __init__(self, *args, **kwargs):
        self.items = []
        self.instances.append(self)

    def add_command(self, label, command):
        self.items.append((label, command))

    def add_separator(self):
        self.items.append((None, None))

    def tk_popup(self, x, y):
        pass

    def grab_release(self):
        pass


class ContextMenuTranslationTests(unittest.TestCase):
    def test_right_click_translates_actions_and_properties_after_language_switch(self):
        tree, fired = FakeTree(), []
        actions = [
            ("Wert ändern…", lambda: fired.append("edit")),
            ("❄ Einfrieren", lambda: fired.append("freeze")),
            ("Auftauen", lambda: fired.append("unfreeze")),
            ("Alle auftauen", lambda: fired.append("all")),
            (None, None),
            ("Im Speicher zeigen", lambda: fired.append("memory")),
            ("Schreiber finden", lambda: fired.append("writer")),
        ]
        original_menu = common.tk.Menu
        try:
            common.tk.Menu = MenuSpy
            common._attach_context_menu(tree, [("value", "WERT")], actions, lambda iid: [("a", "b")])
            event = types.SimpleNamespace(x=10, y=12, x_root=100, y_root=120)

            i18n.set_lang("en")
            tree.popup(event)
            english = MenuSpy.instances[-1]
            self.assertEqual([name for name, _ in english.items if name], [
                "Change value…", "❄ Freeze", "Unfreeze", "Unfreeze all",
                "Show in memory", "Find writers", "Properties...",
            ])
            english.items[0][1]()
            self.assertEqual(fired, ["edit"])

            i18n.set_lang("de")
            tree.popup(event)
            german = MenuSpy.instances[-1]
            self.assertEqual([name for name, _ in german.items if name],
                             [label for label, _ in actions if label] + ["Eigenschaften..."])
        finally:
            i18n.set_lang("de")
            common.tk.Menu = original_menu


if __name__ == "__main__":
    unittest.main()
