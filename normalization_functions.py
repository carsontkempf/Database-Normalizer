from classes import Relation, FunctionalDependency

relation_counter = 1

# Normalization Functions


# 1NF: Detect if an attribute is of type list
def is_1NF(relation):
    violation_attributes = []
    for attr in relation.attributes:
        is_non_atomic = input(
            f"Is '{attr}' a non-atomic attribute (e.g., list or composite)? (yes/no): "
        ).lower()
        if is_non_atomic == "yes":
            violation_attributes.append(attr)
    return violation_attributes


# 2NF: Detect if there are partial functional dependencies
def is_2NF(relation):
    partial_dependencies = []
    for fd in relation.functional_dependencies:
        if any(pk not in fd.get_x() for pk in relation.primary_key):
            partial_dependencies.append(fd)
    return partial_dependencies


# 3NF: Detect if there are any transitive functional dependencies
def is_3NF(relation):
    transitive_dependencies = []
    for fd in relation.functional_dependencies:
        if all(pk not in fd.get_x() for pk in relation.primary_key):
            transitive_dependencies.append(fd)
    return transitive_dependencies


# BCNF: Detect if X is a superkey in X -> Y
def is_BCNF(relation):
    bcnf_violations = []
    for fd in relation.functional_dependencies:
        if not set(fd.get_x()).issuperset(set(relation.primary_key)):
            bcnf_violations.append(fd)
    return bcnf_violations


# 4NF: Detect if X is a superkey or if Y is independently determinable in X -> Y
def is_4NF(relation):
    fourth_nf_violations = []
    for fd in relation.functional_dependencies:
        if (
            not set(fd.get_x()).issuperset(set(relation.primary_key))
            and len(fd.get_y()) > 1
        ):
            fourth_nf_violations.append(fd)
    return fourth_nf_violations


# 5NF: Detect multi-valued relations
def is_5NF(relation):
    multi_valued_dependencies = []
    for fd in relation.functional_dependencies:
        if len(fd.get_y()) > 1 and len(set(fd.get_y())) > 1:
            multi_valued_dependencies.append(fd)
    return multi_valued_dependencies


# Global Functions


# Decompose Relation
# Decompose function updated to ensure correct decomposition flow
def decomposeRelation(parent_relation, violation_attribute):
    global relation_counter

    # Create dynamic primary key format for child relations
    child_1_primary_key = f"R{relation_counter}_id"

    # Create child relation for the violating attribute
    child_relation = Relation(
        f"R{relation_counter}", [violation_attribute, child_1_primary_key]
    )
    relation_counter += 1
    child_relation.add_primary_key(child_1_primary_key)
    child_relation.add_foreign_key(parent_relation.primary_key)

    # Remove the violating attribute from the parent relation
    parent_relation.attributes.remove(violation_attribute)

    # Return the new child relation and the updated parent relation
    return child_relation, parent_relation


# Input Relation
def inputRelation():
    name = input("Enter relation name: ")
    attributes = input("Enter attributes (comma-separated): ").split(",")

    # Example for entering composite and single keys
    print("\nExample for entering keys:")
    print("For a composite key: (ssn, address)")
    print("For a single key: ssn")
    print("For multiple keys: (ssn, address), ssn")
    print()
    # Ask for primary key
    use_default_pk = input("Use default primary key (yes/no)? ").lower()
    if use_default_pk == "yes":
        primary_key = [f"{name}_id"]
    else:
        primary_key = parse_keys(
            input("Enter primary key: ")
        )

    # Foreign and candidate keys input
    foreign_keys = parse_keys(input("Enter foreign keys (comma-separated, if any): "))
    candidate_keys = parse_keys(
        input("Enter candidate keys (if any): ")
    )

    # Create the relation and return
    relation = Relation(name, attributes)
    relation.add_primary_key(primary_key)
    if foreign_keys:
        relation.add_foreign_key(foreign_keys)
    if candidate_keys:
        relation.add_candidate_key(candidate_keys)

    return relation


# Input Functional Dependency
def inputFunctionalDependency(relation):
    lhs = input("Enter functional dependency left-hand side (comma-separated): ").split(
        ","
    )
    rhs = input(
        "Enter functional dependency right-hand side (comma-separated): "
    ).split(",")
    relation.add_functional_dependency(lhs, rhs)


# Input Data for Relation (Optional)
def inputData(relation):
    print(f"Enter data for the relation: {relation.attributes}")
    data = input(
        f"Enter values for {', '.join(relation.attributes)} (comma-separated): "
    ).split(",")
    # Storing data can be added later, this step is for user input simulation


def parse_keys(key_input):
    key_input = key_input.strip()
    if not key_input:
        return []

    keys = []
    composite_keys = key_input.split("),")
    for composite in composite_keys:
        composite = composite.replace("(", "").replace(")", "").strip()
        key_parts = [part.strip() for part in composite.split(",")]
        if len(key_parts) == 1:
            keys.append(key_parts[0])
        else:
            keys.append(key_parts)
    return keys


# Print Relation
def printRelation(relation):
    print(f"Relation Name: {relation.name}")
    print("Attributes:", relation.attributes)
    print("Primary Key:", relation.primary_key)
    print("Foreign Keys:", relation.foreign_keys)
    print("Candidate Keys:", relation.candidate_keys)

    if relation.functional_dependencies:
        print("Functional Dependencies:")
        for fd in relation.functional_dependencies:
            print(f"  {fd}")


def print_description(description):
    print(f"\n{description}\n")
