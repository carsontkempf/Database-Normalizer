from unittest.mock import patch
from main import main  # Import the main function from main.py

# Define various input_data lists for each normalization option
input_data_1NF = [
    "1NF",
    "student",
    "fname, lname, ssn, address",
    "",
    "",
    "",
    "yes",
    "yes",
    "no",
    "no",
    "yes",  # Is 'student_id' atomic?
]

input_data_2NF = [
    "2NF",
    "student",
    "fname, lname, ssn, home_address",
    "fname, lname",
    "",
    "",
    "lname",
    "home_address",
    "no",
    "yes",
    "yes",
    "yes",
    "yes",
]

input_data_3NF = [
    "3NF",  # Select normalization form
    "student",  # Enter relation name
    "fname, lname, ssn, home_address, phone_number",  # Enter attributes
    "",  # Enter primary keys (leave blank as in the example)
    "",  # Enter candidate keys (leave blank as in the example)
    "",  # Enter foreign keys (leave blank as in the example)
    "student_id",  # Determinant attributes for first functional dependency
    "ssn",  # Dependent attributes for first functional dependency
    "yes",  # Add another functional dependency
    "ssn",  # Determinant attributes for second functional dependency
    "home_address",  # Dependent attributes for second functional dependency
    "no",  # Stop adding functional dependencies
    "yes",  # Is 'fname' atomic?
    "yes",  # Is 'lname' atomic?
    "yes",  # Is 'ssn' atomic?
    "yes",  # Is 'home_address' atomic?
    "no",  # Is 'phone_number' atomic?
    "yes",  # Is 'student_id' atomic?
]

input_data_BCNF = [
    "BCNF",  # Select normalization form
    "student",  # Enter relation name
    "fname, lname, ssn, address",  # Enter attributes
    "fname, lname",  # Enter primary keys
    "",  # Enter candidate keys (leave blank as in the example)
    "",  # Enter foreign keys (leave blank as in the example)
    "fname, lname, address",  # Determinant attributes for functional dependency
    "ssn",  # Dependent attribute for functional dependency
    "no",  # Stop adding functional dependencies
    "yes",  # Is 'fname' atomic?
    "yes",  # Is 'lname' atomic?
    "yes",  # Is 'ssn' atomic?
    "yes",  # Is 'address' atomic?
]

input_data_4NF = [
    "4NF",  # Select normalization form
    "student",  # Enter relation name
    "fname, lname",  # Enter attributes
    "",  # Enter primary keys (leave blank as in the example)
    "",  # Enter candidate keys (leave blank as in the example)
    "",  # Enter foreign keys (leave blank as in the example)
    "student_id",  # Determinant attribute for functional dependency
    "fname, lname",  # Dependent attributes for functional dependency
    "no",  # Stop adding functional dependencies
    "james, cunningham, 1",  # Enter tuple values for first data tuple
    "yes",  # Confirm to add another data tuple
    "trevin, distefano, 1",  # Enter tuple values for second data tuple
    "no",  # Stop adding data tuples
    "yes",  # Confirm 'fname' is atomic
    "yes",  # Confirm 'lname' is atomic
    "yes",  # Is 'student_id' atomic?
]

input_data_5NF = [
    "5NF",  # Select 5NF normalization form
    "music_purchase",  # Relation name
    "customer_id,artist_id,song_id",  # Attributes
    "customer_id,artist_id;artist_id,song_id;customer_id,song_id",  # Primary keys
    "",  # Default candidate keys
    "",  # Default foreign keys
    "customer_id,artist_id",  # Determinant attributes for first functional dependency
    "song_id",  # Dependent attribute
    "yes",  # Add another functional dependency
    "customer_id,song_id",  # Determinant attributes for second functional dependency
    "artist_id",  # Dependent attribute
    "yes",  # Add another functional dependency
    "artist_id,song_id",  # Determinant attributes for third functional dependency
    "customer_id",  # Dependent attribute
    "no",  # Stop adding functional dependencies
    "1, 2, 3",  # Data tuple 1
    "yes",  # Add another data tuple
    "1, 3, 4",  # Data tuple 2
    "yes",  # Add another data tuple
    "2, 2, 3",  # Data tuple 3
    "yes",  # Add another data tuple
    "2, 3, 4",  # Data tuple 4
    "no",  # Stop adding data tuples
    "yes",  # Is 'customer_id' atomic?
    "yes",  # Is 'artist_id' atomic?
    "yes",  # Is 'song_id' atomic?
]

# Prompt the user to select a normalization form
user_choice = input("Select normalization form (1, 2, 3, B, 4, 5): ")

# Choose the appropriate input_data list based on user choice
if user_choice == "1":
    selected_input_data = input_data_1NF
elif user_choice == "2":
    selected_input_data = input_data_2NF
elif user_choice == "3":
    selected_input_data = input_data_3NF
elif user_choice == "B":
    selected_input_data = input_data_BCNF
elif user_choice == "4":
    selected_input_data = input_data_4NF
elif user_choice == "5":
    selected_input_data = input_data_5NF
else:
    raise ValueError("Invalid choice! Please select 1, 2, 3, B, 4, or 5.")

# Use patch to simulate input() calls
with patch("builtins.input") as mock_input:
    # Configure mock to return each value in selected_input_data on each call to input()
    mock_input.side_effect = selected_input_data
    main()  # Run the main function, which will now use the selected mocked inputs
