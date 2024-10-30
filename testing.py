from unittest.mock import patch
from main import main  # Import the main function from main.py

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

# Use patch to simulate input() calls
with patch("builtins.input") as mock_input:
    # Configure mock to return each value in input_data on each call to input()
    mock_input.side_effect = input_data
    main()  # Run the main function, which will now use mocked inputs
