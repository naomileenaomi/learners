# define constants
INITIAL_WEIGHT = 10.0
UPDDATE_WEIGHT = 0.2
ALREADY_SELECTS_BONUS = 0.5


def run(input_file_path="./sample_input.txt"):

    with open(input_file_path,'r') as learningDataFile:
        learningDataString = learningDataFile.read().splitlines()


    for line in learningDataString:
        print(line)
    
run()