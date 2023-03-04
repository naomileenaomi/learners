# define constants
from ast import parse
import inspect
import re
import random

INITIAL_TERMINAL_WEIGHT = 10.0
UPDDATE_TERMINAL_WEIGHT = 0.2
ALREADY_SELECTS_BONUS = 0.75

INITIAL_SPROUTING_RULE_WEIGHT = 1
UPDATE_SPROUTING_RULE_WEIGHT = .1


class SemanticTerminal:
    def __init__(self, label, values, selectional, selection_strength):
        self.label = label
        self.values = values
        self.selectional = selectional
        self.selection_strength = selection_strength
        self.weight = INITIAL_TERMINAL_WEIGHT
        self.linear = self

    def __str__(self):
        return f"SemanticTerminal: {self.label}"
    
    def big_string(self):
        return inspect.cleandoc(
            f"""
            Semantic Terminal:
                label: {self.label}
                values: {self.values}
                selectional: {self.selectional}
                selection_strength: {self.selection_strength}
                weight: {self.weight}
                linear: {self.linear}
            """
        )


class NominalizerTerminal:
    def __init__(self, values, selectional):
        self.label = "nominalizer"
        self.values = values
        self.selectional = selectional
        self.selection_strength = True
        self.weight = INITIAL_TERMINAL_WEIGHT
        self.linear = self

    def __str__(self):
        return f"NominalizerTerminal: {self.label}"
    
    def big_string(self):
        return inspect.cleandoc(
            f"""
            NominalizerTerminal:
                label: {self.label}
                values: {self.values}
                selectional: {self.selectional}
                selection_strength: {self.selection_strength}
                weight: {self.weight}
                linear: {self.linear}
            """
        )

    def __eq__(self, other):
        return (
                self.label == other.label 
            and self.values == other.values
            and self.selectional == other.selectional
            and self.selection_strength == other.selection_strength
            and self.weight == other.weight
        )


class Root:
    def __init__(self, label):
        self.label = label
        self.values = ()
        self.linear = self
    
    def __str__(self):
        return f"Root: {self.label}"

    def big_string(self):
        return inspect.cleandoc(
            f"""
            Root:
                label: {self.label}
                values: {self.values}
                linear: {self.linear}
            """
        )


def create_semantic_terminals(learner_version):
    core_terminals = (
        SemanticTerminal(
            label=("definite",),
            values={"+definite",},
            selectional=("atomic", "minimal"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("definite",),
            values={"+definite",},
            selectional=("atomic", "minimal"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("definite",),
            values={"-definite",},
            selectional=("atomic", "minimal"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("definite",),
            values={"-definite",},
            selectional=("atomic", "minimal"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values={"+atomic", "+minimal"},
            selectional=("nominalizer"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values={"+atomic", "+minimal"},
            selectional=("nominalizer"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values={"-atomic", "+minimal"},
            selectional=("nominalizer"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values={"-atomic", "+minimal"},
            selectional=("nominalizer"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values={"-atomic", "-minimal"},
            selectional=("nominalizer"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values={"-atomic", "-minimal"},
            selectional=("nominalizer"),
            selection_strength=False,
        ),  
    )

    additional_terminals = {
        1: (),
        2: (),
        3: (),
    }

    return core_terminals + additional_terminals[learner_version]


def parse_input(input_line):
        tokens = input_line.split("\t")
        input_string = tokens[0]
        value_strings = tokens[1:]
        values = [set(value_string.split(",")) for value_string in value_strings]

        return input_string, values


def find_roots(input_string):
    exponents = re.split("[#-]", input_string)
    return [exponent for exponent in exponents if exponent.isupper()]


def create_nominalizer(root, values, existing_nominalizers):

    for nominalizer in existing_nominalizers:
        if nominalizer.values == values:
            if root in nominalizer.selectional:
                return existing_nominalizers
            else:
                nominalizer.selectional.append(root)
                return existing_nominalizers
    
    existing_nominalizers.append(
        NominalizerTerminal(
            values = values,
            selectional = [root],
        )
    )

    return existing_nominalizers


def select_nominalizer(root, existing_nominalizers):
    weights = [
        nominalizer.weight + ALREADY_SELECTS_BONUS
        if root in nominalizer.selectional 
        else nominalizer.weight
        for nominalizer 
        in existing_nominalizers
    ]

    return random.choices(population=existing_nominalizers, weights=weights)[0]


def select_semantic_terminals(input_values, semantic_terminals):
    selected_terminals = []
    
    for values in input_values:
        choices = [
            terminal 
            for terminal 
            in semantic_terminals
            if terminal.values == values
        ]

        assert len(choices) == 2

        weights = [
            terminal.weight
            for terminal
            in choices
        ]

        selected_terminals.append(random.choices(population=choices, weights=weights)[0])

    assert len(selected_terminals) == len(input_values)

    return selected_terminals


def run(
    input_file_path="./data/input/italian-class-iii-plus-adjectives.txt",
    root_file_path="./data/roots/italian-class-iii-plus-adjectives-ROOTS-list.txt",
    learner_version=1,
    verbosity_level = 2,
):


    # initialize state

    with open(root_file_path,'r') as root_file:
        roots = [Root(label=label) for label in root_file.read().splitlines()]

    if verbosity_level == 3:
        for root in roots:
            print(root.big_string())

    semantic_terminals = create_semantic_terminals(learner_version=learner_version)

    if verbosity_level == 3:
        for ST in semantic_terminals:
            print(ST.big_string())


    nominalizer_terminals = []
    sprouting_rules = []
    vocabulary_items = []

    # process input

    with open(input_file_path,'r') as learningDataFile:
        learningDataString = learningDataFile.read().splitlines()


    for line in learningDataString:
        input_string, values = parse_input(line)
        roots = find_roots(input_string)
        
        if verbosity_level >= 2:
            print(f"roots: {roots}")
            print(f"values: {values}")

        if len(nominalizer_terminals) == 0:
            create_nominalizer(
                roots[0],
                values={},
                existing_nominalizers=nominalizer_terminals,
            )
        
        selected_nominalizer_terminal = select_nominalizer(roots[0], existing_nominalizers=nominalizer_terminals)
        
        if verbosity_level >= 2:
            print(f"Nominalizer selected: {selected_nominalizer_terminal}")

        selected_semantic_terminals = select_semantic_terminals(input_values=values, semantic_terminals=semantic_terminals)

        if verbosity_level >= 2:
            print(f"SemanticTerminals selected: {selected_semantic_terminals}")

run()