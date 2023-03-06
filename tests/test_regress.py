"""Regression tests to cover former bugs."""

from sys import modules

from kivy.graphics.vertex_instructions import Line

from ..src.gui.access_widgets import *

class MockObject(dict):
    def __init__(self):
        self.__dict__ = self  # this makes attribute syntax work on a dict, i.e. dict.x == dict['x']

# mock get_button_layout() to isolate the AgoraWidget from interactions with the button panel
_mock_button_layout = MockObject()
_mock_button_layout.ids = MockObject()
_mock_button_layout.ids.iteration_counter = MockObject()
_mock_button_layout.ids.iteration_counter.text = ''
def _mock_get_button_layout():
    return _mock_button_layout
modules['morphohistory.src.gui.access_widgets'].get_button_layout = _mock_get_button_layout

from ..src.gui.sim import AgoraWidget
from ..src.demos import Rainbow9x9

def test_arrow_and_iteration_counter_after_reset():
    agora = AgoraWidget()
    agora.load_demo_agora(Rainbow9x9)
    agora.save_starting_state()
    for _ in range(3):
        agora.simulate()
    assert any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 3 == agora.state.sim_iteration_total
    assert '3' == _mock_get_button_layout().ids.iteration_counter.text[0]
    agora.reset()
    assert not any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 0 == agora.state.sim_iteration_total
    assert '0' == _mock_get_button_layout().ids.iteration_counter.text[0]

def test_arrow_and_iteration_counter_after_quick_reset():
    agora = AgoraWidget()
    agora.load_demo_agora(Rainbow9x9)
    agora.save_starting_state()
    for _ in range(3):
        agora.simulate()
    assert any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 3 == agora.state.sim_iteration_total
    assert '3' == _mock_get_button_layout().ids.iteration_counter.text[0]
    agora.quick_reset()
    assert not any([isinstance(instruction, Line) for instruction in agora.canvas.children])
    assert 0 == agora.state.sim_iteration_total
    assert '0' == _mock_get_button_layout().ids.iteration_counter.text[0]
