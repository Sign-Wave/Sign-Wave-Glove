import pandas as pd

# Load your CSV
df = pd.read_csv("sign_language_data.csv")

# Remove rows where label == "L" and flex0 > 950
df_cleaned = df[~((df["label"] == "D") & (df["flex0"] < 730))]

# Save back to the same file (overwrite)
df_cleaned.to_csv("sign_language_data.csv", index=False)
