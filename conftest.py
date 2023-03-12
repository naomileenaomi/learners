import pytest
import main
import copy


@pytest.fixture
def adjectivalizer_terminal():
    adjectivalizer_terminal = main.AdjectivalizerTerminal()
    yield adjectivalizer_terminal


@pytest.fixture
def semantic_terminal1():
    semantic_terminal = main.SemanticTerminal(
        label="label",
        values={"1", "2", "3"},
        selectional=["label2"],
        selection_strength=True,
    )
    yield semantic_terminal

@pytest.fixture
def semantic_terminal2():
    semantic_terminal = main.SemanticTerminal(
        label="label",
        values={"1", "2", "3"},
        selectional=["label2"],
        selection_strength=True,
    )
    yield semantic_terminal

@pytest.fixture
def semantic_terminal3():
    semantic_terminal = main.SemanticTerminal(
        label="label",
        values={"4", "5", "6"},
        selectional=["label2"],
        selection_strength=True,
    )
    yield semantic_terminal

@pytest.fixture
def nominalizer_terminal1():
    nominalizer_terminal = main.NominalizerTerminal(
        values={"3", "2", "1"},
        selectional=["label1"],
    )
    yield nominalizer_terminal


@pytest.fixture
def nominalizer_terminal2():
    nominalizer_terminal = main.NominalizerTerminal(
        values={"3", "2", "1"},
        selectional=["label2"],
    )
    yield nominalizer_terminal


@pytest.fixture
def nominalizer_terminal3():
    nominalizer_terminal = main.NominalizerTerminal(
        values={"3", "2", "1"},
        selectional=["label3"],
    )
    yield nominalizer_terminal


@pytest.fixture
def nominalizer_terminal_input1():
    nominalizer_terminal = main.NominalizerTerminal(
        values=set(),
        selectional=["KEY"],
    )
    yield nominalizer_terminal

@pytest.fixture
def root_input1():
    root = main.Root("KEY")
    yield root

@pytest.fixture
def semantic_terminal_input_1_1():
    semantic_terminal = main.SemanticTerminal(
        label="(definite)",
        values={"+definite"},
        selectional=["(atomic, minimal)"],
        selection_strength=False,
    )
    yield semantic_terminal

@pytest.fixture
def semantic_terminal_input_1_2():
    semantic_terminal = main.SemanticTerminal(
        label="(atomic, minimal)",
        values={"+atomic", "+minimal"},
        selectional=["nominalizer"],
        selection_strength=True,
    )
    yield semantic_terminal

@pytest.fixture
def terminal_chain_input_1_1(nominalizer_terminal_input1, root_input1):
    terminal_chain = main.TerminalChain(
        selector=nominalizer_terminal_input1,
        complement=root_input1,
        affix="suffixing",
    )

    return terminal_chain

@pytest.fixture
def terminal_chain_input_1_2(semantic_terminal_input_1_2, terminal_chain_input_1_1):
    terminal_chain = main.TerminalChain(
        selector=semantic_terminal_input_1_2,
        complement=terminal_chain_input_1_1,
        affix="suffixing",
    )

    return terminal_chain

@pytest.fixture
def terminal_chain_input_1_3(semantic_terminal_input_1_1, terminal_chain_input_1_2):
    terminal_chain = main.TerminalChain(
        selector=semantic_terminal_input_1_1,
        complement=terminal_chain_input_1_2,
        affix="suffixing",
    )

    return terminal_chain

@pytest.fixture
def terminal_chain_toy_1(terminal_chain_input_1_1):
    terminal_chain = copy.deepcopy(terminal_chain_input_1_1)
    terminal_chain.linear = (1, 2, 3, 4, 5)

    return terminal_chain

@pytest.fixture
def vocabulary_item_toy_1():
    return main.VocabularyItem(
        pronunciation="a",
        label="a",
        values={1, 2, 3},
        diacritic="a_1",
        triggers={1, 2, 3}
    )

@pytest.fixture
def vocabulary_item_toy_2():
    return main.VocabularyItem(
        pronunciation="a",
        label="a",
        values={1, 2, 3},
        diacritic="a_2",
        triggers={1, 2, 3}
    )

@pytest.fixture
def vocabulary_item_toy_3():
    return main.VocabularyItem(
        pronunciation="b",
        label="b",
        values={1, 2, 3},
        diacritic="b_1",
        triggers={1, 2, 3}
    )

@pytest.fixture
def vocabulary_items_toy(vocabulary_item_toy_1, vocabulary_item_toy_2, vocabulary_item_toy_3):
    return [
        vocabulary_item_toy_1, vocabulary_item_toy_2, vocabulary_item_toy_3
    ]
