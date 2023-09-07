"""Regression tests to cover former bugs."""

import pytest
from importlib import reload
from sys import modules

from kivy.graphics.vertex_instructions import Line

from ..src.gui.access_widgets import *
from ..src.gui.sim import AgoraWidget
from ..src.settings import SETTINGS


_REAL_GET_BUTTON_LAYOUT = modules['morphohistory.src.gui.access_widgets'].get_button_layout

@pytest.fixture
def mock_setup():
    class MockObject(dict):
        def __init__(self):
            # this makes attribute syntax work on a dict, i.e. dict.x == dict['x']
            self.__dict__ = self

    # mock get_button_layout() to isolate the AgoraWidget from interactions with the button panel
    _mock_button_layout = MockObject()
    _mock_button_layout.ids = MockObject()
    _mock_button_layout.ids.iteration_counter = MockObject()
    _mock_button_layout.ids.iteration_counter.text = ''
    # I have no idea what I'm doing here really
    global get_button_layout
    def get_button_layout():
        return _mock_button_layout
    modules['morphohistory.src.gui.access_widgets'].get_button_layout = lambda: _mock_button_layout
    reload(modules['morphohistory.src.gui.sim'])
    # setup ends here
    yield
    # teardown starts here
    # restore true implementation of get_button_layout()
    modules['morphohistory.src.gui.access_widgets'].get_button_layout = _REAL_GET_BUTTON_LAYOUT
    reload(modules['morphohistory.src.gui.sim'])


def test_arrow_and_iteration_counter_after_reset(mock_setup):
    agora = AgoraWidget()
    agora.load_demo_agora(SETTINGS.DemoAgora.RAINBOW_9X9)
    agora.save_starting_state()
    for _ in range(3):
        agora.simulate()
    assert any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 3 == agora.state.sim_iteration_total
    assert '3' == get_button_layout().ids.iteration_counter.text[0]
    agora.reset()
    assert not any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 0 == agora.state.sim_iteration_total
    assert '0' == get_button_layout().ids.iteration_counter.text[0]

def test_arrow_and_iteration_counter_after_quick_reset(mock_setup):
    agora = AgoraWidget()
    agora.load_demo_agora(SETTINGS.DemoAgora.RAINBOW_9X9)
    agora.save_starting_state()
    for _ in range(3):
        agora.simulate()
    assert any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 3 == agora.state.sim_iteration_total
    assert '3' == get_button_layout().ids.iteration_counter.text[0]
    agora.quick_reset()
    assert not any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 0 == agora.state.sim_iteration_total
    assert '0' == get_button_layout().ids.iteration_counter.text[0]
