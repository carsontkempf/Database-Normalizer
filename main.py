from helper_functions import *
from classes import *


def main():
    normalization_choice = input(
        "Select the Normalization Form (1NF, 2NF, 3NF, BCNF, 4NF, 5NF): "
    ).upper()

    relation_object = input_relation()

    if normalization_choice in ["2NF", "3NF", "BCNF", "4NF", "5NF"]:
        while True:
            input_functional_dependency(relation_object)
            more_fds = (
                input("Do you want to add another functional dependency? (yes/no): ")
                .strip()
                .lower()
            )
            if more_fds != "yes":
                break

    if normalization_choice in ["4NF", "5NF"]:
        while True:
            input_data(relation_object)
            more_data = (
                input("Do you want to add another data tuple? (yes/no): ")
                .strip()
                .lower()
            )
            if more_data != "yes":
                break

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
        print("Invalid choice")


if __name__ == "__main__":
    main()
