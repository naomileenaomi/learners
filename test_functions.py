import main
import copy


def test_parse_input():
    assert (
        main.parse_input("la#KEY-e	+definite	+atomic,+minimal") 
        == 
        ("la#KEY-e", [{"+definite",}, {"+atomic", "+minimal"}])
    )


def test_find_roots():
    assert main.find_roots("la#KEY-e") == [main.Root("KEY")]
    assert main.find_roots("le#KEY-i") == [main.Root("KEY")]
    assert main.find_roots("il#BOOK-o#BIG-e") == [main.Root("BOOK"), main.Root("BIG")]


def test_select_nominalizer(nominalizer_terminal1, nominalizer_terminal2):
    nominalizer_terminal1.weight = 0
    nominalizer_terminal2.weight = 0

    assert nominalizer_terminal1.selectional != nominalizer_terminal2.selectional

    assert main.select_nominalizer(
        root=main.Root(nominalizer_terminal1.selectional[0]),
        existing_nominalizers=[nominalizer_terminal1, nominalizer_terminal2]
    ) == nominalizer_terminal1


def test_select_semantic(semantic_terminal1, semantic_terminal2, semantic_terminal3):
    semantic_terminal1.weight = 0
    semantic_terminal2.weight = 1
    semantic_terminal3.weight = 100

    values = {"1", "2", "3"}

    assert semantic_terminal1.values == values
    assert semantic_terminal2.values == values
    assert semantic_terminal3.values != values


    assert main.select_semantic_terminals(
        input_values=[values],
        semantic_terminals=[semantic_terminal1, semantic_terminal2, semantic_terminal3]
    ) == [semantic_terminal2]


def test_select_adjectivalizer(adjectivalizer_terminal):
    adjectivalizer_terminal.selectional = ["a", "b", "c"]
    
    new_adjectivalizer = copy.deepcopy(adjectivalizer_terminal)


    assert main.select_adjectivalizer_terminals(main.Root("a"), new_adjectivalizer) == adjectivalizer_terminal
    assert main.select_adjectivalizer_terminals(main.Root("b"), new_adjectivalizer) == adjectivalizer_terminal
    assert new_adjectivalizer.selectional == ["a", "b", "c"]


    assert main.select_adjectivalizer_terminals(main.Root("d"), new_adjectivalizer) != adjectivalizer_terminal
    assert new_adjectivalizer.selectional == ["a", "b", "c", "d"]

def test_derive_terminal_chain(
        nominalizer_terminal_input1,
        semantic_terminal_input_1_1,
        semantic_terminal_input_1_2,
):
    enumeration = {
        "roots": [main.Root("KEY")],
        "nominalizer": nominalizer_terminal_input1,
        "semantic_0": semantic_terminal_input_1_1,
        "semantic_1": semantic_terminal_input_1_2
    }

    terminal_chain = main.derive_terminal_chain(enumeration=enumeration, affix="suffixing")

    assert terminal_chain == main.TerminalChain(
            semantic_terminal_input_1_1,
            main.TerminalChain(semantic_terminal_input_1_2,
                main.TerminalChain(
                    nominalizer_terminal_input1,
                    main.Root("KEY"),
                    affix="suffixing",
                ),
                affix="suffixing"
            ),
            affix="suffixing"
        )
