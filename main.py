from helper_functions import *
from classes import *


def normalize_relation(relation, choice):
    if choice == "1NF":

        anomalies = detect_1NF_anomalies(relation)

        list_of_1NF_relations = decompose(relation, anomalies)

        print_relation(list_of_1NF_relations)

    elif choice == "2NF":
        # Placeholder: Get Functional Dependencies as input
        # Placeholder: Detect 2NF violations
        # Placeholder: Decompose relation if any violations are found
        normalize_relation(relation, "1NF")
    elif choice == "3NF":
        # Placeholder: Detect 3NF violations
        # Placeholder: Decompose relation if any violations are found
        normalize_relation(relation, "2NF")
    elif choice == "BCNF":
        # Placeholder: Detect BCNF violations
        # Placeholder: Decompose relation if any violations are found
        normalize_relation(relation, "3NF")
    elif choice == "4NF":
        # Placeholder: Get data instances as input
        # Placeholder: Detect 4NF violations
        # Placeholder: Decompose relation if any violations are found
        normalize_relation(relation, "BCNF")
    elif choice == "5NF":
        # Placeholder: Detect 5NF violations
        # Placeholder: Decompose relation if any violations are found
        normalize_relation(relation, "4NF")
    else:
        print("Invalid choice")

        normalization_choice = input(
            "Select the Normalization Form (1NF, 2NF, 3NF, BCNF, 4NF, 5NF): "
        ).upper()

        relation_object = input_relation()

        normalize_relation(relation_object, normalization_choice)


def main():
    normalization_choice = input(
        "Select the Normalization Form (1NF, 2NF, 3NF, BCNF, 4NF, 5NF): "
    ).upper()

    relation_object = input_relation()

    if normalization_choice in ["2NF", "3NF", "BCNF", "4NF", "5NF"]:
        add_functional_dependency(relation_object)

    if normalization_choice in ["4NF", "5NF"]:
        add_data(relation_object)

    normalize_relation(relation_object, normalization_choice)


if __name__ == "__main__":
    main()
