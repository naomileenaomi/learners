import pytest
import main


@pytest.fixture
def semantic_terminal():
    semantic_terminal = main.SemanticTerminal(
        label="label",
        values={"1", "2", "3"},
        selectional=["label2"],
        selection_strength=True,
    )
    yield semantic_terminal

@pytest.fixture
def nominalizer_terminal1():
    nominalizer_terminal = main.NominalizerTerminal(
        values={"3", "2", "1"},
        selectional=["label1"],
        selection_strength=True,
    )
    yield nominalizer_terminal


@pytest.fixture
def nominalizer_terminal2():
    nominalizer_terminal = main.NominalizerTerminal(
        values={"3", "2", "1"},
        selectional=["label2"],
        selection_strength=True,
    )
    yield nominalizer_terminal


@pytest.fixture
def nominalizer_terminal3():
    nominalizer_terminal = main.NominalizerTerminal(
        values={"3", "2", "1"},
        selectional=["label3"],
        selection_strength=True,
    )
    yield nominalizer_terminal