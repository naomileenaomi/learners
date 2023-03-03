import main


def test_parse_input():
    assert (
        main.parse_input("la#KEY-e	+definite	+atomic,+minimal") 
        == 
        ("la#KEY-e", [{"+definite",}, {"+atomic", "+minimal"}])
    )


def test_find_roots():
    assert main.find_roots("la#KEY-e") == ["KEY"]
    assert main.find_roots("le#KEY-i") == ["KEY"]
    assert main.find_roots("il#BOOK-o#BIG-e") == ["BOOK", "BIG"]


def test_select_nominalizer(nominalizer_terminal1, nominalizer_terminal2):
    nominalizer_terminal1.weight = 0
    nominalizer_terminal2.weight = 0

    assert nominalizer_terminal1.selectional != nominalizer_terminal2.selectional

    assert main.select_nominalizer(
        root=nominalizer_terminal1.selectional[0],
        existing_nominalizers=[nominalizer_terminal1, nominalizer_terminal2]
    ) == nominalizer_terminal1
