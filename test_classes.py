import main
import pytest

def test_permuted_value_equality(semantic_terminal1, nominalizer_terminal1):
    assert semantic_terminal1.values == nominalizer_terminal1.values
