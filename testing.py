import subprocess

# Define the inputs, including blank lines for 'Enter' keypresses
input_data = [
    "4NF",  # Select normalization form
    "testing",  # Enter relation name
    "A,B,C",  # Enter attributes
    "A,B;B,C;A,C",  # Enter primary keys
    "",  # Press Enter for default candidate keys
    "",  # Press Enter for default foreign keys
    "A,B",  # Determinant attributes for first functional dependency
    "C",  # Dependent attributes
    "yes",  # Add another functional dependency
    "A,C",  # Determinant attributes for second functional dependency
    "B",  # Dependent attributes
    "yes",  # Add another functional dependency
    "B,C",  # Determinant attributes for third functional dependency
    "A",  # Dependent attributes
    "no",  # Stop adding functional dependencies
    "1, 2, 3",  # Enter tuple values
    "no",  # Stop adding data tuples
    "yes",  # Is 'A' atomic?
    "yes",  # Is 'B' atomic?
    "yes",  # Is 'C' atomic?
]

# Convert input_data to a single string with newline characters
input_text = "\n".join(input_data) + "\n"

# Run main.py and pass the input_data as stdin
process = subprocess.Popen(["python3", "main.py"], stdin=subprocess.PIPE, text=True)

# Send input_text to the process and wait for it to complete
output, errors = process.communicate(input=input_text)

print("Simulation Complete.")
