from normalization_functions import (
    inputRelation,
    is_1NF,
    decomposeRelation,
    printRelation,
    inputFunctionalDependency,
    print_description,
)


def main():
    print_description("Program Start")

    # Get user input for the relation
    relation = inputRelation()

    print_description("Enter functional dependencies (if any):")
    more_fds = input("Add functional dependencies? (yes/no): ").lower()
    while more_fds == "yes":
        inputFunctionalDependency(relation)
        more_fds = input("Add more functional dependencies? (yes/no): ").lower()

    print_description("Print initial relation")
    print("Initial Relation:")
    printRelation(relation)

    # List to store all relations
    all_relations = [relation]

    print_description("Check 1NF")
    violation_attributes_1NF = is_1NF(relation)
    if violation_attributes_1NF:
        print(f"1NF Violation detected in attributes: {violation_attributes_1NF}")

        # Decompose for each violating attribute and update the parent relation
        for attr in violation_attributes_1NF:
            child_relation, relation = decomposeRelation(relation, attr)
            all_relations.append(child_relation)

        # Append the final updated parent relation
        all_relations.append(relation)

    else:
        print("No 1NF violation detected.")

    # Print only the first 3 relations: 2 child relations and the final parent relation
    print_description("Print all normalized relations")
    for i, rel in enumerate(
        all_relations[:3], 1
    ):  # Ensure only 3 relations are printed
        print(f"\nRelation {i}:")
        printRelation(rel)


if __name__ == "__main__":
    main()
