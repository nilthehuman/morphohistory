"""Little notes to pop up in the middle of the screen when the user saves or discards their data."""

from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.uix.label import Label

from .l10n import localize

class ConfirmedLabel(Label):
    """Common base class to ApplyConfirmedLabel and DiscardConfirmedLabel for convenience."""
    alpha = NumericProperty(1)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        Animation(alpha=0, d=1.5, t='in_quad').start(self)
        self.bind(alpha=self.on_fade)
        self.text = localize(self.text)  # need to do this by hand which is a bit unfortunate

    def on_fade(self, _instance, value: float) -> None:
        if 0 == value:
            self.parent.remove_widget(self)

class ApplyConfirmedLabel(ConfirmedLabel):
    """A small green note in the center of the screen to confirm applying the user's settings."""
    pass

class DiscardConfirmedLabel(ConfirmedLabel):
    """A small red note in the center of the screen to confirm discarding the user's settings."""
    pass
