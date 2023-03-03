import main
import pytest

def test_permuted_value_equality(semantic_terminal, nominalizer_terminal1):
    assert semantic_terminal.values == nominalizer_terminal1.values
