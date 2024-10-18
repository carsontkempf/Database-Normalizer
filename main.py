from normalization_functions import (
    inputRelation,
    is_1NF,
    is_2NF,
    is_3NF,
    is_BCNF,
    is_5NF,
    decomposeRelation,
    printRelation,
    inputFunctionalDependency,
    print_spaced,
)


def main():
    print_spaced("Start Normalization...")

    # User inputs their relation to be normalized
    relation = inputRelation()

    print_spaced("Enter functional dependencies (if any):")

    # User inputs ALL functional dependencies for their relation
    more_fds = input("Add functional dependencies? (yes/no): ").lower()
    while more_fds == "yes":
        inputFunctionalDependency(relation)
        more_fds = input("Add more functional dependencies? (yes/no): ").lower()

    # Outputs initial relation
    print_spaced("Initial Relation:")
    printRelation(relation)

    # Initialize the final relation list
    all_relations = []

    # ----- Normalizing to 1NF -----
    print_spaced("Check 1NF")

    violation_attributes_1NF = is_1NF(relation)
    if violation_attributes_1NF:

        print_spaced(
            f"1NF Violation detected in attributes: {violation_attributes_1NF}"
        )

        for attr in violation_attributes_1NF:
            child_relation, relation = decomposeRelation(relation, attr)
            all_relations.append(child_relation)

        all_relations.append(relation)

    else:
        print("No 1NF violation detected.")

    # ----- Normalizing to 2NF -----
    print_spaced("Check 2NF")

    violation_attributes_2NF = is_2NF(relation)
    if violation_attributes_2NF:
        print(f"2NF Violation detected in attributes: {violation_attributes_2NF}")

        # Decompose for each violating attribute
        for attr in violation_attributes_2NF:
            child_relation, relation = decomposeRelation(relation, attr)
            all_relations.append(child_relation)

        all_relations.append(relation)

    else:
        print("No 2NF violation detected.")

    # ----- Normalizing to 3NF -----
    print_spaced("Check 3NF")

    # ----- Normalizing to BCNF -----
    print_spaced("Check BCNF")

    # ----- Normalizing to 4NF -----
    print_spaced("Check 4NF")

    # ----- Normalizing to 5NF -----
    print_spaced("Check 5NF")

    # ----- Print all remaining relations after normalization -----
    print("Final Relations:")

    for i, rel in enumerate(all_relations, 1):
        print_spaced(f"\nRelation {i}:")
        printRelation(rel)


if __name__ == "__main__":
    main()
