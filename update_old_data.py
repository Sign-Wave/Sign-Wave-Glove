import pandas as pd
import numpy as np

# --- 1. Define the new features per label ---
# Fill these in with the correct values for each label.
# Example values shown for label "A" — adjust for yours.
label_to_extra = {
    #"A": [1, 1, 0, 0],
    #"D": [0, 1, 0, 0],
    #"G": [0, 1, 0, 0], #
    #"I": [1, 1, 0, 0], #
    #"J": [1, 1, 0, 0], #
    #"L": [0, 1, 0, 0], #
    #"M": [1, 0, 0, 1], #
    #"N": [1, 0, 1, 0], #
    #"Q": [0, 1, 0, 0], #
    #"R": [0, 1, 0, 0], #
    #"S": [1, 1, 0, 0], #
    "T": [0, 1, 0, 0], #
    #"X": [0, 1, 0, 0], #
    #"Y": [1, 1, 0, 0], #
    #"Z": [0, 1, 0, 0],
    #"REST": [0, 0, 0, 0],
}

# Columns to overwrite
extra_cols = [
    "index_inside",
    "middle_fingerprint",
    "middle_inside_to_ring",
    "ring_tape"
]

# ---- Load CSV -------------------------------------------------------
df = pd.read_csv("sign_language_data_old.csv")

# ---- Apply replacements ---------------------------------------------
df["thumbprint"] = (df["label"]=="T").astype(int)
mask_DZ = df["label"].isin(["D", "Z"])
df.loc[mask_DZ, "thumbprint"] = (np.random.rand(mask_DZ.sum()) < 0.15).astype(int)

mask_G = df["label"] == "G"
df.loc[mask_G, "thumbprint"] = (np.random.rand(mask_G.sum()) < 0.10).astype(int)

# ---- Save modified CSV ----------------------------------------------
df.to_csv("sign_language_data.csv", index=False)

print("Done! Saved as output.csv")