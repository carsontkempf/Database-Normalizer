from normalization_functions import (
    is_1NF,
    is_2NF,
    is_3NF,
    is_BCNF,
    is_4NF,
    is_5NF,
    decomposeRelation,
    inputRelation,
    inputFunctionalDependency,
    inputData,
    printRelation,
)


def main():
    relation = inputRelation()

    # Input functional dependencies for the relation
    more_fds = input("Add functional dependencies? (yes/no): ").lower()
    while more_fds == "yes":
        inputFunctionalDependency(relation)
        more_fds = input("Add more functional dependencies? (yes/no): ").lower()

    print("Initial Relation:")
    printRelation(relation)

    # Check 1NF
    violation_attributes_1NF = is_1NF(relation)
    if violation_attributes_1NF:
        print(f"1NF Violation detected in attributes: {violation_attributes_1NF}")
        child_rel_1, child_rel_2 = decomposeRelation(
            relation, violation_attributes_1NF[0]
        )
        print("Child Relation 1:")
        printRelation(child_rel_1)
        print("Child Relation 2:")
        printRelation(child_rel_2)
    else:
        print("No 1NF violation detected.")

    # Check 2NF
    violation_fds_2NF = is_2NF(relation)
    if violation_fds_2NF:
        print(f"2NF Violation detected in functional dependencies: {violation_fds_2NF}")

    # Check 3NF
    violation_fds_3NF = is_3NF(relation)
    if violation_fds_3NF:
        print(f"3NF Violation detected in functional dependencies: {violation_fds_3NF}")

    # Check BCNF
    violation_fds_BCNF = is_BCNF(relation)
    if violation_fds_BCNF:
        print(
            f"BCNF Violation detected in functional dependencies: {violation_fds_BCNF}"
        )

    # Check 4NF
    violation_fds_4NF = is_4NF(relation)
    if violation_fds_4NF:
        print(f"4NF Violation detected in functional dependencies: {violation_fds_4NF}")

    # Check 5NF
    violation_fds_5NF = is_5NF(relation)
    if violation_fds_5NF:
        print(f"5NF Violation detected in functional dependencies: {violation_fds_5NF}")


if __name__ == "__main__":
    main()
