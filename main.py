# define constants
from ast import parse
import inspect
import re

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
            values=("+definite",),
            selectional=("atomic", "minimal"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("definite",),
            values=("+definite",),
            selectional=("atomic", "minimal"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("definite",),
            values=("-definite",),
            selectional=("atomic", "minimal"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("definite",),
            values=("-definite",),
            selectional=("atomic", "minimal"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values=("+atomic", "+minimal"),
            selectional=("nominalizer"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values=("+atomic", "+minimal"),
            selectional=("nominalizer"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values=("-atomic", "+minimal"),
            selectional=("nominalizer"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values=("-atomic", "+minimal"),
            selectional=("nominalizer"),
            selection_strength=False,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values=("-atomic", "-minimal"),
            selectional=("nominalizer"),
            selection_strength=True,
        ),
        SemanticTerminal(
            label=("atomic", "minimal"),
            values=("-atomic", "-minimal"),
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
        values = [tuple(value_string.split(",")) for value_string in value_strings]

        return input_string, values


def find_roots(input_string):
    words = re.split("[#-]", input_string)
    return [word for word in words if word.isupper()]


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
            print(roots)
            print(values)


run()