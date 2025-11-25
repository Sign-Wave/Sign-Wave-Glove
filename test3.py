import pandas as pd
# Load your CSV

df = pd.read_csv("sign_language_data.csv")

# Filter rows where label == "L" and flex0 > 950
filtered = df[(df["label"] == "E") & (df["flex0"] < 950)]

print(filtered)
filtered.to_csv("filtered_output.csv", index=False)
