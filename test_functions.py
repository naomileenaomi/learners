import main
import copy
from collections import Counter


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
        root=main.Root(next(iter(nominalizer_terminal1.selectional))),
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
    adjectivalizer_terminal.selectional = {"a", "b", "c"}
    
    new_adjectivalizer = copy.deepcopy(adjectivalizer_terminal)


    assert main.select_adjectivalizer_terminals(main.Root("a"), new_adjectivalizer) == adjectivalizer_terminal
    assert main.select_adjectivalizer_terminals(main.Root("b"), new_adjectivalizer) == adjectivalizer_terminal
    assert new_adjectivalizer.selectional == {"a", "b", "c"}


    assert main.select_adjectivalizer_terminals(main.Root("d"), new_adjectivalizer) != adjectivalizer_terminal
    assert new_adjectivalizer.selectional == {"a", "b", "c", "d"}

def test_derive_terminal_chain(
        nominalizer_terminal_input1,
        semantic_terminal_input_1_1,
        semantic_terminal_input_1_2,
        adjectivalizer_terminal
):
    numeration = {
        "roots": [main.Root("KEY")],
        "nominalizer": nominalizer_terminal_input1,
        "semantic_0": semantic_terminal_input_1_1,
        "semantic_1": semantic_terminal_input_1_2
    }

    terminal_chain = main.derive_terminal_chain(numeration=numeration, affix="suffixing")

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
    
    numeration = {
        "roots": [main.Root("KEY"),  main.Root("BIG")],
        "nominalizer": nominalizer_terminal_input1,
        "adjectivalizer": adjectivalizer_terminal,
        "semantic_0": semantic_terminal_input_1_1,
        "semantic_1": semantic_terminal_input_1_2
    }

    terminal_chain = main.derive_terminal_chain(numeration=numeration, affix="suffixing")

    assert terminal_chain == main.TerminalChain(
            semantic_terminal_input_1_1,
            main.TerminalChain(main.TerminalChain(semantic_terminal_input_1_2,
                main.TerminalChain(
                    nominalizer_terminal_input1,
                    main.Root("KEY"),
                    affix="suffixing",
                ),
                affix="suffixing"
            ), main.TerminalChain(
                    adjectivalizer_terminal,
                    main.Root("BIG"),
                    affix="suffixing",
                ),
            affix="suffixing"
        ), affix="suffixing"
    )

def test_slice_terminal_chain(
    terminal_chain_input_1_1,
    terminal_chain_input_1_2, 
    terminal_chain_input_1_3,
):
    assert (
        main.slice_terminal_chain(terminal_chain_input_1_1) 
        == 
        [terminal_chain_input_1_1.linear]
    )

    assert (
        main.slice_terminal_chain(terminal_chain_input_1_2) 
        == 
        [terminal_chain_input_1_2.linear]
    )

    assert (
        main.slice_terminal_chain(terminal_chain_input_1_3) 
        == 
        [terminal_chain_input_1_3.linear[0:1], terminal_chain_input_1_3.linear[2:]]
    )

def test_all_combinations():
    assert main.all_combinations({1, 2}) == [
        set(),
        {1}, {2},
        {1, 2},
    ]

    assert main.all_combinations({1, 2, 3}) == [
        set(),
        {1}, {2}, {3},
        {1, 2}, {1, 3}, {2, 3},
        {1, 2, 3},
    ]

def test_insert_into_linear(terminal_chain_toy_1):
    
    terminal_chain = main.insert_into_linear(
        terminal_chain=terminal_chain_toy_1,
        terminal=3,
        affix="suffixing",
        new_linear=(3.3, 3.6)
    )

    assert terminal_chain.linear == (1, 2, 3, 3.3, 3.6, 4, 5)

    terminal_chain = main.insert_into_linear(
        terminal_chain=terminal_chain_toy_1,
        terminal=3,
        affix="prefixing",
        new_linear=(2.3, 2.6)
    )

    assert terminal_chain.linear == (1, 2, 2.3, 2.6, 3, 4, 5)

def test_get_diacritic_number(vocabulary_items_toy):
    assert main.get_diacritic_number(pronunciation="a", vocabulary_items=vocabulary_items_toy) == 3
    assert main.get_diacritic_number(pronunciation="b", vocabulary_items=vocabulary_items_toy) == 2
    assert main.get_diacritic_number(pronunciation="c", vocabulary_items=vocabulary_items_toy) == 1

def test_create_vi(vocabulary_items_toy):
    # TODO turn this back on maybe
    # assert main.create_vi(
    #     pronunciation="null",
    #     label="doesn't matter",
    #     values=set(),
    #     triggers={1, 2, 3},
    #     vocabulary_items=vocabulary_items_toy
    # ) == (False, None, vocabulary_items_toy)

    # assert main.create_vi(
    #     pronunciation=vocabulary_items_toy[0].pronunciation,
    #     label=vocabulary_items_toy[0].label,
    #     values=vocabulary_items_toy[0].values,
    #     triggers=vocabulary_items_toy[0].triggers,
    #     vocabulary_items=vocabulary_items_toy
    # ) == (False, vocabulary_items_toy[0], vocabulary_items_toy)

    # new_vi = main.VocabularyItem(
    #     pronunciation="d",
    #     label="d",
    #     values={1, 2, 3},
    #     diacritic="d_1",
    #     triggers={1, 2, 3}
    # )

    # assert main.create_vi(
    #     pronunciation="d",
    #     label="d",
    #     values={1, 2, 3},
    #     triggers={1, 2, 3},
    #     vocabulary_items=vocabulary_items_toy
    # ) == (True, new_vi, vocabulary_items_toy + [new_vi])

    pass

def test_insert_vi(terminal_chain_input_2, vocabulary_items_no_values, vocabulary_items_super_matches):
    # full_pronunciation, vis_used = main.insert_vi(
    #     terminal_chain=terminal_chain_input_2,
    #     vocabulary_items=vocabulary_items_no_values
    # )
    
    # assert full_pronunciation == "SHIP"
    # assert sorted([vi.diacritic for vi in vis_used]) == sorted([vi.diacritic for vi in vocabulary_items_no_values])

    # full_pronunciation, vis_used = main.insert_vi(
    #     terminal_chain=terminal_chain_input_2,
    #     vocabulary_items=vocabulary_items_super_matches
    # )

    # assert full_pronunciation == "SHIP"
    # assert sorted([vi.diacritic for vi in vis_used]) == sorted(["null_1", "SHIP_1"])

    pass


def test_prep_slices(root_input1, nominalizer_terminal_input1, semantic_terminal_input_1_1, semantic_terminal_input_1_2):
    morphs = ["la"]

    terminals = [semantic_terminal_input_1_1]

    prepped_morphs, prepped_terminals = main.prep_slices(morphs, terminals, affix="suffixing")

    assert prepped_terminals == terminals
    assert prepped_morphs == morphs
    
    
    morphs = ["KEY", "e"]

    terminals = [root_input1, nominalizer_terminal_input1, semantic_terminal_input_1_2]

    prepped_morphs, prepped_terminals = main.prep_slices(morphs, terminals, affix="suffixing")

    assert prepped_terminals == terminals
    assert prepped_morphs == ["KEY", "null", "e"]


def test_insert_agr(semantic_terminal1, nominalizer_terminal1, adjectivalizer_terminal):
    assert main.insert_agr([semantic_terminal1]) == [semantic_terminal1]
    assert main.insert_agr([nominalizer_terminal1]) == [nominalizer_terminal1]
    assert main.insert_agr([]) == []

    assert main.insert_agr([adjectivalizer_terminal]) == [adjectivalizer_terminal, main.AgrTerminal(values=adjectivalizer_terminal.values)]

    assert main.insert_agr([semantic_terminal1, adjectivalizer_terminal]) == [
        semantic_terminal1, adjectivalizer_terminal, main.AgrTerminal(values=adjectivalizer_terminal.values)
    ]
    assert main.insert_agr([adjectivalizer_terminal, nominalizer_terminal1]) == [
        adjectivalizer_terminal, main.AgrTerminal(values=adjectivalizer_terminal.values), nominalizer_terminal1
    ]

    assert main.insert_agr([semantic_terminal1, adjectivalizer_terminal, nominalizer_terminal1]) == [
        semantic_terminal1, adjectivalizer_terminal, main.AgrTerminal(values=adjectivalizer_terminal.values), nominalizer_terminal1
    ]
