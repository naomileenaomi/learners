import pandas as pd

df = (
    pd.read_csv('./data/Flex_it_nouns.csv')
    .drop(["Unnamed: 0", "Form", "Freq", "Fpmw", "Number", "Form_amb", "Ending", "Zipf", "POS", "Lemma"], axis=1)
)

df = df[~df["Inf_class"].str.contains("NA")]

final = pd.pivot_table(df, index="Baseform", columns="Gender", values="Inf_class", aggfunc='first')

final.to_csv("./data/processed_flex_it_nouns.csv")
