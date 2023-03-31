import re
import csv

class Utterance:
    def __init__(self, filename, linenumber, mother, gloss, dptype):
        self.filename = filename
        self.linenumber = linenumber
        self.mother = mother
        self.gloss = gloss
        self.dptype = dptype
    
    def show(self):
        print("mother: " + self.mother + "\n" + "gloss: " + self.gloss)

class Observation:
    def __init__(self, filename, linenumber, mother, gloss, dptype, pronunCHILDES, glossCHILDES, oglemma1, rootmeaning1, oglemma2, rootmeaning2, values, potentially_invariable_n, potentially_invariable_a):
        self.filename = filename
        self.linenumber = linenumber
        self.mother = mother
        self.gloss = gloss
        self.dptype = dptype
        self.pronunCHILDES = pronunCHILDES
        self.glossCHILDES = glossCHILDES
        self.oglemma1 = oglemma1
        self.rootmeaning1 = rootmeaning1
        self.oglemma2 = oglemma2
        self.rootmeaning2 = rootmeaning2
        self.values = values
        self.potentially_invariable_n = potentially_invariable_n
        self.potentially_invariable_a = potentially_invariable_a

    def show(self):
        print("pronunciation: " + ' '.join(self.pronunCHILDES) + "\n" + "gloss: " + self.glossCHILDES)
        print("noun lemma: " + self.oglemma1 + "\n" + "noun root meaning: " + self.rootmeaning1)
        print("adj lemma: " + self.oglemma2 + "\n" + "adj root meaning: " + self.rootmeaning2)
        print("full pronunc: " + self.mother + "\n" + "full gloss: " + self.gloss + "\n")

with open('./data/art-N-adj.txt', encoding="utf-8") as f:
    raw_DNA = f.read()

with open('./data/art-N.txt', encoding="utf-8") as g:
    raw_DN = g.read()

raw_utterances_DNA = [x for x in raw_DNA.split("****************************************")[1].split("----------------------------------------") if not x.startswith("\nFrom file")]

raw_utterances_DN = [x for x in raw_DN.split("****************************************")[1].split("----------------------------------------") if not x.startswith("\nFrom file")]

Utterance_list = []
Observation_list = []

for utterance in raw_utterances_DNA:
    dp_type = "DNA"
    mother = ''
    gloss = ''
    for line in utterance.splitlines():
        if line.startswith("*** File"):
            file_name = line.split(":")[0]
            line_number = line.split(": ")[1]
        elif line.startswith("*MOT:"):
            mother = line[6:]
        elif line.startswith("%mor:"):
            gloss = line[6:]
        else:
            if not gloss:
                mother += line 
            else:
                gloss += line 
    mother = mother.replace("\t", " ")
    mother = mother.replace("xxx ", "")
    mother = mother.replace("+, ", "")
    mother = mother.replace("++ ", "")
    mother = mother.replace("&s ", "")
    mother = mother.replace("&-eh ", "")
    mother = mother.replace("&pi ", "")
    mother = mother.replace("&lal ", "")
    mother = mother.replace("&pa ", "")
    mother = mother.replace("(.) ", "")
    mother = mother.replace("(..) ", "")
    mother = mother.replace("[>] ", "")
    mother = mother.replace("[<] ", "")
    mother = mother.replace("[: sì] ", "")
    mother = mother.replace("[: palla] ", "")
    mother = mother.replace("[: bene] ", "")
    mother = mother.replace("[: aspetta] ", "")
    if "[/]" in mother:
        for z in range(1, mother.count("[/]") + 1):
            if mother[mother.find("[/]")-2] == ">":
                mother = mother[:mother.rfind("<", 0, mother.find("[/]"))] + mother[mother.find("[/]") + 4:]
            else: 
                if mother.rfind(" ", 0, mother.find(" [/]")) == -1:
                    mother = mother[mother.find("[/]") + 4:]
                else:
                    mother = mother[:mother.rfind(" ", 0, mother.find(" [/]"))] + mother[mother.find("[/]") + 3:]

    if "[//]" in mother:
        for w in range(1, mother.count("[//]") + 1):
            if mother[mother.find("[//]")-2] == ">":
                mother = mother[:mother.rfind("<", 0, mother.find("[//]"))] + mother[mother.find("[//]") + 5:]
            else:
                if mother.rfind(" ", 0, mother.find(" [//]")) == -1:
                    mother = mother[mother.find("[//]") + 5:]
                else:
                    mother = mother[:mother.rfind(" ", 0, mother.find(" [//]"))] + mother[mother.find("[//]") + 4:]

    gloss = gloss.replace("\t", " ")

    Utterance_list.append(Utterance(file_name, line_number, mother, gloss, dp_type))

for utterance in raw_utterances_DN:
    dp_type = "DN"
    mother = ''
    gloss = ''
    for line in utterance.splitlines():
        if line.startswith("*** File"):
            file_name = line.split(":")[0]
            line_number = line.split(": ")[1]
        elif line.startswith("*MOT:"):
            mother = line[6:]
        elif line.startswith("%mor:"):
            gloss = line[6:]
        else:
            if not gloss:
                mother += line 
            else:
                gloss += line 
    mother = mother.replace("\t", " ")
    mother = mother.replace("xxx ", "")
    mother = mother.replace("+, ", "")
    mother = mother.replace("++ ", "")
    mother = mother.replace("&s ", "")
    mother = mother.replace("&-eh ", "")
    mother = mother.replace("&pi ", "")
    mother = mother.replace("&lal ", "")
    mother = mother.replace("&pa ", "")
    mother = mother.replace("(.) ", "")
    mother = mother.replace("(..) ", "")
    mother = mother.replace("[>] ", "")
    mother = mother.replace("[<] ", "")
    mother = mother.replace("[: sì] ", "")
    mother = mother.replace("[: palla] ", "")
    mother = mother.replace("[: bene] ", "")
    mother = mother.replace("[: aspetta] ", "")
    if "[/]" in mother:
        for z in range(1, mother.count("[/]") + 1):
            if mother[mother.find("[/]")-2] == ">":
                mother = mother[:mother.rfind("<", 0, mother.find("[/]"))] + mother[mother.find("[/]") + 4:]
            else: 
                if mother.rfind(" ", 0, mother.find(" [/]")) == -1:
                    mother = mother[mother.find("[/]") + 4:]
                else:
                    mother = mother[:mother.rfind(" ", 0, mother.find(" [/]"))] + mother[mother.find("[/]") + 3:]

    if "[//]" in mother:
        for w in range(1, mother.count("[//]") + 1):
            if mother[mother.find("[//]")-2] == ">":
                mother = mother[:mother.rfind("<", 0, mother.find("[//]"))] + mother[mother.find("[//]") + 5:]
            else:
                if mother.rfind(" ", 0, mother.find(" [//]")) == -1:
                    mother = mother[mother.find("[//]") + 5:]
                else:
                    mother = mother[:mother.rfind(" ", 0, mother.find(" [//]"))] + mother[mother.find("[//]") + 4:]
    gloss = gloss.replace("\t", " ")

    Utterance_list.append(Utterance(file_name, line_number, mother, gloss, dp_type))

# x = 0
# for obj in Utterance_list:
#     x+=1
#     print(x)
#     obj.show()
#     print("\n")
# print("total: ") 
# print(len(Utterance_list))

# print(Utterance_list[44].mother)
# print(Utterance_list[44].gloss)

for obj in Utterance_list:
    n_matches = 5
    while "(" + str(n_matches) + ")" not in obj.gloss:
        n_matches -= 1

    for x in range(1, n_matches + 1):
        pronunc_CHILDES = ""
        gloss_CHILDES = ""
        values = []
        word_index = 0
        match_word_index = 0
        for word in obj.gloss.split(" "): #obj.gloss.split(" "):
            word_index += 1
            if word.startswith("(" + str(x) + ")"):
                gloss_CHILDES += word[3:] + " "
                match_word_index = word_index
        # print(gloss_CHILDES)
        # print("match word index is: " + str(match_word_index) + " for x = " + str(x))

        noungloss = gloss_CHILDES.split(" ")[1]
        
        potentially_invariable_n = False
        potentially_invariable_a = False
        if ("DIM" in noungloss) or ("SUPER" in noungloss):
            oglemma1 = noungloss[noungloss.find("n|") + 2 : noungloss.rfind("-")]
        else:
            z = 0
            if "&m" in noungloss:
                oglemma1 = noungloss[noungloss.find("n|") + 2 : noungloss.find("&m")] 
                potentially_invariable_n = True
            elif "&f" in noungloss:
                oglemma1 = noungloss[noungloss.find("n|") + 2 : noungloss.find("&f")]
                potentially_invariable_n = True 
            else:
                oglemma1 = noungloss[noungloss.find("n|") + 2 : noungloss.find("-")]
            
        if "=" in noungloss:
            rootmeaning1 = noungloss[noungloss.find("=") + 1 : ]
        else: 
            rootmeaning1 = ""        

        if obj.dptype == 'DNA':
            pronunc_CHILDES = obj.mother.split(" ")[match_word_index - 3:match_word_index]
            adjgloss = gloss_CHILDES.split(" ")[2]
            if ("DIM" in adjgloss) or ("SUPER" in adjgloss):
                oglemma2 = adjgloss[adjgloss.find("adj|") + 4 : adjgloss.rfind("-")]
            else:
                q = 0
                if "-" in adjgloss:
                    oglemma2 = adjgloss[adjgloss.find("adj|") + 4 : adjgloss.rfind("-")]
                elif "=" in adjgloss:
                    oglemma2 = adjgloss[adjgloss.find("adj|") + 4 : adjgloss.rfind("=")]
                    potentially_invariable_a = True
                else:
                    oglemma2 = adjgloss[adjgloss.find("adj|") + 4 : ]
                    potentially_invariable_a = True
            if "=" in adjgloss:
                rootmeaning2 = adjgloss[adjgloss.find("=") + 1 : ]
            else: 
                rootmeaning2 = ""

        else:
            pronunc_CHILDES = obj.mother.split(" ")[match_word_index - 2:match_word_index]
            
            oglemma2 = ""
            rootmeaning2 = ""
        # print(pronunc_CHILDES)

        if 'il' in gloss_CHILDES.split(" ")[0]:
            values.append("+definite")
        if 'uno' in gloss_CHILDES.split(" ")[0]:
            values.append("-definite")
        if 'sg' in gloss_CHILDES.split(" ")[1]:
            values.append("+atomic,+minimal")
        if 'pl' in gloss_CHILDES.split(" ")[1]:
            values.append("PLURAL-PLACEHOLDER")
        # print(values)

        Observation_list.append(Observation(obj.filename, obj.linenumber, obj.mother, obj.gloss, obj.dptype, pronunc_CHILDES, gloss_CHILDES, oglemma1, rootmeaning1, oglemma2, rootmeaning2, values, potentially_invariable_n, potentially_invariable_a))

# Observation_list[0].show()

print("total observations: ") 
print(len(Observation_list)) #4844 originally, 4807 after exclusions of intervening commas, etc.

print("total [D N] observations: ") 
print(len([x for x in Observation_list if x.dptype == 'DN'])) #4434 originally, 4428 after exclusions

print("total [D N Adj] observations: ") 
print(len([x for x in Observation_list if x.dptype == 'DNA'])) #410 originally, 379 after exclusions

init_seg_exclude_list = ("gn", "ps", "pn", "x", "z", "sb", "sc", "sd", "sf", "sg", "sk", "sl", "sm", "sn", "sp", "squ", "sr", "st", "sv", "a", "e", "i", "o", "u", "y", "j", "è", "à", "ù", "ò", "é")

Include_list = [obs for obs in Observation_list if not obs.pronunCHILDES[1].startswith(init_seg_exclude_list)]
print("phono regular subset of data has " + str(len(Include_list)) + " observations") #4102


print(Observation_list[0].filename + " " + Observation_list[0].linenumber)
print(Observation_list[1].filename + " " + Observation_list[1].linenumber)
print(Observation_list[2].filename + " " + Observation_list[2].linenumber)
print(Observation_list[3].filename + " " + Observation_list[3].linenumber)
print(Observation_list[4].filename + " " + Observation_list[4].linenumber)
print(Observation_list[-5].filename + " " + Observation_list[-5].linenumber)

def extract_number(linenumber):
    return int(linenumber.split(" ")[-1][:-1])

sorted_observation_list = sorted(Observation_list, key=lambda x: extract_number(x.linenumber))
sorted_observation_list = sorted(sorted_observation_list, key=lambda x: x.filename)

print(sorted_observation_list[0].filename + " " + sorted_observation_list[0].linenumber)
print(sorted_observation_list[1].filename + " " + sorted_observation_list[1].linenumber)
print(sorted_observation_list[2].filename + " " + sorted_observation_list[2].linenumber)
print(sorted_observation_list[3].filename + " " + sorted_observation_list[3].linenumber)
print(sorted_observation_list[4].filename + " " + sorted_observation_list[4].linenumber)
print(sorted_observation_list[-5].filename + " " + sorted_observation_list[-5].linenumber)


def read_csv_column(filename, column_name):
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = []
        for row in csv_reader:
            data.append(row[column_name])
    return data

stems = read_csv_column("./data/italian-declension - tonelli-ROOTS-list.csv", "Italian stem form")

def read_csv_to_dict(filename, key_column_name, val_column_name):
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = {}
        for row in csv_reader:
            data[row[key_column_name]] = row[val_column_name]
    return data


stem_to_root = read_csv_to_dict("./data/italian-declension - tonelli-ROOTS-list.csv", "Italian stem form", "UPPER")

def find_first_substring(substrings, string):
    for substring in substrings:
        if substring in string:
            return substring
    assert False

def process_token(token, substrings):
    substring = find_first_substring(substrings, token)

    remainder = token.replace(substring, "")

    if len(remainder) == 0:
        return f"{stem_to_root[substring]}-null"
    else:
        return f"{stem_to_root[substring]}-{remainder}"


with open("./data/tonelli_input.txt", 'w') as file:       
    for observation in sorted_observation_list:
        tokens = (
            [observation.pronunCHILDES[0]]
            + 
            [
                process_token(token, stems)
                for token
                in observation.pronunCHILDES[1:]
            ]
        )

        token_str = "#".join(tokens)
        values_str = "\t".join(observation.values)

        file.write(f"{token_str}\t{values_str}\n") #test


# Root_list = []
# # gram_gen = ""
# for obs in Observation_list:
#     if "-f&" in obs.glossCHILDES.split(" ")[1]:
#         gram_gen = "fem"
#     elif "&f" in obs.glossCHILDES.split(" ")[1]:
#         gram_gen = "fem"
#     else:
#         gram_gen = "masc"
#     if obs.potentially_invariable_n:
#         a = 0
#         if (obs.rootmeaning1, obs.oglemma1, obs.pronunCHILDES[1], gram_gen) not in Root_list:
#             Root_list.append((obs.rootmeaning1, obs.oglemma1, obs.pronunCHILDES[1], gram_gen))
#     else:
#         b = 0
#         if (obs.rootmeaning1, obs.oglemma1, obs.pronunCHILDES[1][:-1], gram_gen) not in Root_list:
#             Root_list.append((obs.rootmeaning1, obs.oglemma1, obs.pronunCHILDES[1][:-1], gram_gen))
#     if obs.dptype == "DNA":
#         c = 0
#         if obs.potentially_invariable_a:
#             d = 0
#             if (obs.rootmeaning2, obs.oglemma2, obs.pronunCHILDES[2], "") not in Root_list:
#                 Root_list.append((obs.rootmeaning2, obs.oglemma2, obs.pronunCHILDES[2], ""))
#         else:
#             if (obs.rootmeaning2, obs.oglemma2, obs.pronunCHILDES[2][:-1], "") not in Root_list:
#                 Root_list.append((obs.rootmeaning2, obs.oglemma2, obs.pronunCHILDES[2][:-1], ""))

# # for root in Root_list:
# #     print(root[0] + ", " + root[1] + ", " + root[2] + ", " + root[3])

# print(str(len(Root_list)) + " unique Roots (incl. diminutivized Roots as separate)") #1080

# with open('tonelli-ROOTS-list.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerows(Root_list)

#to-do
# values.append("-atomic,+minimal")
# values.append("-atomic,-minimal")


#debugging tests
#'\n*** File "/Applications/CLAN/Tonelli/Marco/020524.cha": line 1029.\n*MOT:\tquesto è l\' uovo rotto e qua c\' è il pulcino .\n%mor:\tpro:det|questo-m&sg=this v|esse-3S&PRES=be \x02\x05(1)\x02\x06art|il&sg\n\t\x02\x05(1)\x02\x06n|uovo-m&sg=egg \x02\x05(1)\x02\x06adj|rotto-m&sg conj|e adv|qua pro:clit|ci&1P\n\tv|esse-3S&PRES=be art|il&m&sg n|pulcino-m&sg .\n',

# mother = "sì , colla pioggia il vento , il mare mosso , le onde alte [/] alte"
# mother = "fai [/] fai ancora la torre bravo ."
# mother = "ah <ha il naso lungo> [/] ha il naso lungo"
# mother = "<aspetta che> [/] aspetta che spengo il registratore ."

# mother = "perché tu avevi messo un tappo sull' altro e quando ho chiuso il pennarello azzurro ho lasciato i tappi [//] i due tappi uniti ."
# mother = "ci [//] ci stava sopra una bambina piccolina ."
# mother = "no , non è una moto , <è un> [//] è la macchina di Paperino ."
# mother = "<e papà> [//] e nonno Dario , il papà della mamma , viene da"

# mother = "dunque [/] dunque , qua no qua c' è la formica , la vespa , eccola qui ."
# mother = "no [/] no , mettiamo il calzetto ."

# mother = "e no [/] no [/] no dobbiamo fare tutta la colonna alta [/] alta con questi pezzi verdi ."
# mother = "sì [/] sì , no , ma cercavo un pezzo dell [/] dell' ovetto dove stava il puzzle ."
# mother = "ed adesso facciamo che [//] e [//] l' uovo che è stato rotto ."
# mother = "no [/] no [/] no [/] no , fammi sentir(e) bene , la pre(cedenza) +..."

# print(mother)
# if "[/]" in mother:
#     for z in range(1, mother.count("[/]") + 1):
#         if mother[mother.find("[/]")-2] == ">":
#             mother = mother[:mother.rfind("<", 0, mother.find("[/]"))] + mother[mother.find("[/]") + 4:]
#         else: 
#             if mother.rfind(" ", 0, mother.find(" [/]")) == -1:
#                 mother = mother[mother.find("[/]") + 4:]
#             else:
#                 mother = mother[:mother.rfind(" ", 0, mother.find(" [/]"))] + mother[mother.find("[/]") + 3:]

# if "[//]" in mother:
#     for w in range(1, mother.count("[//]") + 1):
#         if mother[mother.find("[//]")-2] == ">":
#             mother = mother[:mother.rfind("<", 0, mother.find("[//]"))] + mother[mother.find("[//]") + 5:]
#         else:
#             if mother.rfind(" ", 0, mother.find(" [//]")) == -1:
#                 mother = mother[mother.find("[//]") + 5:]
#             else:
#                 mother = mother[:mother.rfind(" ", 0, mother.find(" [//]"))] + mother[mother.find("[//]") + 4:]
# print(mother)

# issue_count = 0
# for obs in Observation_list:
#     if obs.pronunCHILDES[1] == "e":
#         issue_count+= 1
#         obs.show()
#     if obs.pronunCHILDES[1] == "a":
#         issue_count+= 1
#         obs.show()
#     if obs.pronunCHILDES[1] == "i":
#         issue_count+= 1
#         obs.show()
#     if obs.pronunCHILDES[1] == "il":
#         issue_count+= 1
#         obs.show()
#     if obs.pronunCHILDES[1] == "la":
#         issue_count+= 1
#         obs.show()
#     if obs.pronunCHILDES[1] == "le":
#         issue_count+= 1
#         obs.show()
#     if obs.pronunCHILDES[1].startswith("un"):
#         issue_count+= 1
#         obs.show()

# print(str(issue_count) + " issues found")

# z = 0
# for obs in Observation_list:
#     # if obs.pronunCHILDES[1].startswith(init_seg_exclude_list):
#     #     if obs.pronunCHILDES[0] not in ("il", "le", "la", "un", "una"):
#     #         print(obs.pronunCHILDES[0] + " " + obs.pronunCHILDES[1])
#     if obs.pronunCHILDES[0] not in ("il", "i", "la",  "le", "un", "una", "uno", "l'", "lo", "gli", "un'"):
#         print(obs.pronunCHILDES[0] + " " + obs.pronunCHILDES[1])
#         print(obs.mother + "\n")
#         z+=1
#         # print(obs.filename)
# print(str(z) + "errors")