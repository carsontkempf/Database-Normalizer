from unittest.mock import patch
from main import main  # Import the main function from main.py

# Define the sequence of responses as they would be prompted by the program
mock_inputs = [
    "5NF",  # Select Normalization Form
    "student",  # Enter the name of the relation
    "A,B,C",  # Enter attributes
    "A,B;B,C;A,C",  # Enter primary keys
    "",  # Enter candidate keys
    "",  # Enter foreign keys
    "A,B",  # First FD determinant attributes
    "C",  # First FD dependent attributes
    "yes",  # Add another functional dependency
    "B,C",  # Second FD determinant attributes
    "A",  # Second FD dependent attributes
    "yes",  # Add another functional dependency
    "A,C",  # Third FD determinant attributes
    "B",  # Third FD dependent attributes
    "no",  # No more functional dependencies
    "A1,B1,C1",  # First data tuple
    "yes",  # Add another data tuple
    "A1,B2,C1",  # Second data tuple
    "yes",  # Add another data tuple
    "A2,B1,C2",  # Third data tuple
    "yes",  # Add another data tuple
    "A2,B2,C2",  # Fourth data tuple
    "no",  # No more data tuples
    "yes",  # Attribute 'A' atomic check
    "yes",  # Attribute 'B' atomic check
    "yes",  # Attribute 'C' atomic check
]

# Patch 'input' function to use predefined inputs
with patch("builtins.input", side_effect=mock_inputs):
    main()  # Call the main function to run the program with simulated input
