"""Unit tests to check basic expected behaviors."""

from ..src.paradigm import *

def test_always_pass():
    assert True

def test_default_NounParadigm():
    noun_para = NounParadigm()
    assert noun_para[0][0].weight_a == 0.5
    assert noun_para[0][0].form_a == ''
    assert noun_para[0][0].form_b == ''
    assert noun_para[0][0].importance == 1.0

def test_NounParadigm_assignment():
    noun_para = NounParadigm()
    noun_para[0][0].weight_a = 0.12345
    assert noun_para[0][0].weight_a == 0.12345
