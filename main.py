# define constants
import inspect
import re
import random
import copy
from itertools import combinations
from difflib import SequenceMatcher
import csv


INITIAL_TERMINAL_WEIGHT = 10.0
UPDATE_TERMINAL_WEIGHT = .1
ALREADY_SELECTS_BONUS = 0.75

INITIAL_SPROUTING_RULE_WEIGHT = 1
UPDATE_SPROUTING_RULE_WEIGHT = .1
MORE_SPECIFIC_BONUS = .5


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
            and self.weight == other.weight
        )

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
        self.trigger_diacritic=split_off_vi.values
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
        if random.random() < self.weight / (self.weight + 1):
            return True
        else:
            return False


def create_semantic_terminals(learner_version):
    core_terminals = (
        SemanticTerminal(
            label="definite",
            values={"+definite",},
            selectional=["atomic, minimal"],
            selection_strength=False,
        ),
        # SemanticTerminal(
        #     label="definite",
        #     values={"+definite",},
        #     selectional=["atomic, minimal"],
        #     selection_strength=True,
        # ),
        SemanticTerminal(
            label="definite",
            values={"-definite",},
            selectional=["atomic, minimal"],
            selection_strength=False,
        ),
        # SemanticTerminal(
        #     label="definite",
        #     values={"-definite",},
        #     selectional=["atomic, minimal"],
        #     selection_strength=True,
        # ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"+atomic", "+minimal"},
            selectional=["nominalizer"],
            selection_strength=True,
        ),
        # SemanticTerminal(
        #     label="atomic, minimal",
        #     values={"+atomic", "+minimal"},
        #     selectional=["nominalizer"],
        #     selection_strength=False,
        # ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"-atomic", "+minimal"},
            selectional=["nominalizer"],
            selection_strength=True,
        ),
        # SemanticTerminal(
        #     label="atomic, minimal",
        #     values={"-atomic", "+minimal"},
        #     selectional=["nominalizer"],
        #     selection_strength=False,
        # ),
        SemanticTerminal(
            label="atomic, minimal",
            values={"-atomic", "-minimal"},
            selectional=["nominalizer"],
            selection_strength=True,
        ),
        # SemanticTerminal(
        #     label="atomic, minimal",
        #     values={"-atomic", "-minimal"},
        #     selectional=["nominalizer"],
        #     selection_strength=False,
        # ),  
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


def create_vi(pronunciation, label, values, triggers, vocabulary_items):
    if pronunciation == "null" and values == set():
        return False, None, vocabulary_items
    
    new_vi = VocabularyItem(
        pronunciation=pronunciation,
        label=label,
        values=values,
        diacritic=f"{pronunciation}_{get_diacritic_number(pronunciation, vocabulary_items)}",
        triggers=triggers,
    ) 

    if new_vi in vocabulary_items:
        return False, vocabulary_items[vocabulary_items.index(new_vi)], vocabulary_items
    else:
        return True, new_vi, vocabulary_items + [new_vi]


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
    match_list = [
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
        )
    ]

    for vi in match_list:
        _, _, vocabulary_items = create_vi(
            pronunciation=vi.pronunciation,
            label=vi.label,
            values=vi.values,
            triggers = set().union(
                vocabulary_item.triggers,
                *[vi_2.triggers for vi_2 in match_list]
            ),
            vocabulary_items=vocabulary_items
        )

    partial_match_list = [
        vi
        for vi
        in vocabulary_items
        if (
            vi.label == vocabulary_item.label
            and
            partial_overlap(vi.values, vocabulary_item.values)
            and
            len(shared_substring(vi.pronunciation, vocabulary_item.pronunciation)[0]) > 0
        )
    ]

    return partial_match_list, vocabulary_items


def shared_substring(string1, string2):
    if string1 == "null" and string2 == "null":
        return ('null', 'null', 'null')	

    if string1 == "null":
        return ('null', 'null', string2)

    if string2 == "null":
        return ('null', string1, 'null')
	
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

    for intersecting_vi in match_list:

        substring, new_vi_ex, intersecting_vi_ex = shared_substring(
            new_vi.pronunciation,
            intersecting_vi.pronunciation
        )

        # intersection:
        if not (
            substring == "null" or 
            intersecting_vi_ex == "null"
        ):
            if new_vi.pronunciation[:len(substring)] == substring:
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
            vocabulary_items=vocabulary_items
        )

        if intersection_is_new:
            new_vi_pairs.append((intersection_vi, new_vi))
            new_vi_pairs.append((intersection_vi, intersecting_vi))

        # intersecting-VI MINUS newVI:
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


        subtracted_from_intersecting_is_new, subtracted_from_intersecting_vi, vocabulary_items = create_vi(
            pronunciation=intersecting_vi_ex,
            label=label,
            values=intersecting_vi.values - new_vi.values,
            triggers=intersecting_vi.triggers,
            vocabulary_items=vocabulary_items
        )

        if subtracted_from_intersecting_is_new:
            new_vi_pairs.append((subtracted_from_intersecting_vi, intersecting_vi))

        #newVI MINUS intersecting-VI:

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

        subtracted_from_new_is_new, subtracted_from_new_vi, vocabulary_items = create_vi(
            pronunciation=new_vi_ex,
            label=label,
            values=new_vi.values - intersecting_vi.values,
            triggers=new_vi.triggers,
            vocabulary_items=vocabulary_items
        )

        if subtracted_from_new_is_new:
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


def prep_slices(morphs, terminals, affix):

    assert len(morphs) <= len(terminals)

    root_index = next((i for i, s in enumerate(morphs) if s.isupper()), None)

    if root_index is not None:
        while len(morphs) < len(terminals):
            print(morphs)
            
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


def generate_vi(terminal_chain, input_string, roots, vocabulary_items, nominalizers, sprouting_rules, affix):

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
        diacritics_in_this_word = []
        morphs = string_slice.split("-")
        terminals = [
            item
            for item
            in tc_slice
            if item != "-"
        ]

        morphs, terminals = prep_slices(morphs=morphs, terminals=terminals, affix=affix)

        if affix  == "suffixing":
            zipper = zip(terminals[::-1], morphs[::-1])
        elif affix == "prefixing":
            zipper = zip(terminals, morphs)
        else:
            assert False
        
        for terminal, morph in zipper:
            # if morph.isupper() and type(terminal) != Root:
            #     morph = "null"
            
            static_diacritics_in_this_word = diacritics_in_this_word.copy()
            for triggers in [set()] + [{diacritic} for diacritic in static_diacritics_in_this_word]:
                if terminal.label == "nominalizer":
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
                    vocabulary_items=vocabulary_items
                )

                further_vis = []

                if is_new:
                    further_vis, vocabulary_items = generalize_vi(
                        new_vi=new_vi,
                        vocabulary_items=vocabulary_items, 
                        affix=affix
                    )

                if any(char.isupper() for char in string_slice):
                    diacritics_in_this_word += [new_vi.diacritic]

                    diacritics_in_this_word += [
                        split_out_vi.diacritic
                        for (split_out_vi, source_vi)
                        in further_vis
                        if source_vi == new_vi
                    ]
                    
                else:
                    nominalizers = create_nominalizer(
                        root=roots[0],
                        values={new_vi.diacritic},
                        existing_nominalizers=nominalizers
                    )

                    nominalizers = create_nominalizer(
                        root=roots[0],
                        values=nominalizer.values.union({new_vi.diacritic}),
                        existing_nominalizers=nominalizers
                    )                    
                    
                    if(len(further_vis) > 0):
                        for split_out_vi, source_vi in further_vis:
                            nominalizers = create_nominalizer(
                                root=roots[0],
                                values={split_out_vi.diacritic},
                                existing_nominalizers=nominalizers
                            )

                            for nom in nominalizers:
                                if source_vi.diacritic in nom.values:
                                    nominalizers = create_nominalizer(
                                        root=roots[0], 
                                        values=(nom.values - {source_vi.diacritic}).union({split_out_vi.diacritic}),
                                        existing_nominalizers=nominalizers
                                    )
                            
                            if split_out_vi.label == "Agr":
                                sprouting_rules.append(
                                    SproutingRule(
                                        split_off_vi=split_out_vi, 
                                        large_vi=source_vi
                                    )
                                )

                                nominalizer.values.update({new_vi.diacritic})
                    else:
                        nominalizer.values.update({new_vi.diacritic})

                        nominalizers = create_nominalizer(
                            root=roots[0],
                            values=nominalizer.values,
                            existing_nominalizers=nominalizers
                        )

    return vocabulary_items, nominalizers, sprouting_rules


def insert_vi(terminal_chain, vocabulary_items):
    full_pronunciation = ""
    vis_used = []

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
                        if vi.diacritic in item.values
                    ]

                    if len(super_matches) > 0:
                        selected_vi = random.choices(
                            population=super_matches,
                            weights=[
                                match.weight + MORE_SPECIFIC_BONUS * len(match.values) 
                                for match 
                                in super_matches
                            ]
                        )[0]
                    else:
                        selected_vi = random.choices(
                            population=matching_vis,
                            weights=[
                                match.weight + MORE_SPECIFIC_BONUS * len(match.values) 
                                for match 
                                in matching_vis
                            ]
                        )[0]
                    
                    vis_used.append(selected_vi)

                if selected_vi == None or selected_vi.pronunciation == "null":
                    if selected_vi == None or len(selected_vi.triggers) == 0:    
                        if index < len(slice) - 1:
                            assert slice[index+1] == "-"
                            assert slice[index+2] != "-"
                            
                            for diacritic in item.values:
                                for vi in vis_used:
                                    if diacritic in vi.triggers:
                                        slice[index+2].values.add(diacritic)

                else:
                    full_pronunciation += selected_vi.pronunciation

                if selected_vi != None and len(selected_vi.triggers) > 0:
                    assert root_count == 1
                    if index < len(slice) - 1:
                        assert slice[index+1] == "-"
                        assert slice[index+2] != "-"
                        slice[index+2].values.update(selected_vi.triggers)

        if slice_index < len(slices) - 1:
            full_pronunciation += "#"

    return full_pronunciation, vis_used 
    

def sprout_nodes(terminal_chain, sprouting_rules, affix):
    sprouting_rules_used = []

    for rule in sprouting_rules:
        matching_terminals = [
            terminal
            for terminal
            in terminal_chain.linear
            if (
                    hasattr(terminal, "values")
                and hasattr(terminal, "label")
                and terminal.label == rule.trigger_label
                and {value for value in terminal.values if value[0] in ["+", "-"]}.issubset(rule.trigger_values)
                and rule.trigger_diacritic in terminal.values
            )
        ]

        assert len(matching_terminals) <= 1

        for matching_terminal in matching_terminals:
            if rule.check_if_use():

                matching_terminal.values = rule.key_values
                sprouting_rules_used.append(rule)

                if affix == "suffixing":
                    terminal_chain = insert_into_linear(
                        terminal_chain=terminal_chain,
                        terminal=matching_terminal,
                        affix=affix,
                        new_linear=("-", AgrTerminal(values=matching_terminal.values))
                    )
                elif affix == "prefixing":
                    terminal_chain = insert_into_linear(
                        terminal_chain=terminal_chain,
                        terminal=matching_terminal,
                        affix=affix,
                        new_linear=(AgrTerminal(values=matching_terminal.values), "-")
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


def run(
    input_file_path="./data/input/italian-class-iii-only-duped.txt",
    root_file_path="./data/roots/italian-class-iii-only-ROOTS-list.txt",
    learner_version=1,
    affix = "suffixing",
    verbosity_level = 2,
):

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
    nominalizer_terminals = []
    adjectivalizer = AdjectivalizerTerminal()
    sprouting_rules = []
    vocabulary_items = []

    # store weights as we go
    nominalizer_dicts = {}
    semantic_terminal_dicts = {}
    sprouting_rule_dicts = {}
    vi_dicts = {}

    # process input

    with open(input_file_path,'r') as learningDataFile:
        learningDataString = learningDataFile.read().splitlines()


    for line_index, line in enumerate(learningDataString):
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

        # generate vis from input
        vocabulary_items, nominalizer_terminals, sprouting_rules = generate_vi(
            terminal_chain=terminal_chain,
            input_string=input_string,
            roots=roots,
            vocabulary_items=vocabulary_items,
            nominalizers=nominalizer_terminals,
            sprouting_rules=sprouting_rules,
            affix=affix
        )

        debug_print(verbosity_level, 2, f"vocabulary_items: {vocabulary_items}")
        debug_print(verbosity_level, 2, f"nominalizer_terminals: {nominalizer_terminals}")
        debug_print(verbosity_level, 2, f"sprouting_rules: {sprouting_rules}")


        # Test Derivation
        # Select enumeration
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
        
        # Do node sprouting

        debug_print(verbosity_level, 2, f"sprouting_rules: {sprouting_rules}")

        terminal_chain, sprouting_rules_used = sprout_nodes(
            terminal_chain=terminal_chain,
            sprouting_rules=sprouting_rules,
            affix=affix
        )

        debug_print(verbosity_level, 2, f"TerminalChain: {terminal_chain}")

        # Insert Vis
        full_pronunciation, vis_used = insert_vi(
            terminal_chain=terminal_chain, 
            vocabulary_items=vocabulary_items
        )

        debug_print(verbosity_level, 2, f"full_pronunciation: {full_pronunciation}")
        debug_print(verbosity_level, 2, f"vis_used: {vis_used}")


        if full_pronunciation == input_string.replace("-", ""):

            debug_print(verbosity_level, 2, f"Success")

            nominalizers_used = [
                terminal
                for terminal
                in terminals_used
                if type(terminal) == NominalizerTerminal
            ]

            assert len(nominalizers_used) == 1

            nominalizer_used = nominalizers_used[0]

            nominalizer_terminals = create_nominalizer(
                root=roots[0], 
                values=nominalizer_used.values, 
                existing_nominalizers=nominalizer_terminals
            )            
            
            for terminal in terminals_used:
                terminal.weight += UPDATE_TERMINAL_WEIGHT
            
            for rule in sprouting_rules_used:
                rule.weight += UPDATE_SPROUTING_RULE_WEIGHT

            for vi in vis_used:
                vi.weight += UPDATE_TERMINAL_WEIGHT

        else:

            debug_print(verbosity_level, 2, f"Failure")


            for terminal in terminals_used:
                terminal.weight -= UPDATE_TERMINAL_WEIGHT
            
            for rule in sprouting_rules_used:
                rule.weight -= UPDATE_SPROUTING_RULE_WEIGHT

            for vi in vis_used:
                vi.weight -= UPDATE_TERMINAL_WEIGHT

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


run()