import main

def test_permuted_value_equality(semantic_terminal1, nominalizer_terminal1):
    assert semantic_terminal1.values == nominalizer_terminal1.values


def test_TerminalChain_constructor(nominalizer_terminal_input1, root_input1):
    terminal_chain = main.TerminalChain(nominalizer_terminal_input1, root_input1, "suffixing")

    assert terminal_chain.linear == (root_input1, "-", nominalizer_terminal_input1)
    assert terminal_chain.values == set()
    assert terminal_chain.linear[0].values == set()
    assert terminal_chain.linear[2].values == set()
