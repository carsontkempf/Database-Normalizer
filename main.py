from helper_functions import *
from classes import *


def normalize_relation(relation, choice):
    if choice == "1NF":
        anomalies = detect_1NF_anomalies(relation)  # Detect Anomalies
        if anomalies:  # Ensure anomalies are handled as a list of lists
            list_of_1NF_relations = decompose_relation(relation, [anomalies])
            print_relation(list_of_1NF_relations)  # Print Relations in 1NF
        else:
            print_relation(relation)
    elif choice == "2NF":
        normalize_relation(relation, "1NF")
        anomalies = detect_2NF_anomalies(relation)
        if anomalies:
            list_of_2NF_relations = decompose_relation(relation, [anomalies])
            print_relation(list_of_2NF_relations)
        else:
            print_relation(relation)
    elif choice == "3NF":
        normalize_relation(relation, "2NF")
        anomalies = detect_3NF_anomalies(relation)
        if anomalies:
            list_of_3NF_relations = decompose_relation(relation, [anomalies])
            print_relation(list_of_3NF_relations)
        else:
            print_relation(relation)
    elif choice == "BCNF":
        normalize_relation(relation, "3NF")
        anomalies = detect_BCNF_anomalies(relation)
        if anomalies:
            list_of_BCNF_relations = decompose_relation(relation, [anomalies])
            print_relation(list_of_BCNF_relations)
        else:
            print_relation(relation)
    elif choice == "4NF":
        normalize_relation(relation, "BCNF")
        anomalies = detect_4NF_anomalies(relation)
        if anomalies:
            list_of_4NF_relations = decompose_relation(relation, [anomalies])
            print_relation(list_of_4NF_relations)
        else:
            print_relation(relation)
    elif choice == "5NF":
        normalize_relation(relation, "4NF")
        anomalies = detect_5NF_anomalies(relation)
        if anomalies:
            list_of_5NF_relations = decompose_relation(relation, [anomalies])
            print_relation(list_of_5NF_relations)
        else:
            print_relation(relation)
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
