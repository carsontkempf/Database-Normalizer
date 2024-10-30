from unittest.mock import patch
from main import main  # Import the main function from main.py

# Define the sequence of responses as they would be prompted by the program
mock_inputs = [
    "2NF",  # Select Normalization Form
    "student",  # Enter the name of the relation
    "fname, lname, ssn, home_address",  # Enter attributes
    "ssn, home_address",  # Enter primary keys
    "",  # Enter candidate keys
    "",  # Enter foreign keys
    "",
    "",
    "ssn",  # First FD determinant attributes
    "home_address",  # First FD dependent attributes
    "no",  # No more functional dependencies
    "yes",  # Attribute 'fname' atomic check
    "yes",  # Attribute 'lname' atomic check
    "yes",  # Attribute 'ssn' atomic check
    "yes",  # Attribute 'home_address' atomic check
]

# Patch 'input' function to use predefined inputs
with patch("builtins.input", side_effect=mock_inputs):
    main()  # Call the main function to run the program with simulated input
