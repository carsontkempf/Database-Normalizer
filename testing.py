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
    "no",  # no = the attribute is non-atomic and needs decomposed to a new relation
    "no",  # no = the attribute is non-atomic and needs decomposed to a new relation
    "yes",
]

input_data_2NF = [
    "2NF",
    "student",
    "fname, lname, ssn, home_address",
    "fname, lname",
    "",
    "",
    "lname",  # Determinant = a subset of the primary key but not the entire primary key
    "home_address",  # Dependent = a non-key attribute, therefore partial functional dependency
    "no",
    "yes",
    "yes",
    "yes",
    "yes",
]

input_data_3NF = [
    "3NF",
    "student",
    "fname, lname, ssn, home_address, phone_number",
    "",
    "",
    "",
    "student_id",  # Determinant = primary key
    "ssn",  # Dependent = non-key
    "yes",
    "ssn",  # Determinant = non-key attribute determined by another functional dependency on the primary key
    "home_address",  # Dependent = non-key attribute, therefore transitive functional dependency
    "no",
    "yes",
    "yes",
    "yes",
    "yes",
    "no",
    "yes",
]

input_data_BCNF = [
    "BCNF",
    "student",
    "fname, lname, ssn, address",
    "fname, lname",
    "",
    "",
    "fname, lname, address",  # Determinant = primary key + another attribute, therefore the functional dependency isn't in BCNF
    "ssn",  # Dependent
    "no",
    "yes",
    "yes",
    "yes",
    "yes",
]

input_data_4NF = [
    "4NF",
    "student",
    "fname, lname",
    "",
    "",
    "",
    "student_id",
    "fname, lname",
    "no",
    "james, cunningham, 1",  # data insertion
    "yes",
    "trevin, distefano, 1",  # data insertion with the primary key equaling another tuple in the relation: "james, cunningham, 1", therefore a MVD is detected
    "no",
    "yes",
    "yes",
    "yes",
    "2",
]

input_data_5NF = [
    "5NF",
    "music_purchase",
    "customer_id,artist_id,song_id",
    "customer_id,artist_id;artist_id,song_id;customer_id,song_id",
    "",
    "",
    "customer_id,artist_id",  # Determinant = ONE of the primary / candidate keys
    "song_id",  # Dependent = a key attribute
    "yes",
    "customer_id,song_id",
    "artist_id",
    "yes",
    "artist_id,song_id",
    "customer_id",
    "no",
    "1, 2, 3",
    "yes",
    "1, 3, 4",
    "yes",
    "2, 2, 3",
    "yes",
    "2, 3, 4",
    "no",
    "yes",
    "yes",
    "yes",
]

# Prompt user to select a normalization form
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

# Use patch to simulate input() calls with selected data for testing
with patch("builtins.input") as mock_input:
    mock_input.side_effect = selected_input_data
    main()  # Run the main function with mocked inputs
