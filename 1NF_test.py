from unittest.mock import patch
from main import main  # Import the main function from main.py

# Define the sequence of responses as they would be prompted by the program for 1NF
mock_inputs = [
    "1NF",  # Select Normalization Form
    "student",  # Enter the name of the relation
    "fname, lname, phone_number, address",  # Enter attributes
    "",  # Enter primary keys (use default)
    "",  # Enter candidate keys
    "",  # Enter foreign keys
    "",
    "yes",  # Attribute 'fname' atomic check
    "yes",  # Attribute 'lname' atomic check
    "no",  # Attribute 'phone_number' atomic check
    "no",  # Attribute 'address' atomic check
    "yes",  # Attribute 'student_id' atomic check (default primary key)
]

# Patch 'input' function to use predefined 1NF-specific inputs
with patch("builtins.input", side_effect=mock_inputs):
    main()  # Call the main function to run the program with simulated 1NF inputs
