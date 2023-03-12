from conftest import root_input1, semantic_terminal_input_1_2
import main
import copy

def test_permuted_value_equality(semantic_terminal1, nominalizer_terminal1):
    assert semantic_terminal1.values == nominalizer_terminal1.values

def test_TerminalChain_constructor(
      nominalizer_terminal_input1
    , semantic_terminal_input_1_1
    , semantic_terminal_input_1_2
    , root_input1
):
    terminal_chain = main.TerminalChain(nominalizer_terminal_input1, root_input1, "suffixing")

    old_nominalizer = copy.deepcopy(nominalizer_terminal_input1)

    assert terminal_chain.linear == (root_input1, "-", nominalizer_terminal_input1)
    assert terminal_chain.values == set()
    assert terminal_chain.linear[0].values == set()
    assert terminal_chain.linear[2].values == set()
    assert old_nominalizer == nominalizer_terminal_input1

    old_terminal_chain = copy.deepcopy(terminal_chain)

    terminal_chain2 = main.TerminalChain(semantic_terminal_input_1_2, terminal_chain, "suffixing")

    assert terminal_chain2.linear == (root_input1, "-", nominalizer_terminal_input1, "-", semantic_terminal_input_1_2)
    assert terminal_chain2.values == {"+atomic", "+minimal"}
    assert terminal_chain2.linear[0].values == set()
    assert terminal_chain2.linear[2].values == set()
    assert terminal_chain2.linear[4].values == {"+atomic", "+minimal"}
    assert old_terminal_chain == terminal_chain

    old_terminal_chain = copy.deepcopy(terminal_chain2)

    terminal_chain3 = main.TerminalChain(semantic_terminal_input_1_1, terminal_chain2, "suffixing")

    mutated_selector = copy.deepcopy(semantic_terminal_input_1_1)
    mutated_selector.values.update({"+atomic", "+minimal", "+definite"})

    assert terminal_chain3.linear == (mutated_selector, "#", root_input1, "-", nominalizer_terminal_input1, "-", semantic_terminal_input_1_2)
    assert terminal_chain3.values == {"+atomic", "+minimal", "+definite"}
    assert terminal_chain3.linear[0].values == {"+atomic", "+minimal", "+definite"}
    assert terminal_chain3.linear[2].values == set()
    assert terminal_chain3.linear[4].values == set()
    assert terminal_chain3.linear[6].values == {"+atomic", "+minimal"}
    assert old_terminal_chain == terminal_chain2
