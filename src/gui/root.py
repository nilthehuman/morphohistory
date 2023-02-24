"""The top level root widget (main window) of the application's GUI."""

from kivy.uix.tabbedpanel import TabbedPanel

class TopTabbedPanel(TabbedPanel):
    """The application's root widget, enables switching between tabs."""

    def switch_to_next(self):
        """Switch to the tab immediately to the right of the currently active tab,
        cycling back to the leftmost tab on overflow."""
        tab_index = self.tab_list.index(self.current_tab)
        tab_index = (tab_index - 1) % len(self.tab_list)
        self.switch_to(self.tab_list[tab_index])

    def switch_to_prev(self):
        """Switch to the tab immediately to the left of the currently active tab,
        cycling back to the rightmost tab on underflow."""
        tab_index = self.tab_list.index(self.current_tab)
        tab_index = (tab_index + 1) % len(self.tab_list)
        self.switch_to(self.tab_list[tab_index])
