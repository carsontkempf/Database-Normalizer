from classes import Relation, FunctionalDependency


# Normalization Functions

# 1NF: Detect if an attribute is of type list
def is_1NF(relation):
    violation_attributes = []
    for attr in relation.attributes:
        is_non_atomic = input(f"Is '{attr}' a non-atomic attribute (e.g., list or composite)? (yes/no): ").lower()
        if is_non_atomic == 'yes':
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
        if not set(fd.get_x()).issuperset(set(relation.primary_key)) and len(fd.get_y()) > 1:
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
def decomposeRelation(parent_relation, violation_attribute):
    # Create child relation 1 with violation attribute and parent's primary key
    child_relation_1 = Relation([violation_attribute] + parent_relation.primary_key)
    child_relation_1.add_primary_key(violation_attribute)
    child_relation_1.add_foreign_key(parent_relation.primary_key)

    # Create child relation 2 with remaining attributes without the violation attribute
    remaining_attributes = [attr for attr in parent_relation.attributes if attr != violation_attribute]
    child_relation_2 = Relation(remaining_attributes)
    child_relation_2.add_primary_key(parent_relation.primary_key)

    # Remove the violation attribute from the parent relation
    parent_relation.attributes.remove(violation_attribute)

    return child_relation_1, child_relation_2


# Input Relation
def inputRelation():
    name = input("Enter relation name: ")
    attributes = input("Enter attributes (comma-separated): ").split(",")
    primary_key = input("Enter primary key (comma-separated, default 'id'): ").split(",")
    foreign_keys = input("Enter foreign keys (comma-separated, if any): ").split(",")
    candidate_keys = input("Enter candidate keys (comma-separated, if any): ").split(",")

    relation = Relation(attributes)
    relation.add_primary_key(primary_key if primary_key != [''] else ['id'])
    if foreign_keys != ['']:
        relation.add_foreign_key(foreign_keys)
    if candidate_keys != ['']:
        relation.add_candidate_key(candidate_keys)

    return relation


# Input Functional Dependency
def inputFunctionalDependency(relation):
    lhs = input("Enter functional dependency left-hand side (comma-separated): ").split(",")
    rhs = input("Enter functional dependency right-hand side (comma-separated): ").split(",")
    relation.add_functional_dependency(lhs, rhs)


# Input Data for Relation (Optional)
def inputData(relation):
    print(f"Enter data for the relation: {relation.attributes}")
    data = input(f"Enter values for {', '.join(relation.attributes)} (comma-separated): ").split(",")
    # Storing data can be added later, this step is for user input simulation


# Print Relation
def printRelation(relation):
    print(f"Relation Name: {relation.name}")
    print("Attributes:", relation.attributes)
    print("Primary Key:", relation.primary_key)
    print("Foreign Keys:", relation.foreign_keys)
    print("Candidate Keys:", relation.candidate_keys)
    print("Functional Dependencies:")
    for fd in relation.functional_dependencies:
        print(f"  {fd}")
