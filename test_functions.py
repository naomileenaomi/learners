import main


def test_parse_input():
    assert (
        main.parse_input("la#KEY-e	+definite	+atomic,+minimal") 
        == 
        ("la#KEY-e", [("+definite",), ("+atomic", "+minimal")])
    )


def test_find_roots():
    assert main.find_roots("la#KEY-e") == ["KEY"]
    assert main.find_roots("le#KEY-i") == ["KEY"]
    assert main.find_roots("il#BOOK-o#BIG-e") == ["BOOK", "BIG"]