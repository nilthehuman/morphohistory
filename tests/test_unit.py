"""Unit tests to check basic expected behaviors."""

from ..src.gui.l10n import localize, unlocalize
from ..src.paradigm import *
from ..src.settings import SETTINGS

def test_always_pass():
    assert True

def test_default_NounParadigm():
    noun_para = NounParadigm()
    assert noun_para[0][0].bias_a == 0.5
    assert noun_para[0][0].form_a == ''
    assert noun_para[0][0].form_b == ''
    assert noun_para[0][0].prominence == 1.0

def test_NounParadigm_assignment():
    noun_para = NounParadigm()
    noun_para[0][0].bias_a = 0.12345
    assert noun_para[0][0].bias_a == 0.12345

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
