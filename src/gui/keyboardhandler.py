"""The class that listens for and processes single keypresses tied to basic commands for the application like
run simulation, stop simulation, fast forward etc. This class is probably going to be retired at some point."""

from logging import info

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

from .access_widgets import get_root, get_agora


# Adapted from kivy.org/doc/stable/api-kivy.core.window.html
class KeyboardHandler(Widget):
    """Handles hotkeys to the application's basic features."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(lambda: True, self)
        self.keyboard.bind(on_key_down=self.on_keypressed)

    def on_keypressed(self, _keyboard, keycode: tuple[int, str], _text, modifiers: list[str]) -> bool:
        if get_root().current_tab == get_root().tab_list[-1]:
            # we're on the main tab panel
            if keycode[1] == 's':
                get_agora().start_stop_sim()
                return True
            if keycode[1] == 'f':
                get_agora().start_stop_sim(fastforward=True)
                return True
            if keycode[1] == 'r':
                get_agora().stop_sim()
                get_agora().quick_reset()
                return True
        if keycode[1] == 'q':
            info("KeyboardHandler: Exiting app...")
            App.get_running_app().stop()
            return True
        if keycode[1] == 'tab' and 'ctrl' in modifiers:
            if 'shift' in modifiers:
                get_root().switch_to_prev()
            else:
                get_root().switch_to_next()
            return True
        return False
