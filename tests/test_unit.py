"""Unit tests to check basic expected behaviors."""

from ..src.gui.l10n import localize, unlocalize
from ..src.agora import Agora
from ..src.paradigm import CellIndex, NounParadigm
from ..src.agora import Speaker
from ..src.settings import SETTINGS

def test_always_pass():
    assert True

def test_default_NounParadigm():
    noun_para = NounParadigm()
    assert noun_para[0][0].bias_a == 0.5
    assert noun_para[CellIndex(0,0)].bias_a == 0.5
    assert noun_para[0][0].form_a == ''
    assert noun_para[CellIndex(0,0)].form_a == ''
    assert noun_para[0][0].form_b == ''
    assert noun_para[CellIndex(0,0)].form_b == ''
    assert noun_para[0][0].prominence == 1.0
    assert noun_para[CellIndex(0,0)].prominence == 1.0

def test_NounParadigm_assignment():
    noun_para = NounParadigm()
    noun_para[0][0].bias_a = 0.12345
    assert noun_para[0][0].bias_a == 0.12345
    assert noun_para[CellIndex(0,0)].bias_a == 0.12345

def test_simulation_harmonic():
    SETTINGS.sim_learning_model = SETTINGS.LearningModel.HARMONIC
    agora = Agora()
    noun_para_tomayto = NounParadigm(0.0, 'tomahto', 'tomayto')
    agora.add_speaker(Speaker(0, (-100, 0), noun_para_tomayto))
    noun_para_tomahto = NounParadigm(1.0, 'tomahto', 'tomayto')
    agora.add_speaker(Speaker(1, (+100, 0), noun_para_tomahto))
    assert 0.0 == agora.state.speakers[0].principal_bias()
    assert 1.0 == agora.state.speakers[1].principal_bias()
    agora.simulate()
    assert (0.0 == agora.state.speakers[0].principal_bias() and 0.5 == agora.state.speakers[1].principal_bias()) or \
           (0.5 == agora.state.speakers[0].principal_bias() and 1.0 == agora.state.speakers[1].principal_bias())
    assert 2 == agora.state.speakers[0].experience and 2 == agora.state.speakers[1].experience

def test_simulation_RW_vanilla():
    SETTINGS.sim_learning_model = SETTINGS.LearningModel.RW
    agora = Agora()
    noun_para_tomayto = NounParadigm(0.0, 'tomahto', 'tomayto')
    agora.add_speaker(Speaker(0, (-100, 0), noun_para_tomayto))
    noun_para_tomahto = NounParadigm(1.0, 'tomahto', 'tomayto')
    agora.add_speaker(Speaker(1, (+100, 0), noun_para_tomahto))
    assert 0.0 == agora.state.speakers[0].principal_bias()
    assert 1.0 == agora.state.speakers[1].principal_bias()
    agora.simulate()
    assert (0.0 == agora.state.speakers[0].principal_bias() == agora.state.speakers[1].principal_bias()) or \
           (1.0 == agora.state.speakers[0].principal_bias() == agora.state.speakers[1].principal_bias())
    assert 2 == agora.state.speakers[0].experience and 2 == agora.state.speakers[1].experience

def test_l10n_to_English():
    SETTINGS.gui_language = SETTINGS.GuiLanguage.ENG
    assert "Start" == localize("Start")
    assert "%d iterations" % 13 == localize("%d iterations") % 13
    assert "abracadabra" == localize("abracadabra")
    assert "Start" == unlocalize("Start")
    assert "%d iterations" % 13 == unlocalize("%d iterations") % 13
    assert "abracadabra" == unlocalize("abracadabra")

def test_l10n_to_Hungarian():
    SETTINGS.gui_language = SETTINGS.GuiLanguage.HUN
    assert "Csapassad neki!" == localize("Start")
    assert "%d iteráció" % 13 == localize("%d iterations") % 13
    assert "abracadabra" == localize("abracadabra")
    assert "Start" == unlocalize(localize("Start"))
    assert "%d iterations" % 13 == unlocalize(localize("%d iterations")) % 13
    assert "abracadabra" == unlocalize(localize("abracadabra"))
