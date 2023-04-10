# define constants
import inspect
import re
import random
import copy
from itertools import combinations
from difflib import SequenceMatcher
import csv
import sys
import matplotlib.pyplot as plt


INITIAL_TERMINAL_WEIGHT = 10.0
UPDATE_TERMINAL_WEIGHT = .1

INITIAL_SPROUTING_RULE_WEIGHT = 1
UPDATE_SPROUTING_RULE_WEIGHT = .1

FLOOR_WEIGHT = 0.0001
UPDATE_REDO_WEIGHT = .1
UPDATE_SUCCESS_WEIGHT = .5

ALREADY_SELECTS_BONUS = 0.75
MORE_SPECIFIC_BONUS = 2
DIACRITIC_BONUS = 2

N_TEST_DERIVATIONS = 100
N_OBSERVATIONS_CHECKPOINT = 1200

LEARN_X_TIMES = 1

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
        self.selectional = set()
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


class AgrTerminal:
    def __init__(self, values):
        self.label = "Agr"
        self.values = values
        self.linear = self
    
    def __str__(self):
        return f"AgrTerminal: {self.values}"
    
    def big_string(self):
        return inspect.cleandoc(
            f"""
            AgrTerminal:
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


class TerminalChain:
    def __init__(self, selector, complement, affix):
        self.selector = copy.deepcopy(selector); selector = None
        self.complement = copy.deepcopy(complement); complement = None
        self.label = self.selector.label
        self.selectional = set()

        if self.complement.label not in self.selector.selectional and type(self.complement) == Root:
            self.selector.selectional.add(self.complement.label)

        
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
                    if (token[0] == "+" or token[0] == "-") and "feminine" not in token:
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

    def __hash__(self):
        return hash((self.label))


class VocabularyItem:
    def __init__(self, pronunciation, label, values, diacritic, triggers):

        assert pronunciation != ""

        self.pronunciation = pronunciation
        self.label = label
        self.values = values
        self.diacritic = diacritic
        self.triggers = triggers
        self.weight = INITIAL_TERMINAL_WEIGHT
    
    def __str__(self):
        return f"VocabularyItem: {self.pronunciation}"

    def big_string(self):
        return inspect.cleandoc(
            f"""
            VocabularyItem:
                pronunciation: {self.pronunciation}
                label: {self.label}
                values: {self.values}
                diacritic: {self.diacritic}
                triggers: {self.triggers}
                weight: {self.weight}
            """
        )

    def full_equality(self, other):
        if type(self) != type(other): return False

        return (
                self.pronunciation == other.pronunciation 
            and self.label == other.label
            and self.values == other.values
            and self.diacritic == other.diacritic
            and self.triggers == other.triggers
            and self.weight == other.weight)

    def __eq__(self, other):
        if type(self) != type(other): return False

        return (
                self.pronunciation == other.pronunciation 
            and self.label == other.label
            and self.values == other.values
            and self.triggers == other.triggers
            )


class SproutingRule:
    def __init__(self, split_off_vi, large_vi):
        self.trigger_label=large_vi.label
        self.trigger_values=large_vi.values
        self.trigger_diacritic=split_off_vi.diacritic
        self.keep_values=large_vi.values - split_off_vi.values
        self.weight = INITIAL_SPROUTING_RULE_WEIGHT

    def __str__(self):
        return f"SproutingRule: {self.trigger_label}"

    def big_string(self):
        return inspect.cleandoc(
            f"""
            SproutingRule:
                trigger_label: {self.trigger_label}
                trigger_values: {self.trigger_values}
                trigger_diacritic: {self.trigger_diacritic}
                keep_values: {self.keep_values}
                weight: {self.weight}
            """
        )

    def __eq__(self, other):
        assert type(self) == type(other)

        return (
                self.trigger_label == other.trigger_label 
            and self.trigger_values == other.trigger_values
            and self.trigger_diacritic == other.trigger_diacritic
            and self.keep_values == other.keep_values
        )

    def full_equality(self, other):
        if type(self) != type(other): return False

        return (
                self.trigger_label == other.trigger_label 
            and self.trigger_values == other.trigger_values
            and self.trigger_diacritic == other.trigger_diacritic
            and self.keep_values == other.keep_values
            and self.weight == other.weight
        )

    def check_if_use(self):
        if random.random() < self.weight / (self.weight + 1): #should we start at 2/3 instead? (add 0.5)
            return True
        else:
            return False


def create_semantic_terminals(learner_version):
    core_terminals = (
        #TURNED OFF
        # SemanticTerminal(
        #     label="definite",
        #     values={"+definite",},
        #     selectional={"atomic, minimal"},
        #     selection_strength=False,
        # ),
        # # SemanticTerminal(
        # #     label="definite",
        # #     values={"+definite",},
        # #     selectional={"atomic, minimal"},
        # #     selection_strength=True,
        # # ),
        # SemanticTerminal(
        #     label="definite",
        #     values={"-definite",},
        #     selectional={"atomic, minimal"},
        #     selection_strength=False,
        # ),
        # # SemanticTerminal(
        # #     label="definite",
        # #     values={"-definite",},
        # #     selectional={"atomic, minimal"},
        # #     selection_strength=True,
        # # ),
        # SemanticTerminal(
        #     label="atomic, minimal",
        #     values={"+atomic", "+minimal"},
        #     selectional={"nominalizer"},
        #     selection_strength=True,
        # ),
        # # SemanticTerminal(
        # #     label="atomic, minimal",
        # #     values={"+atomic", "+minimal"},
        # #     selectional={"nominalizer"},
        # #     selection_strength=False,
        # # ),
        # SemanticTerminal(
        #     label="atomic, minimal",
        #     values={"-atomic", "+minimal"},
        #     selectional={"nominalizer"},
        #     selection_strength=True,
        # ),
        # # SemanticTerminal(
        # #     label="atomic, minimal",
        # #     values={"-atomic", "+minimal"},
        # #     selectional={"nominalizer"},
        # #     selection_strength=False,
        # # ),
        # SemanticTerminal(
        #     label="atomic, minimal",
        #     values={"-atomic", "-minimal"},
        #     selectional={"nominalizer"},
        #     selection_strength=True,
        # ),
        # # SemanticTerminal(
        # #     label="atomic, minimal",
        # #     values={"-atomic", "-minimal"},
        # #     selectional={"nominalizer"},
        # #     selection_strength=False,
        # # ),  
    )

    additional_terminals = {
        1: (
            SemanticTerminal(
                label="definite",
                values={"+definite",},
                selectional={"atomic"},
                selection_strength=False,
            ),
            SemanticTerminal(
                label="definite",
                values={"-definite",},
                selectional={"atomic"},
                selection_strength=False,
            ),
            SemanticTerminal(
                label="atomic",
                values={"+atomic"},
                selectional={"nominalizer"},
                selection_strength=True,
            ),
            SemanticTerminal(
                label="atomic",
                values={"-atomic"},
                selectional={"nominalizer"},
                selection_strength=True,
            ),
        ),
        2: (
            SemanticTerminal(
                label="definite",
                values={"+definite",},
                selectional={"atomic"},
                selection_strength=False,
            ),
            SemanticTerminal(
                label="definite",
                values={"-definite",},
                selectional={"atomic"},
                selection_strength=False,
            ),
            SemanticTerminal(
                label="atomic",
                values={"+atomic"},
                selectional={"nominalizer"},
                selection_strength=True,
            ),
            SemanticTerminal(
                label="atomic",
                values={"-atomic"},
                selectional={"nominalizer"},
                selection_strength=True,
            ),
        ),
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


def create_nominalizer(root, values, existing_nominalizers, learner_version):
    #is there a nominalizer with these values?
    for nominalizer in existing_nominalizers:
        if nominalizer.values == values:
            # if it exists already AND the Root we passed in is already part of its selectional, boost weight a little
            if root.label in nominalizer.selectional:
                #TURNED OFF
                # print(f"this nominalizer with values {nominalizer.values} already selects for {root.label}: increase weight from current {nominalizer.weight}")
                # nominalizer.weight += UPDATE_REDO_WEIGHT
                return existing_nominalizers
            # otherwise, add the Root we passed in to its selectional
            else:
                nominalizer.selectional.add(root.label)
                return existing_nominalizers
    

    if learner_version == 1:
        #if there isn't already a nominalizer with these values, make one
        existing_nominalizers.append(
            NominalizerTerminal(
                values = values,
                selectional = {root.label},
            )
        )
    
    # \sout{assert learner_version == 1} no, because we need to add Roots to the sem-gendered noms in learner 2, too.
    return existing_nominalizers


def create_initial_nominalizers():
    return [
        NominalizerTerminal(
            values={"+feminine"},
            selectional=set(),
        ),
        NominalizerTerminal(
            values={"-feminine"},
            selectional=set(),
        ),
        NominalizerTerminal(
            values=set(),
            selectional=set(),
        ),
    ]


def create_nominalizer_given_selectional(selectional, values, existing_nominalizers, combining):
    # is there a nominalizer with these values?
    for nominalizer in existing_nominalizers:
        if nominalizer.values == values:
            # if we're combining, that means one of the combinees was just successful. let's boost the combined result, too.
            if combining:
                nominalizer.weight += UPDATE_SUCCESS_WEIGHT
            # if the nominalizer that already exists, add to its weight: the call came from an input line that used it
            # if it exists already AND the Root we passed in is already part of its selectional, boost weight a little (called either: as we clean up noms with references to un-segmented agreement word VIs during generation, or in combine_noms when we consolidate noms with overlapping selectionals)
            if nominalizer.selectional == selectional:
                #TURNED OFF
                # print(f"(given selectional): this nominalizer with values {nominalizer.values} already selects for {root.label}: increase weight from current {nominalizer.weight}")
                # nominalizer.weight += UPDATE_REDO_WEIGHT 
                return existing_nominalizers
            # if we passed in a different selectional (might happen from combine_noms if the intersection between two single-value noms' selectional grew in the meantime)
            else: 
                nominalizer.selectional = nominalizer.selectional.union(selectional)
                return existing_nominalizers
    
    existing_nominalizers.append(
        NominalizerTerminal(
            values = values,
            selectional = selectional, 
        )
    )

    return existing_nominalizers


def find_nominalizer_with_values(nominalizers, values):
    for nom in nominalizers:
        if nom.values == values:
            return nom
    
    assert False


def select_nominalizer(root, existing_nominalizers, only_already_selected, values, learner_version, phase, test_and_learn):
    
    if learner_version == 1:
        if only_already_selected: #only during processing phase, learner 1
            weights = [
                nominalizer.weight
                if root.label in nominalizer.selectional 
                else 0 
                for nominalizer 
                in existing_nominalizers
            ]
        else:
            already_selects_list = [nominalizer for nominalizer in existing_nominalizers if root.label in nominalizer.selectional]
            # max_non_selecting_weight = max(nomin.weight for nomin in existing_nominalizers if root.label not in nomin.selectional)
            if len(already_selects_list) == 0:
                return existing_nominalizers[0]
            else:
                max_values_had_by_n_already_selects = max(len(nomi.values) for nomi in already_selects_list)
                contains_already_selects = [] #so we can add weight for (each value of) nominalizers with values that encompass the values of noms that are KNOWN to select for the Root (generalize only based on one inflectional context / data point)
                for nom in already_selects_list: 
                    for nominalizer in existing_nominalizers:
                        if nominalizer.values.issuperset(nom.values):
                            contains_already_selects.append(nominalizer)
                unique_contains_already_selects = []
                for nomz in contains_already_selects:
                    if nomz not in unique_contains_already_selects:
                        unique_contains_already_selects.append(nomz)
                weights = []
                for nom in existing_nominalizers:
                    # print(f"{nom.values}")
                    if nom.weight == 0: #don't ever select noms that we already discarded as hypotheses 
                        # print(f"i already have zero weight\n")
                        weights.append(0)
                    elif nom in already_selects_list: # extra boost for noms that already select, PLUS multiplier for extra values (full(er) inflectional context coverage)
                        # print(f"i already select, so i get (1+n_val)*boost\n")
                        weights.append(nom.weight + ALREADY_SELECTS_BONUS + ALREADY_SELECTS_BONUS * len(nom.values))
                    elif nom in unique_contains_already_selects and max_values_had_by_n_already_selects == 1:
                        # print(f"i contain something that already selects, and everything that already selects is only one value long (not fully covering the paradigm), so i get (1+n_val)*boost too\n")
                        weights.append(nom.weight + ALREADY_SELECTS_BONUS + ALREADY_SELECTS_BONUS * len(nom.values))
                    elif nom in unique_contains_already_selects: # boost for noms that encompass noms that already select: boosting their extra values (full(er) inflectional context coverage) than known selectors
                        # print(f"i contain something that already selects, so i get (n_val)*boost\n")
                        weights.append(nom.weight + ALREADY_SELECTS_BONUS * len(nom.values))
                    else: # all other noms are possible, too, but no boost
                        # print(f"no relation, zero weight \n") \sout{print(f"no relation, just my weight\n")}
                        weights.append(0) #weights.append(nom.weight) <- nvm. every Root gets at least one nom that selects for it. don't want to allow nominalizers that have no relationship to the diacritic borne by that to select, which can even happen most of the time if one nom weight is just super high! 

        return random.choices(population=existing_nominalizers, weights=weights)[0]
    
    elif learner_version == 2:
        if {"+feminine"} in values:
            return find_nominalizer_with_values(existing_nominalizers, {"+feminine"})
        elif {"-feminine"} in values:
            return find_nominalizer_with_values(existing_nominalizers, {"-feminine"})
        else:
            if phase == "process":
                return existing_nominalizers[2]
            elif test_and_learn == "just_test":
                return existing_nominalizers[2]
            elif phase == "test":
                assert False


def select_vis_to_combine(vocabulary_items, nominalizer_vi_used, nom_being_considered):
    return [
        vi 
        for vi
        in vocabulary_items
        if (vi.values == nom_being_considered.values
            and
            vi.weight > FLOOR_WEIGHT
            and # don't let VIs with triggers for VIs spelling out the same values combine (e.g. no -a.sg and -e.sg triggers on the same combined nom VI)
            len({trigger[1] for trigger in nominalizer_vi_used[0].triggers}.intersection({trigger[1] for trigger in vi.triggers})) == 0
        )
    ]


def select_semantic_terminals(input_values, semantic_terminals):
    
    selected_terminals = []
    
    for values in input_values:
        choices = [
            terminal 
            for terminal 
            in semantic_terminals
            if terminal.values == values
        ]

        # assert len(choices) == 2

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
        adjectivalizer.selectional.add(second_root.label)

    return adjectivalizer


def derive_terminal_chain(numeration, affix):
    if len(numeration["roots"]) == 2:
        numeration["adjective_terminal_chain"] = TerminalChain(
            selector=numeration["adjectivalizer"],
            complement=numeration["roots"][1],
            affix=affix,
        )

        numeration["roots"] = numeration["roots"][:1]
        del numeration["adjectivalizer"]

        terminal_chain = TerminalChain(
            selector=numeration["nominalizer"],
            complement=numeration["roots"][0],
            affix=affix
        )

        del numeration["nominalizer"]
        del numeration["roots"]

        possible_selectors = [
                key 
                for key 
                in numeration.keys()
                if terminal_chain.label in numeration[key].selectional
            ]

        assert len(possible_selectors) > 0

        selector_counts = {
            key: sum([
                1
                for value
                in numeration.values()
                if value.label in numeration[key].selectional
            ])
            for key
            in possible_selectors
        }

        selector_key = min(selector_counts, key=selector_counts.get)

        terminal_chain=TerminalChain(
            selector=numeration[selector_key],
            complement=terminal_chain,
            affix=affix
        )

        del numeration[selector_key]

        terminal_chain = TerminalChain(
                selector=terminal_chain,
                complement=numeration["adjective_terminal_chain"],
                affix=affix,
            )
        
        del numeration["adjective_terminal_chain"]

        possible_selectors = [
                key 
                for key 
                in numeration.keys()
                if terminal_chain.label in numeration[key].selectional
            ]

        assert len(possible_selectors) > 0

        selector_counts = {
            key: sum([
                1
                for value
                in numeration.values()
                if value.label in numeration[key].selectional
            ])
            for key
            in possible_selectors
        }

        selector_key = min(selector_counts, key=selector_counts.get)

        terminal_chain=TerminalChain(
            selector=numeration[selector_key],
            complement=terminal_chain,
            affix=affix
        )

        del numeration[selector_key]


    else:
        terminal_chain = TerminalChain(
            selector=numeration["nominalizer"],
            complement=numeration["roots"][0],
            affix=affix
        )

        del numeration["nominalizer"]
        del numeration["roots"]

        while len(numeration.keys()) > 0:

            possible_selectors = [
                key 
                for key 
                in numeration.keys()
                if terminal_chain.label in numeration[key].selectional
            ]

            assert len(possible_selectors) > 0

            selector_counts = {
                key: sum([
                    1
                    for value
                    in numeration.values()
                    if value.label in numeration[key].selectional
                ])
                for key
                in possible_selectors
            }

            selector_key = min(selector_counts, key=selector_counts.get)

            terminal_chain=TerminalChain(
                selector=numeration[selector_key],
                complement=terminal_chain,
                affix=affix
            )

            del numeration[selector_key]
        
    return terminal_chain


def select_numeration(
    roots, 
    nominalizer_terminals,
    values,
    semantic_terminals,
    adjectivalizer, 
    phase,
    test_and_learn,
    learner_version,
    verbose
):
    numeration = dict()
    terminals_used = []

    numeration["roots"] = roots

    if learner_version == 1:
        if phase == "process": # we don't want to add gender diacritics to nominalizers AND Roots to those nominalizers without fully reliable evidence, so only valueless nom OR nom that already_selects
            # if we've seen this Root at all and we have some Root(s) that select for it
            if sum([nom.weight for nom in nominalizer_terminals if roots[0].label in nom.selectional]) > 0:
                # pick from those (only_already_selected = True)
                nominalizer = select_nominalizer(roots[0], existing_nominalizers=nominalizer_terminals, only_already_selected=True, values=values, learner_version=learner_version, phase=phase, test_and_learn=test_and_learn)
            # if we haven't seen this Root at all (if the Root isn't already selected by something)
            else:
                # always select the value-less nominalizer when we're processing input data...only generate single-derivation hypotheses
                nominalizer = nominalizer_terminals[0] 
        elif phase == "test": # we can try all sorts now. won't add Root to nom unless it was successful, and actually contributed a gender diacritic used in the success
            nominalizer = select_nominalizer(roots[0], existing_nominalizers=nominalizer_terminals, only_already_selected=False, values=values, learner_version=learner_version, phase=phase, test_and_learn=test_and_learn)
    
    elif learner_version == 2:
        nominalizer = select_nominalizer(roots[0], existing_nominalizers=nominalizer_terminals, only_already_selected=False, values=values, learner_version=learner_version, phase=phase, test_and_learn=test_and_learn)
    

    if verbose:
        print(f"we selected the nominalizer with values: {nominalizer.values}") 
    
    numeration["nominalizer"] = nominalizer
    terminals_used.append(nominalizer)

    # if we don't remove these gender features, which are never introduced on semantic terminals, we won't be able to finish picking semantic terminals
    # if learner_version == 2:
    #     if {'+feminine'} in values:
    #         print(f"HERE!!! {values}")
    #         values.remove({"+feminine"})
    #         print(f"{values}")
    #     if {'-feminine'} in values:
    #         values.remove({"-feminine"})
    
    semantics = select_semantic_terminals(input_values=[value for value in values if value != {'+feminine'} and value != {'-feminine'}], semantic_terminals=semantic_terminals)

    for i, semantic_terminal in enumerate(semantics):
        numeration[f"semantic_{i}"] = semantic_terminal
    terminals_used += semantics


    if len(roots) == 2:
        adjectivalizer = select_adjectivalizer_terminals(second_root = roots[1], adjectivalizer=adjectivalizer)
        numeration["adjectivalizer"] = adjectivalizer
        terminals_used.append(adjectivalizer)
    
    return numeration, terminals_used


def create_vi(pronunciation, label, values, triggers, vocabulary_items, redo_bonus):
    # if pronunciation == "null" and values == set():
    #     return False, None, vocabulary_items
    
    new_vi = VocabularyItem(
        pronunciation=pronunciation,
        label=label,
        values=values,
        diacritic=f"{pronunciation}_{get_diacritic_number(pronunciation, vocabulary_items)}",
        triggers=triggers,
    ) 

    if new_vi in vocabulary_items: 
        if redo_bonus:
            vocabulary_items[vocabulary_items.index(new_vi)].weight += UPDATE_REDO_WEIGHT 
            print(f"\ncreate_vi: tried {vocabulary_items[vocabulary_items.index(new_vi)].label}: {vocabulary_items[vocabulary_items.index(new_vi)].diacritic}, triggers = {vocabulary_items[vocabulary_items.index(new_vi)].triggers}, weight = {vocabulary_items[vocabulary_items.index(new_vi)].weight}..already existed")
        return False, vocabulary_items[vocabulary_items.index(new_vi)], vocabulary_items
    else:
        print(f"\ncreate_vi: made {new_vi.label}: {new_vi.diacritic}, triggers = {new_vi.triggers}, weight = {new_vi.weight}")
        return True, new_vi, vocabulary_items + [new_vi]


def create_sprouting_rule(split_off_vi, large_vi, sprouting_rules):
    new_sprouting = SproutingRule(
        split_off_vi=split_off_vi,
        large_vi=large_vi
    ) 

    if new_sprouting in sprouting_rules:
        for rule in sprouting_rules:
            if rule == new_sprouting:
                rule.weight += UPDATE_SPROUTING_RULE_WEIGHT #if we check for a sprouting rule that already exists, add to its weight??
        return sprouting_rules
    else:
        sprouting_rules.append(new_sprouting)
        return sprouting_rules 


def partial_overlap(set1, set2):
    if set1 == set2:
        return False
    
    count = sum([
        1
        for val
        in set1
        if val in set2
    ])

    if count > 0:
        return True
    else:
        return False


def compare_vi(vocabulary_item, vocabulary_items):
    # print(f"COMPARE_VI has been called on {vocabulary_item.diacritic}")

    #(1) first, look for VIs that completely overlap except in triggers... \checkmark: should only apply to ROOT VIs bc of requirement that triggers overlap.
    full_match_list = [
        vi
        for vi
        in vocabulary_items
        if (
            vi.label == vocabulary_item.label
            and
            vi.values == vocabulary_item.values
            and
            vi.pronunciation == vocabulary_item.pronunciation
            and 
            vi.diacritic != vocabulary_item.diacritic
            and
            len(vi.triggers.intersection(vocabulary_item.triggers)) > 0 #there are some overlapping triggers
            and 
            ((len({trigger[1] for trigger in vi.triggers}.intersection(trigger[1] for trigger in vocabulary_item.triggers)) == 0) #either there are no overlaps in what the triggered VIs spell out
            or
            ({trigger[1] for trigger in vi.triggers}.intersection(trigger[1] for trigger in vocabulary_item.triggers) == {frozenset()})) #or the only overlap is frozenset() i.e. the trigger in common is for the null empty triggers nominalizer
            # \sout{and
            # vi.weight > INITIAL_TERMINAL_WEIGHT + 1}
        )
    ]

    for vi in full_match_list:
        print(f"     what if we combine triggers with the otherwise identical vi {vi.diacritic} (triggers: {vi.triggers})?")
        is_new, triggercombined, vocabulary_items = create_vi(
            pronunciation=vi.pronunciation,
            label=vi.label,
            values=vi.values,
            triggers = set().union(
                vocabulary_item.triggers,
                vi.triggers
            ),
            vocabulary_items=vocabulary_items,
            redo_bonus=False # (because we don't want to even further advantage Root-borne diacritics - would benefit cross-inflectional diacritic-bearing Root VIs above single-inflection-diacritic Root VIs, but also above non-diacritic-bearing VIs (which are already too dispreferred)) ?
        )
        if is_new:
            print(f"     -> created a new vi {triggercombined.diacritic} \tspelling out {triggercombined.label}: {triggercombined.values} \t\t triggering {triggercombined.triggers}")

    #(2) second, look for VIs that partially overlap in values, and in pronunciations
    partial_match_list = [
        vi
        for vi
        in vocabulary_items
        if (
            vi.label == vocabulary_item.label
            and
            partial_overlap(vi.values, vocabulary_item.values)
            and
            len(shared_substring(vi.pronunciation, vocabulary_item.pronunciation)[0]) > 0 #if one or both are null, compare_vis returns "" so they won't be included.
        )
    ]

    return partial_match_list, vocabulary_items


def shared_substring(string1, string2):
    if string1 == "null" and string2 == "null":
        return ('', 'null', 'null')	

    if string1 == "null":
        return ('', 'null', string2)

    if string2 == "null":
        return ('', string1, 'null')
	
    match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
	
    substring = string1[match.a: match.a + match.size]

    if substring == string1:
        string1_minus = "null"
    else:
        string1_minus = string1.replace(substring, '')

    if substring == string2:
        string2_minus = "null"
    else:
        string2_minus = string2.replace(substring, '')

    return substring, string1_minus, string2_minus


def generalize_vi(new_vi, vocabulary_items, affix):
    new_vi_pairs = []
    match_list, vocabulary_items = compare_vi(
        vocabulary_item=new_vi,
        vocabulary_items=vocabulary_items
    )

    print(f"generalize_vi: here's what is in match_list: {match_list}")
    for intersecting_vi in match_list:
        substring, new_vi_ex, intersecting_vi_ex = shared_substring(
            new_vi.pronunciation,
            intersecting_vi.pronunciation
        )

    # (A) intersection:
        # \sout{if not (
        #     substring == "null" or 
        #     intersecting_vi_ex == "null"
        # ):}
        if not ( #TODO what i need to do with various null VIs that i want to manipulate in both directions...(5b) and (7)
            new_vi_ex == "null" or 
            intersecting_vi_ex == "null"
        ):
            if new_vi.pronunciation[:len(substring)] == substring: #TODO am i sure about never having VIs with the same pronunciation??
                if affix == "suffixing":
                    label = new_vi.label
                elif affix == "prefixing":
                    label = "Agr"
                else:
                    assert False
            elif new_vi.pronunciation[-len(substring):] == substring:
                if affix == "suffixing":
                    label = "Agr"
                elif affix == "prefixing":
                    label = new_vi.label
                else:
                    assert False
            else:
                assert False
        else:
            label = new_vi.label
            
        intersection_is_new, intersection_vi, vocabulary_items = create_vi(
            pronunciation=substring,
            label=label,
            values=new_vi.values.intersection(intersecting_vi.values),
            triggers=new_vi.triggers.union(intersecting_vi.triggers),
            vocabulary_items=vocabulary_items, 
            redo_bonus=False #TURNED OFF: changing this from True to False
        )

        new_vi_pairs.append((intersection_vi, new_vi))
        new_vi_pairs.append((intersection_vi, intersecting_vi))

        if (intersecting_vi.pronunciation == new_vi.pronunciation): #TODO: think through the -e II.f.pl and -e III.sg ?
            return new_vi_pairs, vocabulary_items
        

    # (B) intersecting-VI MINUS newVI:
        if (
            new_vi_ex == "null" or intersecting_vi_ex == "null"
        ):
            label = new_vi.label
        else:
            if new_vi.pronunciation[:len(substring)] == substring:
                if affix == "suffixing":
                    label = "Agr"
                elif affix == "prefixing":
                    label = intersecting_vi.label
                else:
                    assert False
            elif new_vi.pronunciation[-len(substring):] == substring:
                if affix == "suffixing":
                    label = intersecting_vi.label
                elif affix == "prefixing":
                    label = "Agr"
                else:
                    assert False
            else:
                assert False

            if not (intersecting_vi.values - new_vi.values) == set():
                subtracted_from_intersecting_is_new, subtracted_from_intersecting_vi, vocabulary_items = create_vi(
                    pronunciation=intersecting_vi_ex,
                    label=label,
                    values=intersecting_vi.values - new_vi.values,
                    triggers=intersecting_vi.triggers,
                    vocabulary_items=vocabulary_items, 
                    redo_bonus=False #TURNED OFF: changing this from True to False
                )
                new_vi_pairs.append((subtracted_from_intersecting_vi, intersecting_vi))

            
        # (C) newVI MINUS intersecting-VI:
            if (
                new_vi_ex == "null" or intersecting_vi_ex == "null"
            ):
                label = new_vi.label
            else:
                if new_vi.pronunciation[:len(substring)] == substring:
                    if affix == "suffixing":
                        label = "Agr"
                    elif affix == "prefixing":
                        label = new_vi.label
                    else:
                        assert False
                elif new_vi.pronunciation[-len(substring):] == substring:
                    if affix == "suffixing":
                        label = new_vi.label
                    elif affix == "prefixing":
                        label = "Agr"
                    else:
                        assert False
                else:
                    assert False

            if not (new_vi.values - intersecting_vi.values) == set():
                subtracted_from_new_is_new, subtracted_from_new_vi, vocabulary_items = create_vi(
                    pronunciation=new_vi_ex,
                    label=label,
                    values=new_vi.values - intersecting_vi.values,
                    triggers=new_vi.triggers,
                    vocabulary_items=vocabulary_items, 
                    redo_bonus=False #TURNED OFF: changing this from True to False
                )
                new_vi_pairs.append((subtracted_from_new_vi, new_vi))

    return new_vi_pairs, vocabulary_items


def slice_terminal_chain(terminal_chain):

    assert terminal_chain.linear[0] != "#"
    assert terminal_chain.linear[-1] != "#"

    result = []
    sublist = []
    for x in terminal_chain.linear:
        if x == "#":
            result.append(tuple(sublist))
            sublist = []
        else:
            sublist.append(x)
    result.append(tuple(sublist))
    return result


def all_combinations(initial_set):
    result = [set()]
    for r in range(1, len(initial_set)+1):
        result += [set(combination) for combination in combinations(initial_set, r)]
    
    return result


def get_diacritic_number(pronunciation, vocabulary_items):
    return 1 + sum([
        1
        for vi
        in vocabulary_items
        if vi.pronunciation == pronunciation
    ])


def insert_agr(terminals):

    for index, terminal in enumerate(terminals):
        if type(terminal) == AdjectivalizerTerminal:
            terminals.insert(index+1, AgrTerminal(values=terminal.values))

    return terminals


def prep_slices(morphs, terminals, affix):

    assert len(morphs) <= len(terminals)

    root_index = next((i for i, s in enumerate(morphs) if s.isupper()), None)

    terminals = insert_agr(terminals)

    if root_index is not None:
        while len(morphs) < len(terminals):
            # print(morphs)
            
            root_index = next((i for i, s in enumerate(morphs) if s.isupper()), None)
            if root_index is not None:
                if affix  == "suffixing":
                    morphs.insert(root_index+1, "null")
                elif affix == "prefixing":
                    morphs.insert(root_index, "null")
                else:
                    assert False
                
                assert len(morphs) == len(terminals)

    return morphs, terminals


def generate_vi(terminal_chain, input_string, roots, vocabulary_items, nominalizers, sprouting_rules, affix, learner_version):

    string_slices = input_string.split("#") 
    tc_slices = slice_terminal_chain(terminal_chain)

    assert len(string_slices) == len(tc_slices)

    nominalizers_in_tc = [
        item
        for item
        in terminal_chain.linear
        if type(item) == NominalizerTerminal
    ]

    assert len(nominalizers_in_tc) == 1

    nominalizer=nominalizers_in_tc[0] 

    for string_slice, tc_slice in zip(string_slices, tc_slices):
        diacritics_in_this_word = set()
        morphs = string_slice.split("-")
        terminals = [
            item
            for item
            in tc_slice
            if item != "-"
        ]
        print(f"\nnow working with the word '{string_slice}', mapping to {len(terminals)} terminals:")

        morphs, terminals = prep_slices(morphs=morphs, terminals=terminals, affix=affix)

        if affix  == "suffixing":
            zipper = zip(terminals[::-1], morphs[::-1])
        elif affix == "prefixing":
            zipper = zip(terminals, morphs)
        else:
            assert False
        
        for terminal, morph in zipper:
            
            zero_trigger_vis = set([
                (vi.pronunciation, frozenset([value 
                                        for value 
                                        in vi.values 
                                        if value[0] in ["+", "-"] and value not in ["+feminine", "-feminine"]])
                 )
                for vi 
                in vocabulary_items 
                if (vi.diacritic in diacritics_in_this_word) and (len(vi.triggers) == 0)
            ])

            if len(zero_trigger_vis) == 0:
                x = [set()] 
            else:
                x = [set(), zero_trigger_vis]

            for triggers in x:
                if terminal.label == "nominalizer" and learner_version == 1:
                    new_values = terminal.values
                else:
                    new_values = set([
                        value 
                        for value 
                        in terminal.values 
                        if value[0] in ["+", "-"]
                    ])

                is_new, new_vi, vocabulary_items = create_vi(
                    pronunciation=morph,
                    label=terminal.label,
                    values=new_values,
                    triggers=triggers,
                    vocabulary_items=vocabulary_items,
                    redo_bonus = False
                )

                further_vis = []

                further_vis, vocabulary_items = generalize_vi(
                        new_vi=new_vi,
                        vocabulary_items=vocabulary_items, 
                        affix=affix
                    )

                #if we're in a word with a Root...
                if any(char.isupper() for char in string_slice): #TODO: IS THIS RIGHT FOR ADJECTIVES ?????
                    print(f"  we're in a lexical word...")
                    diacritics_in_this_word.add(new_vi.diacritic)
                    print(f"  - we add the newvi's diacritic: diacritics_in_this_word now contains {diacritics_in_this_word}")
                    #TO BE TURNED OFF?: was only put in place to counteract redo_bonus for split out vis from generalize_vi()
                    # if (not is_new) and (len(further_vis) == 0) and (x == [set()]): #add redo weight to vis if they're rederived, w/o causing any new intersection VIs, and they're the only VI for that terminal (only created with no triggers): effectively only for atomic (Num) terminals, not Roots, not nominalizers
                    #     vocabulary_items[vocabulary_items.index(new_vi)].weight += UPDATE_REDO_WEIGHT
                    if(len(further_vis) > 0):
                        for split_out_vi, source_vi in further_vis:
                            #TODO source_vi.weight = FLOOR_WEIGHT ?
                            if source_vi.diacritic in diacritics_in_this_word:
                                diacritics_in_this_word.remove(source_vi.diacritic)
                                diacritics_in_this_word.add(split_out_vi.diacritic)
                                print(f"  - we split out {split_out_vi.diacritic} from {source_vi.diacritic} (which should be the newvi {new_vi.diacritic}:")
                                print(f"    diacritics_in_this_word now contains {diacritics_in_this_word}")    

                #if we're in a non-Root word...
                else:
                    print(f"  we're in a functional word...")
                    if learner_version == 1:
                        #here we handle setting the values of our current nominalizer so that we don't try to create a nominalizer with conflicting diacritics for the same inflectional context
                        if new_vi.pronunciation != "null": 
                            #if there is no overlap btw nom's triggers' vi values and newvi's values:
                            if len(set().union(*[set().union(*[v.values for v in vocabulary_items if v.diacritic == value]) for value in nominalizer.values]).intersection(new_vi.values)) == 0: 
                                #ADD new_vi (fine if we have the no-value nominalizer to start (1st instance of Root), fine if the nom we picked (which had to select for the Root) has no values that spellout any of the same values as new_vi
                                nominalizer.values.update({new_vi.diacritic})  
                            
                            #elif there is overlap (e.g. new_vi (pl def article) and nom trigger for a pl Agr), but there's a (presumably responsible) value in our nom that is split out from the new_vi (e.g. pl Agr on nom is part of the new_vi), so that should be taken care of. do nothing
                            elif len([value for value in nominalizer.values if (new_vi.diacritic, value) in further_vis]) > 0: 
                                pass #do nothing, keep the original values of current nominalizer
                            
                            #else there is overlap (e.g. new_vi (le pl def article) and nom trigger for a -i pl Agr), and none of the nominalizer's value vis are a smaller piece inside new_vi 
                            else:
                                #CHANGE the nominalizer to ONLY have new_vi as values
                                nominalizer.values = set().union({new_vi.diacritic})
                            #we either add the newvi's diacritic; or if , keep as is; or if there are conflicting values, set to only newvi's diacritic: 
                            print(f"  - nominalizer's values are now {nominalizer.values}")

                    #here we handle cleaning up the nominalizer inventory wrt diacritics for non-segmented agreeing words (e.g. una)
                    if(len(further_vis) > 0):
                        for split_out_vi, source_vi in further_vis:
                             #TODO??: source_vi.weight = FLOOR_WEIGHT or max(FLOOR_WEIGHT, vi.weight - UPDATE_TERMINAL_WEIGHT)
                             if split_out_vi.label == "Agr":  
                                print(f"  - but that newvi helped us find a new Agr node vi: {split_out_vi.diacritic}")

                                if learner_version == 1:
                                    # (1) clean up our List1: find all the nominalizers in state that include non-segmented diacritics as values...
                                    for nom in nominalizers:
                                        if source_vi.diacritic in nom.values: 
                                            print(f"     so (1) we clean up our nominalizer inventory: \n    > the nominalizer with these values ({nom.values}) gets set to 0")
                                            #... and never select them again (stem the tide of nominalizers)
                                            nom.weight = 0 
                                            #...and create new nominalizer that replaces the larger vi with the split out vi
                                            print(f"    > and we make sure a nominalizer with {split_out_vi.diacritic} instead of {source_vi.diacritic} exists")
                                            nominalizers = create_nominalizer_given_selectional(
                                                values = (nom.values - {source_vi.diacritic}).union({split_out_vi.diacritic}),
                                                selectional = nom.selectional,
                                                existing_nominalizers=nominalizers,
                                                combining = False)
                                        
                                # (2) make an Agr sprouting rule (or check that it already exists)
                                print(f"     and (2) we make sure an Agr sprouting rule exists, splitting {source_vi.values} to host {split_out_vi.values}")
                                sprouting_rules = create_sprouting_rule(split_out_vi, source_vi, sprouting_rules)

                                if learner_version == 1:
                                    if source_vi.diacritic in nominalizer.values:
                                        nominalizer.values = (nominalizer.values - {source_vi.diacritic}).union({split_out_vi.diacritic})
                                        print(f"     and (3) if the Agr was split out of the newvi in THIS input observation, we change the nominalizer we're currently using to have the split out value(s): {nominalizer.values}") 

                    if nominalizer.values != set(): # not just in learner_version == 1: in learner 2, we are only here with core nouns, and nouns that have already been added to gender_dict{}, so safe to add Root to selectional.
                        print(f"  - finally, make (sure) the nominalizer with current (non-empty!) values: {nominalizer.values} has root {roots[0]} in its selectional")    
                        nominalizers = create_nominalizer(
                            root=roots[0],
                            values=nominalizer.values,
                            existing_nominalizers=nominalizers,
                            learner_version=learner_version
                        ) #now that we can generate multiple-feature nominalizers, not just single-feature ns, we can give either a small boost when rederived

    return vocabulary_items, nominalizers, sprouting_rules


def insert_vi(terminal_chain, vocabulary_items, verbose):
    full_pronunciation = ""
    vis_used = []
    if verbose:
        print("------------------------------\n spellout time \n------------------------------")
 
    slices = slice_terminal_chain(terminal_chain=terminal_chain)
    for slice_index, slice in enumerate(slices): 

        root_count = sum([
            1
            for token
            in slice
            if type(token) == Root
        ])

        assert root_count <= 1

        for index, item in enumerate(slice):
            if item == "-":
                pass
            elif item == "#":
                assert False
            else:
                if verbose:
                    print(f"now spelling out {item.label} terminal with values {item.values}")
                matching_vis = [
                    vi
                    for vi
                    in vocabulary_items
                    if (
                            vi.label == item.label
                        and vi.values.issubset(item.values)
                    )
                ]

                if len(matching_vis) == 0:
                    selected_vi = None
                else:
                    super_matches = [
                        vi 
                        for vi
                        in matching_vis
                        if ((vi.pronunciation in item.values) and (len(vi.triggers) == 0)) or (vi.diacritic in item.values) #learner 2 non-Root-word terminals never have super matches! in contrast to gender diacritics being obligatorily used in learner 1
                    ]

                    if len(super_matches) > 0:
                        selected_vi = random.choices(
                            population=super_matches,
                            weights=[
                                match.weight + DIACRITIC_BONUS * len([value for value in item.values if (("+" not in value) and ("-" not in value)) and ((value == match.diacritic) or (value == match.pronunciation))]) #TODO: i think this is now adding a bonus if the terminal has any pronunciation diacritics OR learner-1-only gender features (not +/-). AND (that value is the match's diacritic (learner 1 style gender feature was used) OR that value is the match's pronunciation (decl diacritic was used))
                                for match #should mean the nominalizer VIs w/ and w/o gender values just have base weight to be chosen
                                in super_matches
                            ]
                        )[0] 
                        if selected_vi.pronunciation in item.values and verbose:
                            print(f"we picked {selected_vi.diacritic} bc its pronunciation was locally triggered")
                        elif selected_vi.diacritic in item.values and verbose:
                            print(f"we picked {selected_vi.diacritic} bc its pronunciation was triggered at a distance by a n-borne gender feature")
                    else:
                        weights = []
                        for match in matching_vis:
                            weights.append(
                                (
                                    match.weight 
                                    / 
                                    sum(
                                        vi.weight 
                                        for vi 
                                        in matching_vis 
                                        if len(vi.values) == len(match.values)
                                    )
                                ) 
                                + 
                                MORE_SPECIFIC_BONUS 
                                * 
                                len(match.values)
                                )

                        # max_n_values = max(len(vi.values) for vi in matching_vis) #3
                        # min_n_values = min(len(vi.values) for vi in matching_vis) #0
                        # # min_weight_max_n_values = min(vi.weight for vi in matching_vis if len(vi.values) == max_n_values)
                        # weights = [] 
                        # if max_n_values != min_n_values:
                        #     if max_n_values - min_n_values == 1:
                        #         if (max(vi.weight for vi in matching_vis if len(vi.values) == max_n_values) < max(vi.weight for vi in matching_vis if len(vi.values) == (max_n_values - 1) )):
                        #             for match in matching_vis:
                        #                 if len(match.values) == min_n_values:
                        #                     weights.append(match.weight + MORE_SPECIFIC_BONUS * len(match.values))
                        #                 elif len(match.values) == min_n_values + 1:
                        #                     weights.append(match.weight * ((max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values))/(max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values + 1))) + MORE_SPECIFIC_BONUS * len(match.values) )
                        #                 else:
                        #                     assert False
                        #     elif max_n_values - min_n_values == 2:
                        #         if (
                        #             max(vi.weight for vi in matching_vis if len(vi.values) == max_n_values) < max(vi.weight for vi in matching_vis if len(vi.values) == (max_n_values - 1) )
                        #             or
                        #             (max(vi.weight for vi in matching_vis if len(vi.values) == max_n_values) < max(vi.weight for vi in matching_vis if len(vi.values) == (max_n_values - 2) ))
                        #         ):
                        #             for match in matching_vis:
                        #                 if len(match.values) == min_n_values:
                        #                     weights.append(match.weight + MORE_SPECIFIC_BONUS * len(match.values))
                        #                 elif len(match.values) == min_n_values + 1:
                        #                     weights.append(match.weight * ((max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values))/(max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values + 1))) + MORE_SPECIFIC_BONUS * len(match.values) )
                        #                 elif len(match.values) == min_n_values + 2:
                        #                     weights.append(match.weight + MORE_SPECIFIC_BONUS * len(match.values) )
                        #                 else:
                        #                     assert False
                        #     elif max_n_values - min_n_values == 3:
                        # else: 

                        # for match in matching_vis:
                        #     if len(match.values) == min_n_values:
                        #         weights.append(match.value)
                        #     elif len(match.values) == min_n_values + 1:
                        #         weights.append(match.value * ((max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values))/(max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values + 1))) + MORE_SPECIFIC_BONUS * len(match.values) )

                        # weights = []
                        # while max_n_values != min_n_values:
                        #     max_weight_smaller_n_values = max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values)
                        #     min_weight_larger_n_values = min(vi.weight for vi in matching_vis if len(vi.values) == max_n_values)
                        #     for match in matching_vis:
                        #         if len(match.values) == min_n_values + 1:
                        #             weights.append(match.value * (max_weight_smaller_n_values / min_weight_larger_n_values))
                        #     min_n_values+=1

                        #
                        # if (
                        #     max_n_values != min_n_values 
                        #     and 
                        #     min_weight_max_n_values < max(vi.weight for vi in matching_vis if len(vi.values) == min_n_values) #(max_n_values - 1)
                        #     ):
                        #     print("hm!")
                        # else: 
                        #     weights = [match.weight for match in matching_vis]
                        selected_vi = random.choices(
                            population=matching_vis,
                            weights=weights
                        )[0]
                        if verbose:
                            print(f"we picked {selected_vi.diacritic}: no super match (neither decl nor L1-gender)")
                    
                    vis_used.append(selected_vi)

                if selected_vi == None or selected_vi.pronunciation == "null":
                    if selected_vi == None or len(selected_vi.triggers) == 0:    
                        if index < len(slice) - 1:
                            assert slice[index+1] == "-"
                            assert slice[index+2] != "-"
                            
                            #pass on triggers (just pronunciation string) if you are null and have no triggers of your own...or if nothing got inserted at this terminal
                            for value in item.values:
                                for vi in vis_used:
                                    for trigger in vi.triggers:
                                        if value == trigger[0] and len(trigger[1]) > 0: #i think, without the 2nd half of if conditional, this would pass along its own trigger if it was triggered (null nominalizer)...always trigger null sg/pl???
                                            slice[index+2].values.add(value) 

                else:
                    full_pronunciation += selected_vi.pronunciation

                if selected_vi != None and len(selected_vi.triggers) > 0:
                    assert root_count == 1
                    if index < len(slice) - 1:
                        assert slice[index+1] == "-"
                        assert slice[index+2] != "-"
                        for (trigger_pron, trigger_values) in selected_vi.triggers:
                            if trigger_values.issubset(set().union(*[terminal.values for terminal in slice if terminal != '-'])):
                                slice[index+2].values.add(trigger_pron)

        if slice_index < len(slices) - 1:
            full_pronunciation += "#"

    return full_pronunciation, vis_used 
    

def sprout_nodes(terminal_chain, sprouting_rules, affix, learner_version):
    sprouting_rules_used = []

    for terminal in terminal_chain.linear:
        if learner_version == 1:
            weights = [
                rule.weight
                if (
                    hasattr(terminal, "values")
                    and hasattr(terminal, "label")
                    and terminal.label == rule.trigger_label
                    and {value for value in terminal.values if value[0] in ["+", "-"]} == rule.trigger_values #why was it {value for value in terminal.values if value[0] in ["+", "-"]}.issubset(rule.trigger_values)??
                    and rule.trigger_diacritic in terminal.values
                ) 
                else 0
                for rule 
                in sprouting_rules
            ]

        elif learner_version == 2:
            weights = [
                rule.weight
                if (
                    hasattr(terminal, "values")
                    and hasattr(terminal, "label")
                    and terminal.label == rule.trigger_label
                    and {value for value in terminal.values if value[0] in ["+", "-"]} == rule.trigger_values 
                )
                else 0
                for rule 
                in sprouting_rules
            ]
        
        if sum(weights) != 0:
            rule_used = random.choices(population=sprouting_rules, weights=weights)[0]
            sprouted_agr = AgrTerminal(values=terminal.values)
            terminal.values = rule_used.keep_values
            sprouting_rules_used.append(rule_used)

            if affix == "suffixing":
                terminal_chain = insert_into_linear(
                    terminal_chain=terminal_chain,
                    terminal=terminal,
                    affix=affix,
                    new_linear=("-", sprouted_agr)
                )
            elif affix == "prefixing":
                terminal_chain = insert_into_linear(
                    terminal_chain=terminal_chain,
                    terminal=terminal,
                    affix=affix,
                    new_linear=(sprouted_agr, "-")
                )
            else:
                assert False      

    return terminal_chain, sprouting_rules_used


def insert_into_linear(terminal_chain, terminal, affix, new_linear):

    terminal_chain = copy.deepcopy(terminal_chain)

    index = terminal_chain.linear.index(terminal)

    if affix == "suffixing":
        terminal_chain.linear = (
              terminal_chain.linear[:index+1]
            + new_linear
            + terminal_chain.linear[index+1:]
        )
    elif affix == "prefixing":
        terminal_chain.linear = (
              terminal_chain.linear[:index]
            + new_linear
            + terminal_chain.linear[index:]
        )
    else:
        assert False

    return terminal_chain


def combine_nominalizers_l1(nominalizer_used, nominalizer_vi_used, nominalizers, vocabulary_items):
    overlap_list = [
        nom
        for nom
        in nominalizers
        if (len(nom.selectional.intersection(nominalizer_used.selectional)) > 1 #to prevent weird edge cases?
            and
            len(nom.values) > 0
            and
            nom.weight > 0
            and
            len(set().union(*[set().union(*[v.values for v in vocabulary_items if v.diacritic == value]) for value in nom.values]).intersection(set().union(*[set().union(*[v.values for v in vocabulary_items if v.diacritic == value]) for value in nominalizer_used.values]))) == 0
            ) # and no overlap in values of vis whose diacritics they bear! Also stops it from trying to combine with itself or supersets of itself (noms with a superset of its values)
    ]

    for nom in overlap_list:
        print(f"..plus that nominalizer selected (some of) the same Roots as the nominalizer with {nom.values} as values: {nom.selectional.intersection(nominalizer_used.selectional)}")
        nominalizers = create_nominalizer_given_selectional(
            values = nom.values.union(nominalizer_used.values),
            selectional = nom.selectional.intersection(nominalizer_used.selectional),
            existing_nominalizers=nominalizers,
            combining = True)
        
        print(f"..so we'll also combine the vis that spell out {nom.values}")
        
        vis_to_combine = select_vis_to_combine(vocabulary_items=vocabulary_items, nominalizer_vi_used=nominalizer_vi_used, nom_being_considered = nom)

        for vi in vis_to_combine:
            is_new, combined_vi, vocabulary_items = create_vi(
                pronunciation="null",
                label="nominalizer",
                values=vi.values.union(nominalizer_vi_used[0].values),
                triggers=vi.triggers.union(nominalizer_vi_used[0].triggers),
                vocabulary_items=vocabulary_items,
                redo_bonus=True
            )
            if is_new:
                # assert 
                print(f"....made the new vi: {combined_vi.big_string()}")

    return nominalizers, vocabulary_items


def combine_nominalizer_vis_l2(nominalizer_used, nominalizer_vi_used, nominalizers, vocabulary_items):
    full_match_list = [
        vi
        for vi
        in vocabulary_items
        if (
            vi.label == "nominalizer"
            and
            vi.values == nominalizer_used.values
            and
            vi.pronunciation == "null"
            and 
            vi.diacritic != nominalizer_vi_used[0].diacritic
            and # either there are no overlaps in what the triggered VIs spell out (i.e. don't put two triggers for diff +atomic exponents together)
            ((len({trigger[1] for trigger in vi.triggers}.intersection(trigger[1] for trigger in nominalizer_vi_used[0].triggers)) == 0) 
            or  # or the only overlap is frozenset() i.e. the trigger in common is for the null empty triggers nominalizer (shouldn't arise, since noms only have triggers for meaningful items)
            ({trigger[1] for trigger in vi.triggers}.intersection(trigger[1] for trigger in nominalizer_vi_used[0].triggers) == {frozenset()}))
            and 
            vi.weight > FLOOR_WEIGHT
        )
    ]
    
    for vi in full_match_list:
        is_new, combined_vi, vocabulary_items = create_vi(
            pronunciation="null",
            label="nominalizer",
            values=nominalizer_used.values,
            triggers=vi.triggers.union(nominalizer_vi_used[0].triggers),
            vocabulary_items=vocabulary_items,
            redo_bonus=True
        )
        if is_new:
            # assert 
            print(f"....made the new vi: {combined_vi.big_string()}")

    return nominalizers, vocabulary_items


def print_nominalizers(nominalizers, roots):
    sorted_roots = sorted(roots, key = lambda x: x.label)
    sorted_nominalizers = sorted(nominalizers, key = lambda x: x.weight, reverse=True)
    
    with open("./outputs/nominalizers.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Values", "Weight"] + [root.label for root in sorted_roots])

        for nominalizer in sorted_nominalizers:
            writer.writerow(
                [nominalizer.values, nominalizer.weight] 
                + 
                [
                    1 
                    if root.label in nominalizer.selectional 
                    else 0
                    for root 
                    in sorted_roots
                ]
            )


def print_items(items, func, file_name, headers):
    with open(f"./outputs/{file_name}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for item in items:
            writer.writerow(func(item))


def add_to_dicts(
    nominalizer_dicts, 
    semantic_terminal_dicts, 
    sprouting_rule_dicts, 
    vi_dicts,
    nominalizers,
    semantic_terminals,
    sprouting_rules,
    vocabulary_items,
    input_num
):
    
    def dict_helper(dicts, items, input_num, func):
        for item in items:
            if dicts.get(func(item)) is None:
                dicts[func(item)] = {}
            
            dicts[func(item)][input_num] = item.weight
    
        return dicts

    nominalizer_dicts = dict_helper(nominalizer_dicts, nominalizers, input_num, lambda x: f"{x.values}")
    semantic_terminal_dicts = dict_helper(semantic_terminal_dicts, semantic_terminals, input_num, lambda x: f"{x.values} - {x.selection_strength}")
    sprouting_rule_dicts = dict_helper(sprouting_rule_dicts, sprouting_rules, input_num, lambda x: f"{x.trigger_values} - {x.trigger_label} - {x.trigger_diacritic}")
    vi_dicts = dict_helper(vi_dicts, vocabulary_items, input_num, lambda x: f"{x.diacritic}")

    return nominalizer_dicts, semantic_terminal_dicts, sprouting_rule_dicts, vi_dicts
            

def print_weights(dicts, end_index, file_name):

    items = list(dicts.keys())

    with open(f"./outputs/{file_name}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Line"] + items)

        for index in range(end_index):
            writer.writerow(
                [index] 
                + 
                [
                    dicts[item].get(index, "")
                    for item 
                    in items
                ]
            )


def test(
        gender_trial, test_and_learn, verbose,
        roots, nominalizer_terminals, values, semantic_terminals,
        adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
        line_index, nominalizer_dicts, 
        semantic_terminal_dicts, 
        sprouting_rule_dicts, 
        vi_dicts,
        vocabulary_items, all_roots, affix
):
    if gender_trial is not None:
        print(f"we are now trying with gender_trial {gender_trial}")
        numer_values = values + [gender_trial]
        # \sout{values.append(gender_trial)} <- will cause doubling of gender features, causing select_numeration to fail
    else:
        numer_values = values

     # Select numeration
    while True:
        numeration, terminals_used = select_numeration(
            roots=roots,
            nominalizer_terminals=nominalizer_terminals,
            values=numer_values,
            semantic_terminals=semantic_terminals,
            adjectivalizer=adjectivalizer,
            phase = "test",
            test_and_learn=test_and_learn,
            learner_version=learner_version, 
            verbose = verbose
        )
        
        terminal_chain = derive_terminal_chain(numeration=numeration, affix=affix)

        # debug_print(verbosity_level, 2, f"TerminalChain linear: {terminal_chain.linear}")

        if input_string.count("#") == terminal_chain.linear.count("#"):
            if verbose:
                debug_print(verbosity_level, 2, "we broke out")
            break
    
        if verbose:
            debug_print(verbosity_level, 2, "we failed")
        #TURNED OFF
        # for terminal in terminals_used:
        #     terminal.weight -= UPDATE_TERMINAL_WEIGHT
    
    # Do node sprouting
    terminal_chain, sprouting_rules_used = sprout_nodes(
        terminal_chain=terminal_chain,
        sprouting_rules=sprouting_rules,
        affix=affix,
        learner_version=learner_version
    )

    if verbose:
        debug_print(verbosity_level, 2, f"we used sprouting_rules: {sprouting_rules_used}")
        debug_print(verbosity_level, 2, f"now we have this TerminalChain: {terminal_chain.linear}")

    # Insert Vis
    full_pronunciation, vis_used = insert_vi(
        terminal_chain=terminal_chain, 
        vocabulary_items=vocabulary_items,
        verbose=verbose
    )

    debug_print(verbosity_level, 2, f"input pronunciation: {input_string}")
    debug_print(verbosity_level, 2, f"full_pronunciation: {full_pronunciation}")
    if verbose:
        debug_print(verbosity_level, 2, f"vis_used: {[vi.diacritic for vi in vis_used]}")

    nominalizers_used = [
            terminal
            for terminal
            in terminals_used
            if type(terminal) == NominalizerTerminal
        ]

    assert len(nominalizers_used) == 1

    nominalizer_used = nominalizers_used[0]

    nominalizer_vi_used = [vi for vi in vis_used if vi.label == "nominalizer"]

    successful_nominalizer = False

    if test_and_learn == "just_test":
        if full_pronunciation == input_string.replace("-", "").replace("null", ""):
            success = True
            if learner_version == 1:
                #if a value of the nominalizer was relevant for spelling out...by triggering the diacritic of a vi!
                if len(nominalizer_used.values.intersection({vi.diacritic for vi in vis_used})) > 0: 
                    successful_nominalizer = True # not used for learner1
            if learner_version == 2:
                #if the gender value of the nominalizer was relevant for spelling out...by being used in one of the non-nom VIs (i.e. Agr, hopefully)!
                if len(nominalizer_used.values.intersection(set().union(*[vi.values for vi in vis_used if vi.label != "nominalizer"]))) > 0: 
                    successful_nominalizer = True # is a condition on adding gender_trial to gender_dict!!!
        else:
            success = False


    elif test_and_learn == "test_and_learn":
        if full_pronunciation == input_string.replace("-", "").replace("null", ""):

            debug_print(verbosity_level, 2, f"Successful derivation!")
            success = True

            #update nominalizer inventory, specific to learner_version:

            #update nominalizer inventory: add Root to nom, and/or combine nominalizers that share Roots in their selectionals
            if learner_version == 1:
                #if a value of the nominalizer was relevant for spelling out...by triggering the diacritic of a vi!
                if len(nominalizer_used.values.intersection({vi.diacritic for vi in vis_used})) > 0: 
                    debug_print(verbosity_level, 2, f"Since it worked, and the nominalizer's value(s) contributed to spellout (was a diacritic in vis_used), let's add {roots[0]} to the selectional of the nominalizer whose values are {nominalizer_used.values}")
                    successful_nominalizer = True # not used for learner1
                    debug_print(verbosity_level, 2, f"Before changes, that nominalizer was {nominalizer_used.big_string()}")
                    nominalizer_terminals = create_nominalizer(
                        root=roots[0], 
                        values=nominalizer_used.values, 
                        existing_nominalizers=nominalizer_terminals,
                        learner_version=learner_version
                    ) #make sure current Root is selected for by that successful nominalizer

                    nominalizer_terminals, vocabulary_items = combine_nominalizers_l1(
                        nominalizer_used = nominalizer_used,
                        nominalizer_vi_used = nominalizer_vi_used,
                        nominalizers = nominalizer_terminals,
                        vocabulary_items=vocabulary_items
                    ) #combine nominalizers that share Roots, and combine corresponding VIs for those nominalizers

            #update nominalizer inventory: add Root to gendered nom, and/or combine VIs (triggers on) for same gender nominalizer 
            if learner_version == 2:
                #if the gender value of the nominalizer was relevant for spelling out...by being used in one of the non-nom VIs (i.e. Agr, hopefully)!
                if len(nominalizer_used.values.intersection(set().union(*[vi.values for vi in vis_used if vi.label != "nominalizer"]))) > 0: 
                    successful_nominalizer = True # is a condition on adding gender_trial to gender_dict!!!
                    debug_print(verbosity_level, 2, f"Since it worked, and the nominalizer's value(s) contributed to spellout (was a diacritic in vis_used), let's add {roots[0]} to the selectional of the nominalizer whose values are {nominalizer_used.values}")
                    debug_print(verbosity_level, 2, f"Before changes, that nominalizer was {nominalizer_used.big_string()}")
                    nominalizer_terminals = create_nominalizer(
                        root=roots[0], 
                        values=nominalizer_used.values, 
                        existing_nominalizers=nominalizer_terminals,
                        learner_version=learner_version
                    ) #make sure current Root is selected for by that successful nominalizer

                nominalizer_terminals, vocabulary_items = combine_nominalizer_vis_l2( 
                    nominalizer_used = nominalizer_used,
                    nominalizer_vi_used = nominalizer_vi_used,
                    nominalizers = nominalizer_terminals,
                    vocabulary_items=vocabulary_items
                ) #combine nominalizer VIs for same values, across inflectional space (as long as no overlap, i.e. only one each of +atomic, -atomic)
                
                
            # these can be learner 1 or learner 2: if you're successful, reward everything (in addition, in learner2, to writing down your uninterpretable gender feature)

            #reward terminals
            for terminal in terminals_used:
                terminal.weight += UPDATE_TERMINAL_WEIGHT
            
            #reward sprouting rules
            for rule in sprouting_rules_used:
                rule.weight += UPDATE_SPROUTING_RULE_WEIGHT

            #reward vis
            if successful_nominalizer: #BIG TBD: would stem how genderless VIs seem to pull ahead of gendered Agr VIs in learner 2? would not diff between 1-gender-diacritic and 2-gender-diacritic VIs in learner 1...but the isolation of redo-bonus to combine_nom_l1() seems to be working to help those pull ahead
                for vi in vis_used:
                    print(f"now increasing weight of {vi.big_string()}")
                    vi.weight += UPDATE_SUCCESS_WEIGHT 
                    _, vocabulary_items = compare_vi( #TODO: is the call to compare_vi enough (to combine diacritics across contexts on Vis)? \sout{prob not for learner 1, so we have combine_nominalizer action too}. #TODO: how does this work for sem gender learner 2 noms? doesn't apply, I think. so this call to compare_vis() is prob not enough alone for learner 2 either?
                        vocabulary_item=vi,
                        vocabulary_items=vocabulary_items
                    )

        else:
            success = False
            debug_print(verbosity_level, 2, f"Failure")

            
            if gender_trial is None: #so we can decrement for failures if you're a semantic core item; if you had uninterpretable gender added already; or if you are in learner 1. yes!

                #TURNED OFF
                # for terminal in terminals_used:
                #     terminal.weight -= UPDATE_TERMINAL_WEIGHT
                
                #TURNED OFF
                # for rule in sprouting_rules_used:
                #     rule.weight -= UPDATE_SPROUTING_RULE_WEIGHT

                for vi in vis_used:
                    print(f"now decrementing weight of {vi.big_string()}")
                    vi.weight = max(FLOOR_WEIGHT, vi.weight - UPDATE_TERMINAL_WEIGHT)

        debug_print(verbosity_level, 2, f"line done")

        (
            nominalizer_dicts, 
            semantic_terminal_dicts, 
            sprouting_rule_dicts, 
            vi_dicts
        ) = add_to_dicts(
            nominalizer_dicts=nominalizer_dicts, 
            semantic_terminal_dicts=semantic_terminal_dicts, 
            sprouting_rule_dicts=sprouting_rule_dicts, 
            vi_dicts=vi_dicts,
            nominalizers=nominalizer_terminals,
            semantic_terminals=semantic_terminals,
            sprouting_rules=sprouting_rules,
            vocabulary_items=vocabulary_items,
            input_num=line_index
        )

        # print outputs
        print_nominalizers(nominalizers=nominalizer_terminals, roots=all_roots)
        
        print_items(
            items=sprouting_rules,
            func=lambda x: [x.trigger_label, x.trigger_values, x.trigger_diacritic, x.keep_values, x.weight],
            file_name="sprouting_rules",
            headers=["trigger_label", "trigger_values", "trigger_diacritic", "keep_values", "weight"]
        )

        print_items(
            items=vocabulary_items,
            func=lambda x: [x.diacritic, x.pronunciation, x.label, x.values, x.triggers, x.weight],
            file_name="vocabulary_items",
            headers=["diacritic", "pronunciation", "label", "values", "triggers", "weight"]
        )


        print_weights(dicts=nominalizer_dicts, end_index=line_index, file_name="nominalizer_weights")
        print_weights(dicts=semantic_terminal_dicts, end_index=line_index, file_name="semantic_weights")
        print_weights(dicts=sprouting_rule_dicts, end_index=line_index, file_name="sprouting_weights")
        print_weights(dicts=vi_dicts, end_index=line_index, file_name="vi_weights")

    return (
        success, successful_nominalizer, 
        full_pronunciation, vis_used, nominalizer_used, 
        roots, nominalizer_terminals, values, semantic_terminals,
        adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
        line_index, nominalizer_dicts, 
        semantic_terminal_dicts, 
        sprouting_rule_dicts, 
        vi_dicts,
        vocabulary_items
    )


#toy data
# def run(
#     input_file_path="./data/input/toy/toy-italian-classes-proportional.txt",
#     root_file_path="./data/roots/toy-italian-classes-roots.txt",
#     test_only_file_path="",
#     learner_version=1,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

# def run(
#     input_file_path="./data/input/toy/toy-italian-classes-proportional-gender.txt",
#     root_file_path="./data/roots/toy-italian-classes-roots-mostly.txt",
#     test_only_file_path="",
#     learner_version=2,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

# def run(
#     input_file_path="./data/input/toy/toy-same-root-nominals-mostly-l1.txt",
#     root_file_path="./data/roots/toy-italian-classes-roots-mostly.txt",
#     test_only_file_path="./data/input/toy/toy-test-mostly-l1.txt",
#     learner_version=1,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

# def run(
#     input_file_path="./data/input/toy/toy-same-root-nominals-mostly.txt",
#     root_file_path="./data/roots/toy-italian-classes-roots-mostly.txt",
#     test_only_file_path="./data/input/toy/toy-test-mostly-l2.txt",
#     learner_version=2,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

#real data, shortened (for testing)
# def run(
#     input_file_path="./data/learner1_input_dn_final_regularized_plus_togeneralize-short-for-testing.txt",
#     root_file_path="./data/roots/tonelli-ROOTS-plus.txt",
#     test_only_file_path="./data/test-only-seen.txt",
#     generate_unseen_file_path="./data/test-not-seen.txt", 
#     learner_version=1,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

# def run(
#     input_file_path="./data/learner2_input_dn_final_regularized_plus_togeneralize-short-for-testing.txt", 
#     root_file_path="./data/roots/tonelli-ROOTS-plus.txt",
#     test_only_file_path="./data/test-only-seen-gender.txt", 
#     generate_unseen_file_path="./data/test-not-seen-gender.txt",
#     learner_version=2,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

#real data
def run(
    input_file_path="./data/learner1_input_dn_final_regularized_plus_togeneralize.txt",
    root_file_path="./data/roots/tonelli-ROOTS-plus.txt",
    test_only_file_path="./data/test-only-seen.txt",
    generate_unseen_file_path="./data/test-not-seen.txt", 
    learner_version=1,
    affix = "suffixing",
    verbosity_level = 2,
):

# def run(
#     input_file_path="./data/learner2_input_dn_final_regularized_plus_togeneralize.txt", 
#     root_file_path="./data/roots/tonelli-ROOTS-plus.txt",
#     test_only_file_path="./data/test-only-seen-gender.txt", 
#     generate_unseen_file_path="./data/test-not-seen-gender.txt",
#     learner_version=2,
#     affix = "suffixing",
#     verbosity_level = 2,
# ):

    assert learner_version in [1, 2]

    sys.stdout = open('./outputs/output.txt', 'w')

    random.seed(1234)

    # initialize state

    with open(root_file_path,'r') as root_file:
        all_roots = [Root(label=label) for label in root_file.read().splitlines()]

    # if verbosity_level == 3:
    #     for root in all_roots:
    #         print(root.big_string())

    semantic_terminals = create_semantic_terminals(learner_version=learner_version)

    if verbosity_level == 3:
        for ST in semantic_terminals:
            print(ST.big_string())


    # store state

    if learner_version == 1:
        nominalizer_terminals = []
    elif learner_version == 2:
        nominalizer_terminals = create_initial_nominalizers()
    else:
        assert False

    adjectivalizer = AdjectivalizerTerminal()
    sprouting_rules = []
    vocabulary_items = []

    # store weights as we go

    nominalizer_dicts = {}
    semantic_terminal_dicts = {}
    sprouting_rule_dicts = {}
    vi_dicts = {}
    gender_dict = {}

    # learn!

    with open(input_file_path,'r') as learningDataFile:
        learningDataString = learningDataFile.read().splitlines()

    with open(test_only_file_path,'r') as toTestFile: 
        testDataString = toTestFile.read().splitlines()

    with open(generate_unseen_file_path,'r') as generateUnseenFile: 
        unseenDataString = generateUnseenFile.read().splitlines()
    n_items_togenerate = len(unseenDataString) #learner 2 -> 11 ; learner 1 -> 6
    
    # random.shuffle(learningDataString) #just for toy datasets

    for line_index, line in enumerate(learningDataString):
        input_string, values = parse_input(line)
        roots = find_roots(input_string)
        
        if verbosity_level >= 2:
            print(f"\n\n------------------------------\n------------------------------")
            print(f"------------------------------\n input line #{line_index} \n------------------------------")
            print(f"input roots: {roots}")
            print(f"input values: {values}")

        if len(nominalizer_terminals) == 0:
            assert learner_version == 1

            create_nominalizer(
                roots[0],
                values=set(),
                existing_nominalizers=nominalizer_terminals,
                learner_version=learner_version
            )

            is_new, null_nom, vocabulary_items = create_vi(
                pronunciation="null",
                label="nominalizer",
                values=set(),
                triggers = set(),
                vocabulary_items=vocabulary_items,
                redo_bonus=False 
            )

            for nom1 in nominalizer_terminals:
                print(f"made our very first nominalizer: {nom1.big_string()}")

        
        # PART ONE: Process and Generate Hypotheses
        
        # learner 2 only: insert uninterpretable gender to context set 

        if learner_version == 2:
            if roots[0] in gender_dict:
                print(f"we already assigned an uninterpretable {gender_dict[roots[0]]} gender to this root {roots[0].label}")
                numer_values = values + [gender_dict[roots[0]]]
            else:
                numer_values = values
        else:
            numer_values = values
        # \sout{if learner_version == 2:
        #     if roots[0] in gender_dict: 
        #         values.append(gender_dict[roots[0]]) } #this was persisting throughout Part 1 through to Part 2 (when testing)
        

        # create numeration

        while True:
            numeration, terminals_used = select_numeration(
                roots=roots,
                nominalizer_terminals=nominalizer_terminals,
                values=numer_values, # note! making a terminal chain from the original values PLUS gender_dict uninterpretable gender value if there is one
                semantic_terminals=semantic_terminals,
                adjectivalizer=adjectivalizer,
                phase = "process",
                test_and_learn="process",
                learner_version=learner_version,
                verbose = True
            )
            
            terminal_chain = derive_terminal_chain(numeration=numeration, affix=affix)

            # debug_print(verbosity_level, 2, f"TerminalChain linear: {terminal_chain.linear}")

            if input_string.count("#") == terminal_chain.linear.count("#"):
                debug_print(verbosity_level, 2, "we broke out")
                break
        
            debug_print(verbosity_level, 2, "we failed")
            #TURNED OFF
            # for terminal in terminals_used:
            #     terminal.weight -= UPDATE_TERMINAL_WEIGHT


        # generate vis from input

        vocabulary_items, nominalizer_terminals, sprouting_rules = generate_vi(
            terminal_chain=terminal_chain,
            input_string=input_string,
            roots=roots,
            vocabulary_items=vocabulary_items,
            nominalizers=nominalizer_terminals,
            sprouting_rules=sprouting_rules,
            affix=affix,
            learner_version=learner_version
        )
        print("------------------------------")
        print("------------------------------\n done processing input, time to test \n------------------------------")

        # debug_print(verbosity_level, 2, f"vocabulary_items: {vocabulary_items}")
        # debug_print(verbosity_level, 2, f"nominalizer_terminals: {nominalizer_terminals}")
        # debug_print(verbosity_level, 2, f"sprouting_rules: {sprouting_rules}")


        # PART TWO: Test Derivation
        # add gender

        test_args = {
            "roots": roots, "nominalizer_terminals": nominalizer_terminals, "values": values,
            "semantic_terminals": semantic_terminals, "adjectivalizer": adjectivalizer,
            "learner_version": learner_version, "input_string": input_string,
            "verbosity_level": verbosity_level, "sprouting_rules": sprouting_rules,
            "line_index": line_index, "nominalizer_dicts": nominalizer_dicts, 
            "semantic_terminal_dicts": semantic_terminal_dicts, 
            "sprouting_rule_dicts": sprouting_rule_dicts, "vi_dicts": vi_dicts,
            "vocabulary_items": vocabulary_items, "all_roots": all_roots, "affix": affix
        }

        if learner_version == 1:
            (
                _, _, 
                _, _, _,
                roots, nominalizer_terminals, values, semantic_terminals,
                adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
                line_index, nominalizer_dicts, 
                semantic_terminal_dicts, 
                sprouting_rule_dicts, 
                vi_dicts,
                vocabulary_items
            ) = test(gender_trial=None, test_and_learn="test_and_learn", verbose = True, **test_args)
            
        elif learner_version == 2:
            #if you are not in the semantic core and have neither semantic +feminine nor -feminine in your context values
            if {"+feminine"} not in values and {"-feminine"} not in values:
                print("not in the semantic core?")
                #you might have an uninterpretable feature listed. if you don't, we need to figure out which one to add!
                #first, try a derivation with +feminine:
                if roots[0] not in gender_dict:
                    (
                        success, successful_nominalizer, 
                        _, _, _,
                        roots, nominalizer_terminals, values, semantic_terminals,
                        adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
                        line_index, nominalizer_dicts, 
                        semantic_terminal_dicts, 
                        sprouting_rule_dicts, 
                        vi_dicts,
                        vocabulary_items
                    ) = test(gender_trial={"+feminine"}, test_and_learn="test_and_learn", verbose = True, **test_args)

                    #if that fails, then try a derivation with -feminine:
                    if success == False:
                        test_args = {
                            "roots": roots, "nominalizer_terminals": nominalizer_terminals, "values": values,
                            "semantic_terminals": semantic_terminals, "adjectivalizer": adjectivalizer,
                            "learner_version": learner_version, "input_string": input_string,
                            "verbosity_level": verbosity_level, "sprouting_rules": sprouting_rules,
                            "line_index": line_index, "nominalizer_dicts": nominalizer_dicts, 
                            "semantic_terminal_dicts": semantic_terminal_dicts, 
                            "sprouting_rule_dicts": sprouting_rule_dicts, "vi_dicts": vi_dicts,
                            "vocabulary_items": vocabulary_items, "all_roots": all_roots, "affix": affix
                        }

                        (
                            success, successful_nominalizer, 
                            _, _, _,
                            roots, nominalizer_terminals, values, semantic_terminals,
                            adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
                            line_index, nominalizer_dicts, 
                            semantic_terminal_dicts, 
                            sprouting_rule_dicts, 
                            vi_dicts,
                            vocabulary_items
                        ) = test(gender_trial={"-feminine"}, test_and_learn="test_and_learn", verbose = True, **test_args)

                        if success == True and successful_nominalizer == True: # add only if the root was added to the -fem nominalizer's selectional in test
                            print(f"now adding {roots[0]} with -feminine to gender_dict")
                            gender_dict[roots[0]] = {"-feminine"}
                            
                    elif success == True and successful_nominalizer == True: # add only if the root was added to the +fem nominalizer's selectional in test
                        gender_dict[roots[0]] = {"+feminine"}
                        print(f"now adding {roots[0]} with +feminine to gender_dict")
                        
                else:
                    print(f"in test: adding the uninterpretable {gender_dict[roots[0]]} gender we already assigned to this root {roots[0].label}")
                    values_w_uninterp_added = values + [gender_dict[roots[0]]] 
                    #not necessary
                    # \sout{unique_values = []
                    # for value in values_w_uninterp_added:
                    #     if value not in unique_values:
                    #         unique_values.append(value)
                    # if values_w_uninterp_added != unique_values:
                    #     print("debug: should never get here") }

                    test_args = {
                        "roots": roots, "nominalizer_terminals": nominalizer_terminals, "values": values_w_uninterp_added,
                        "semantic_terminals": semantic_terminals, "adjectivalizer": adjectivalizer,
                        "learner_version": learner_version, "input_string": input_string,
                        "verbosity_level": verbosity_level, "sprouting_rules": sprouting_rules,
                        "line_index": line_index, "nominalizer_dicts": nominalizer_dicts, 
                        "semantic_terminal_dicts": semantic_terminal_dicts, 
                        "sprouting_rule_dicts": sprouting_rule_dicts, "vi_dicts": vi_dicts,
                        "vocabulary_items": vocabulary_items, "all_roots": all_roots, "affix": affix
                    }

                    (
                        _, _, 
                        _, _, _,
                        roots, nominalizer_terminals, values, semantic_terminals,
                        adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
                        line_index, nominalizer_dicts, 
                        semantic_terminal_dicts, 
                        sprouting_rule_dicts, 
                        vi_dicts,
                        vocabulary_items
                    ) = test(gender_trial=None, test_and_learn="test_and_learn", verbose = True, **test_args)
            #else = you do have +feminine or -feminine in your values already: you're a semantic core item
            else:
               (
                    _, _, 
                    _, _, _,
                    roots, nominalizer_terminals, values, semantic_terminals,
                    adjectivalizer, learner_version, input_string, verbosity_level, sprouting_rules,
                    line_index, nominalizer_dicts, 
                    semantic_terminal_dicts, 
                    sprouting_rule_dicts, 
                    vi_dicts,
                    vocabulary_items
                ) = test(gender_trial=None, test_and_learn="test_and_learn", verbose = True, **test_args) 

        debug_print(verbosity_level, 2, f"line done")

        (
            nominalizer_dicts, 
            semantic_terminal_dicts, 
            sprouting_rule_dicts, 
            vi_dicts
        ) = add_to_dicts(
            nominalizer_dicts=nominalizer_dicts, 
            semantic_terminal_dicts=semantic_terminal_dicts, 
            sprouting_rule_dicts=sprouting_rule_dicts, 
            vi_dicts=vi_dicts,
            nominalizers=nominalizer_terminals,
            semantic_terminals=semantic_terminals,
            sprouting_rules=sprouting_rules,
            vocabulary_items=vocabulary_items,
            input_num=line_index
        )

        # PART THREE:
        if (line_index / N_OBSERVATIONS_CHECKPOINT < 3 and line_index % N_OBSERVATIONS_CHECKPOINT == 0 and line_index != 0) or line_index == len(learningDataString) - 1 - n_items_togenerate:
            for test_only_line_index, test_only_line in enumerate(testDataString):
                test_only_input_string, test_only_values = parse_input(test_only_line)
                test_only_roots = find_roots(test_only_input_string)

                if learner_version == 2:
                    if test_only_roots[0] in gender_dict:
                        test_only_values.append(gender_dict[test_only_roots[0]])
        
                test_args = {
                                "roots": test_only_roots, "nominalizer_terminals": nominalizer_terminals, "values": test_only_values,
                                "semantic_terminals": semantic_terminals, "adjectivalizer": adjectivalizer,
                                "learner_version": learner_version, "input_string": test_only_input_string,
                                "verbosity_level": verbosity_level, "sprouting_rules": sprouting_rules,
                                "line_index": test_only_line_index, "nominalizer_dicts": nominalizer_dicts, 
                                "semantic_terminal_dicts": semantic_terminal_dicts, 
                                "sprouting_rule_dicts": sprouting_rule_dicts, "vi_dicts": vi_dicts,
                                "vocabulary_items": vocabulary_items, "all_roots": all_roots, "affix": affix
                            }
                correct_derivations = 0
                with open(f"./outputs/previously_seen_tests/prev-seen-item-{test_only_line_index}-at-{line_index}.csv", "w", newline="") as file:
                    writer = csv.writer(file)
                    #write the header row
                    writer.writerow(["surface_success?", "full pronunciation", "diacritics", "nom_values", "nom_value_used_in_success?"])
                
                    for x in range(N_TEST_DERIVATIONS):
                        (
                        success, successful_nominalizer, 
                        full_pronunciation, vis_used, nominalizer_used,
                        roots, nominalizer_terminals, values, _,
                        _, _, _, _, _,
                        _, _, _, _, _, _
                        ) = test(gender_trial=None, test_and_learn="just_test", verbose = False, **test_args) 
                        if success:
                            correct_derivations += 1
                        writer.writerow([success, full_pronunciation, [vi.diacritic for vi in vis_used], nominalizer_used.values, successful_nominalizer])
                print(f"WE HAD {correct_derivations} surface-correct derivations of {test_only_input_string} at line {line_index}")
        

    # AT THE END: test learner on productively inflecting new items

    for unseen_line_index, unseen_line in enumerate(unseenDataString):
        unseen_input_string, unseen_values = parse_input(unseen_line)
        unseen_roots = find_roots(unseen_input_string)

        if learner_version == 2:
            if unseen_roots[0] in gender_dict:
                unseen_values.append(gender_dict[unseen_roots[0]])

        test_args = {
                        "roots": unseen_roots, "nominalizer_terminals": nominalizer_terminals, "values": unseen_values,
                        "semantic_terminals": semantic_terminals, "adjectivalizer": adjectivalizer,
                        "learner_version": learner_version, "input_string": unseen_input_string,
                        "verbosity_level": verbosity_level, "sprouting_rules": sprouting_rules,
                        "line_index": unseen_line_index, "nominalizer_dicts": nominalizer_dicts, 
                        "semantic_terminal_dicts": semantic_terminal_dicts, 
                        "sprouting_rule_dicts": sprouting_rule_dicts, "vi_dicts": vi_dicts,
                        "vocabulary_items": vocabulary_items, "all_roots": all_roots, "affix": affix
                    }
        correct_derivations = 0
        with open(f"./outputs/previously_unseen_tests/generate_unseen_{unseen_line_index}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            #write the header row
            writer.writerow(["surface_success?", "full pronunciation", "diacritics", "nom_values", "nom_value_used_in_success?"])
        
            for x in range(N_TEST_DERIVATIONS):
                (
                success, successful_nominalizer, 
                full_pronunciation, vis_used, nominalizer_used,
                roots, nominalizer_terminals, values, _,
                _, _, _, _, _,
                _, _, _, _, _, _
                ) = test(gender_trial=None, test_and_learn="just_test", verbose = False, **test_args) 
                if success:
                    correct_derivations += 1
                writer.writerow([success, full_pronunciation, [vi.diacritic for vi in vis_used], nominalizer_used.values, successful_nominalizer])
        print(f"WE GENERATED {correct_derivations} surface-correct derivations of the previously unseen {unseen_input_string}")
    
    # print outputs
    print_nominalizers(nominalizers=nominalizer_terminals, roots=all_roots)

    if learner_version == 2:
        with open("./outputs/uninterp_gender.csv", "w", newline="") as file:
            writer = csv.writer(file)
            #write the header row
            writer.writerow(["root", "gender"])
            #write each dictionary item as a row
            for key, value in gender_dict.items():
                writer.writerow([key, value])
    
    print_items(
        items=sprouting_rules,
        func=lambda x: [x.trigger_label, x.trigger_values, x.trigger_diacritic, x.keep_values, x.weight],
        file_name="sprouting_rules",
        headers=["trigger_label", "trigger_values", "trigger_diacritic", "keep_values", "weight"]
    )

    print_items(
        items=vocabulary_items,
        func=lambda x: [x.diacritic, x.pronunciation, x.label, x.values, x.triggers, x.weight],
        file_name="vocabulary_items",
        headers=["diacritic", "pronunciation", "label", "values", "triggers", "weight"]
    )


    print_weights(dicts=nominalizer_dicts, end_index=line_index, file_name="nominalizer_weights")
    print_weights(dicts=semantic_terminal_dicts, end_index=line_index, file_name="semantic_weights")
    print_weights(dicts=sprouting_rule_dicts, end_index=line_index, file_name="sprouting_weights")
    print_weights(dicts=vi_dicts, end_index=line_index, file_name="vi_weights")

    for vi_diacritic, series in vi_dicts.items():
        if not any(char.isupper() for char in vi_diacritic):
            x_vals = list(series.keys())
            y_vals = list(series.values())
            plt.plot(x_vals, y_vals, label=vi_diacritic)
    plt.legend()
    plt.xlabel('number of observations processed')
    plt.ylabel('weight')
    plt.savefig(f'./outputs/learner-version-{learner_version}-results-Vocabulary-weight-trace.pdf')

run()
