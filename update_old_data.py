import csv
import random

# --- 1. Define the new features per label ---
# Fill these in with the correct values for each label.
# Example values shown for label "A" — adjust for yours.
label_to_extra = {
    "A": [1, 0, 0, 0],
    "B": [1, 0, 0, 0],
    "C": [[1, 0], 0, 0, 0],
    "D": [0, 0, 0, 0],
    "E": [1, 0, 0, 0], #
    "F": [0, 0, 0, 0], #
    "G": [0, 0, 0, 0], #
    "H": [1, 0, 0, 0], #
    "I": [1, 0, 0, 0], #
    "J": [1, 0, 0, 0], #
    "K": [0, 0, 0, 0], #
    "L": [0, 0, 0, 0], #
    "M": [1, 0, 0, 1], #
    "N": [0, 0, 1, 0], #
    "O": [1, 0, 0, 0], #
    "P": [0, 0, 0, 0], #
    "Q": [0, 0, 0, 0], #
    "R": [0, 1, 0, 0], #
    "S": [1, 0, 0, 0], #
    "T": [[1,0], 0, 0, 0], #
    "U": [1, 0, 0, 0], #
    "V": [0, 0, 0, 0], #
    "W": [0, 0, 0, 0], #
    "X": [0, 0, 0, 0], #
    "Y": [1, 0, 0, 0], #
    "Z": [0, 0, 0, 0],
    "REST": [[1,0], 0, 0, 0],
}

# The new column names
new_columns = [
    "index_inside",
    "middle_fingerprint",
    "middle_inside_to_ring",
    "ring_tape",
]

# --- 2. Process the old CSV and write the new one ---
input_csv  = "sign_language_data_old.csv"
output_csv = "sign_language_data.csv"

def pick_value(v):
    """Return a random choice if v is a list, else return v directly."""
    if isinstance(v, list):
        return random.choice(v)
    return v

with open(input_csv, "r", newline="") as infile, open(output_csv, "w", newline="") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Read and extend header
    header = next(reader)
    header.extend(new_columns)
    writer.writerow(header)

    for row in reader:
        label = row[0]

        if label not in label_to_extra:
            raise ValueError(f"Label '{label}' not found in mapping table.")

        new_feature_values = [pick_value(v) for v in label_to_extra[label]]
        row.extend(new_feature_values)

        writer.writerow(row)

print(f"Finished! Updated file saved as: {output_csv}")