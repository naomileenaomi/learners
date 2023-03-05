# define constants
from ast import parse
import inspect
import re
import random
import copy


INITIAL_TERMINAL_WEIGHT = 10.0
UPDATE_TERMINAL_WEIGHT = 0.0 #TODO fix this
ALREADY_SELECTS_BONUS = 0.75

INITIAL_SPROUTING_RULE_WEIGHT = 1
UPDATE_SPROUTING_RULE_WEIGHT = .1


def debug_print(verbosity_supplied, verbosity_required, message):
    if verbosity_supplied >= verbosity_required:
        print(message)


class SemanticTerminal:
    def __init__(self, label, values, selectional, selection_strength):
        self.label = label
        self.values = values
        self.selectional = selectional
        self.selection_strength = selection_strength
        self.weight = INITIAL_TERMINAL_WEIGHT
        self.linear = (self,)

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

    def __eq__(self, other):
        if type(self) != type(other): return False

        return (
                self.label == other.label 
            and self.values == other.values
            and self.selectional == other.selectional
            and self.selection_strength == other.selection_strength
            and self.weight == other.weight
        )


class NominalizerTerminal:
    def __init__(self, values, selectional):
        self.label = "nominalizer"
        self.values = values
        self.selectional = selectional
        self.selection_strength = True
        self.weight = INITIAL_TERMINAL_WEIGHT
        self.linear = (self,)

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
        if type(self) != type(other): return False
        
        return (
                self.label == other.label 
            and self.values == other.values
            and self.selectional == other.selectional
            and self.selection_strength == other.selection_strength
            and self.weight == other.weight
        )


class AdjectivalizerTerminal:
    def __init__(self):
        self.label = "adjectivalizer"
        self.values = set()
        self.selectional = []
        self.selection_strength = True
        self.weight = 999
        self.linear = (self,)

    def __str__(self):
        return f"AdjectivalizerTerminal: {self.label}"
    
    def big_string(self):
        return inspect.cleandoc(
            f"""
            NominalizerTerminal:
                label: {self.label}
                values: {self.values}
                selectional: {self.selectional}
                selection_strength: {self.selection_strength}
                linear: {self.linear}
            """
        )

    def __eq__(self, other):
        if type(self) != type(other): return False

        return (
                self.label == other.label 
            and self.values == other.values
            and self.selectional == other.selectional
            and self.selection_strength == other.selection_strength
        )


class TerminalChain:
    def __init__(self, selector, complement, affix):
        self.selector = copy.deepcopy(selector); selector = None
        self.complement = copy.deepcopy(complement); complement = None
        self.label = self.selector.label
        self.selectional = []

        if self.complement.label not in self.selector.selectional and type(self.complement) == Root:
            self.selector.selectional.append(self.complement.label)

        
        if self.complement.label in self.selector.selectional:
            self.values = self.complement.values.union(self.selector.values)

            if self.selector.selection_strength == False:
                self.linear = self.selector.linear + ("#",) + self.complement.linear
                self.selector.values.update(self.complement.values)

            else:
                if affix == "suffixing":
                    if "#" in self.complement.linear:
                        self.linear = tuple(
                            list(self.complement.linear)[:self.complement.linear.index('#')]
                            + ["-"] 
                            + list(self.selector.linear) 
                            + list(self.complement.linear)[self.complement.linear.index('#'):]
                        )
                    else:
                        self.linear = self.complement.linear + ("-",) + self.selector.linear
                elif affix == "prefixing":
                    self.linear = self.selector.linear + ("-",) + self.complement.linear
                else: 
                    assert False
                
                for token in self.complement.values:
                    if token[0] == "+" or token[0] == "-":
                        self.selector.values.add(token)

        else:
            self.complement.values.update(self.selector.values)
            self.complement.complement.values.update(self.selector.values)
            self.values = self.selector.values
            self.linear = self.selector.linear + ("#",) + self.complement.linear
        
        assert hasattr(self, 'label')
        assert hasattr(self, 'selector')
        assert hasattr(self, 'complement')
        assert hasattr(self, 'linear')
        assert hasattr(self, 'selectional')
        assert hasattr(self, 'values')


    def __str__(self):
        return f"TerminalChain: {self.label}"
    
    def big_string(self):
        return inspect.cleandoc(
            f"""
            TerminalChain:
                label: {self.label}
                selector: {self.selector}
                complement: {self.complement}
                linear: {self.linear}
                selectional: {self.selectional}
                values: {self.values}
            """
        )

    def __eq__(self, other):
        if type(self) != type(other): return False

        return (
                self.label == other.label 
            and self.selector == other.selector
            and self.complement == other.complement
            and self.linear == other.linear
            and self.selectional == other.selectional
            and self.values == other.values
        )


class Root:
    def __init__(self, label):
        self.label = label
        self.values = set()
        self.linear = (self, )
    
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

    def __eq__(self, other):

        if type(self) != type(other): return False

        return (
                self.label == other.label 
            and self.values == other.values
        )


def create_semantic_terminals(learner_version):
    core_terminals = (
        SemanticTerminal(
            label="definite",
            values={"+definite",},
            selectional=["atomic, minimal"],
            selection_strength=False,
        ),
        SemanticTerminal(
            label="definite",
            values={"+definite",},
            selectional=["atomic, minimal"],
            selection_strength=True,
        ),
        SemanticTerminal(
            label="definite",
            values={"-definite",},
            selectional=["atomic, minimal"],
            selection_strength=False,
        ),
        SemanticTerminal(
            label="definite",
            values={"-definite",},
            selectional=["atomic, minimal"],
            selection_strength=True,
        ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"+atomic", "+minimal"},
            selectional=["nominalizer"],
            selection_strength=True,
        ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"+atomic", "+minimal"},
            selectional=["nominalizer"],
            selection_strength=False,
        ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"-atomic", "+minimal"},
            selectional=["nominalizer"],
            selection_strength=True,
        ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"-atomic", "+minimal"},
            selectional=["nominalizer"],
            selection_strength=False,
        ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"-atomic", "-minimal"},
            selectional=["nominalizer"],
            selection_strength=True,
        ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"-atomic", "-minimal"},
            selectional=["nominalizer"],
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
    return [Root(exponent) for exponent in exponents if exponent.isupper()]


def create_nominalizer(root, values, existing_nominalizers):

    for nominalizer in existing_nominalizers:
        if nominalizer.values == values:
            if root.label in nominalizer.selectional:
                return existing_nominalizers
            else:
                nominalizer.selectional.append(root.label)
                return existing_nominalizers
    
    existing_nominalizers.append(
        NominalizerTerminal(
            values = values,
            selectional = [root.label],
        )
    )

    return existing_nominalizers


def select_nominalizer(root, existing_nominalizers):
    weights = [
        nominalizer.weight + ALREADY_SELECTS_BONUS
        if root.label in nominalizer.selectional 
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


def select_adjectivalizer_terminals(second_root, adjectivalizer):
    if second_root.label not in adjectivalizer.selectional:
        adjectivalizer.selectional.append(second_root.label)

    return adjectivalizer


def derive_terminal_chain(enumeration, affix):
    if len(enumeration["roots"]) == 2:
        enumeration["adjective_terminal_chain"] = TerminalChain(
            selector=enumeration["adjectivalizer"],
            complement=enumeration["roots"][1],
            affix=affix,
        )

        enumeration["roots"] = enumeration["roots"][:1]
        del enumeration["adjectivalizer"]

    terminal_chain = TerminalChain(
        selector=enumeration["nominalizer"],
        complement=enumeration["roots"][0],
        affix=affix
    )

    del enumeration["nominalizer"]
    del enumeration["roots"]
    
    if enumeration.get("adjective_terminal_chain") != None:
        terminal_chain = TerminalChain(
            selector=terminal_chain,
            complement=enumeration["adjective_terminal_chain"],
            affix=affix,
        )
    
        del enumeration["adjective_terminal_chain"]

    while len(enumeration.keys()) > 0:

        possible_selectors = [
            key 
            for key 
            in enumeration.keys()
            if terminal_chain.label in enumeration[key].selectional
        ]

        assert len(possible_selectors) > 0

        selector_counts = {
            key: sum([
                1
                for value
                in enumeration.values()
                if value.label in enumeration[key].selectional
            ])
            for key
            in possible_selectors
        }

        selector_key = min(selector_counts, key=selector_counts.get)

        terminal_chain=TerminalChain(
            selector=enumeration[selector_key],
            complement=terminal_chain,
            affix=affix
        )

        del enumeration[selector_key]
        
    return terminal_chain


def select_enumeration(
    roots, 
    nominalizer_terminals,
    values,
    semantic_terminals,
    adjectivalizer
):
    enumeration = dict()
    terminals_used = []

    enumeration["roots"] = roots
    

    nominalizer = select_nominalizer(roots[0], existing_nominalizers=nominalizer_terminals)
    enumeration["nominalizer"] = nominalizer
    terminals_used.append(nominalizer)
    
    semantics = select_semantic_terminals(input_values=values, semantic_terminals=semantic_terminals)

    for i, semantic_terminal in enumerate(semantics):
        enumeration[f"semantic_{i}"] = semantic_terminal
    terminals_used += semantics


    if len(roots) == 2:
        adjectivalizer = select_adjectivalizer_terminals(second_root = roots[1], adjectivalizer=adjectivalizer)
        enumeration["adjectivalizer"] = adjectivalizer
        terminals_used.append(adjectivalizer)
    
    return enumeration, terminals_used

def run(
    input_file_path="./data/input/italian-class-iii-plus-adjectives.txt",
    root_file_path="./data/roots/italian-class-iii-plus-adjectives-ROOTS-list.txt",
    learner_version=1,
    affix = "suffixing",
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
    adjectivalizer = AdjectivalizerTerminal()
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
                values=set(),
                existing_nominalizers=nominalizer_terminals,
            )

        # create enumeration

        while True:
            enumeration, terminals_used = select_enumeration(
                roots=roots,
                nominalizer_terminals=nominalizer_terminals,
                values=values,
                semantic_terminals=semantic_terminals,
                adjectivalizer=adjectivalizer
            )
            
            terminal_chain = derive_terminal_chain(enumeration=enumeration, affix=affix)

            debug_print(verbosity_level, 2, f"TerminalChain linear: {terminal_chain.linear}")

            if input_string.count("#") == terminal_chain.linear.count("#"):
                debug_print(verbosity_level, 2, "we broke out")
                break
        
            debug_print(verbosity_level, 2, "we failed")
            for terminal in terminals_used:
                terminal.weight -= UPDATE_TERMINAL_WEIGHT

run()
