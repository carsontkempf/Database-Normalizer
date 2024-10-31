from helper_functions import *
from classes import *


# Main function to control the normalization process based on user input
def main():
    # Prompt user to select the desired normalization form
    normalization_choice = input(
        "Select the Normalization Form (1NF, 2NF, 3NF, BCNF, 4NF, 5NF): "
    ).upper()

    # Initialize relation object by capturing relation details from user input
    relation_object = input_relation()

    # For higher normal forms (2NF+), prompt user to add functional dependencies
    if normalization_choice in ["2NF", "3NF", "BCNF", "4NF", "5NF"]:
        while True:
            input_functional_dependency(relation_object)
            # Ask if the user wants to add more functional dependencies
            more_fds = (
                input("Do you want to add another functional dependency? (yes/no): ")
                .strip()
                .lower()
            )
            if more_fds != "yes":
                break

    # For 4NF and 5NF, prompt user to add data tuples to detect multi-valued dependencies
    if normalization_choice in ["4NF", "5NF"]:
        while True:
            input_data(relation_object)
            # Ask if the user wants to add more data tuples
            more_data = (
                input("Do you want to add another data tuple? (yes/no): ")
                .strip()
                .lower()
            )
            if more_data != "yes":
                break

    # Execute the selected normalization function based on the user's choice
    if normalization_choice == "1NF":
        normalize_1NF(relation_object)
    elif normalization_choice == "2NF":
        normalize_2NF(relation_object)
    elif normalization_choice == "3NF":
        normalize_3NF(relation_object)
    elif normalization_choice == "BCNF":
        normalize_BCNF(relation_object)
    elif normalization_choice == "4NF":
        normalize_4NF(relation_object)
    elif normalization_choice == "5NF":
        normalize_5NF(relation_object)
    else:
        print("Invalid choice")  # Handle invalid normalization choice


# Entry point for script execution
if __name__ == "__main__":
    main()
