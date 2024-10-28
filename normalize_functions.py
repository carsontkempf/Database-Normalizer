from classes import *
from helper_functions import *


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(f"Starting {stage_name}")
    print_divider()


def fix_partial_functional_dependencies(parent_relation, decomposed_relation):
    adjusted_fds = []
    for fd in parent_relation.functional_dependencies:
        fd_x = set(fd.get_x())
        fd_y = set(fd.get_y())

        # Check if both X and Y attributes are present in the decomposed relation
        if fd_x.issubset(decomposed_relation.attributes) and fd_y.issubset(
            decomposed_relation.attributes
        ):
            # Adjust the FD to use primary key if partial dependency
            if fd_x != set(parent_relation.primary_key):
                fd.adjust_to_primary_key(parent_relation.primary_key)

            # Append adjusted or unmodified FD after ensuring correctness
            adjusted_fds.append(fd)

    return adjusted_fds


def fix_transitive_functional_dependencies(relation):
    primary_key = relation.primary_key[:]
    transitive_deps = {}
    new_fds = []

    # Step 1: Identify transitive dependencies
    for fd in relation.functional_dependencies:
        X = fd.get_x()
        Y = fd.get_y()

        # If X is not a superkey but is still part of a transitive dependency
        if not set(X).issubset(primary_key):
            # Track each non-key attribute dependency as a transitive dependency
            for y in Y:
                if y not in primary_key:
                    transitive_deps.setdefault(tuple(primary_key), set()).add(y)
        else:
            # If it's a direct dependency on the primary key, keep it in the new list
            new_fds.append(fd)

    # Step 2: Replace transitive dependencies with primary_key -> all transitive dependents
    for pk, dependent_attrs in transitive_deps.items():
        # Add a new consolidated FD for primary key -> (all transitive dependent attributes)
        consolidated_fd = FunctionalDependency(list(pk), list(dependent_attrs))
        new_fds.append(consolidated_fd)
        print(
            f"Replacing transitive dependencies with consolidated FD: {list(pk)} -> {list(dependent_attrs)}"
        )

    return new_fds


def exclude_duplicate_relations(decomposed_relation, decomposed_relation_list):
    new_attrs = set(decomposed_relation.attributes)
    to_remove = []

    for existing_relation in decomposed_relation_list:
        existing_attrs = set(existing_relation.attributes)

        if new_attrs == existing_attrs:
            print(
                f"Skipping exact duplicate relation: {decomposed_relation.attributes}"
            )
            return decomposed_relation_list  # Skip adding duplicate
        elif existing_attrs.issubset(new_attrs):
            print(
                f"Removing subset relation: {existing_relation.attributes} in favor of {decomposed_relation.attributes}"
            )
            to_remove.append(existing_relation)  # Mark subset for removal
        elif new_attrs.issubset(existing_attrs):
            print(
                f"Skipping subset relation: {decomposed_relation.attributes} since {existing_relation.attributes} already exists"
            )
            return decomposed_relation_list  # Skip adding subset

    # Remove marked subset relations
    for relation in to_remove:
        decomposed_relation_list.remove(relation)

    # Add the new relation after checking duplicates
    decomposed_relation_list.append(decomposed_relation)
    print(f"Adding new relation: {decomposed_relation.attributes}")

    return decomposed_relation_list


# Input: relation object, a list of anomalies
# anomaly_list = ['abc', 'def|ghi', 'jkl']
# Output: list of relation objects
# Main decomposition function for detected anomalies
def decompose_relation(parent_relation, anomaly_list):
    if not anomaly_list:
        return (
            []
        )  # No anomalies, so return an empty list to prevent adding the original relation

    decomposed_relation_list = []
    count = 1
    all_parent_attributes = parent_relation.attributes[:]

    print("\nStarting decomposition for anomalies...\n")

    # Process each anomaly to create new relations
    for anomaly in anomaly_list:
        decomposed_relation = Relation(name=str(count), attributes=[])
        decomposed_relation.name = f"Relation_{count}"  # Use unique name format

        # Handle non-nested anomalies directly
        if "|" not in anomaly:
            if anomaly in all_parent_attributes:
                all_parent_attributes.remove(anomaly)
            decomposed_relation.attributes.append(anomaly)
        else:
            # Handle nested anomalies
            attributes = anomaly.split("|")
            for attr in attributes:
                if attr in all_parent_attributes:
                    all_parent_attributes.remove(attr)
                decomposed_relation.attributes.append(attr)

        # Ensure primary key is included in the decomposed relation
        for pk in parent_relation.primary_key:
            if pk not in decomposed_relation.attributes:
                decomposed_relation.attributes.append(pk)

        # Set primary keys, foreign keys, and candidate keys from parent
        decomposed_relation.primary_key = parent_relation.primary_key[:]
        decomposed_relation.foreign_keys = parent_relation.foreign_keys[:]
        decomposed_relation.candidate_keys = parent_relation.candidate_keys[:]

        # Adjust functional dependencies
        decomposed_relation.functional_dependencies = (
            fix_partial_functional_dependencies(parent_relation, decomposed_relation)
        )

        # Detect and fix transitive dependencies
        decomposed_relation.functional_dependencies = (
            fix_transitive_functional_dependencies(decomposed_relation)
        )

        # Add newly created relation to list
        decomposed_relation_list = exclude_duplicate_relations(
            decomposed_relation, decomposed_relation_list
        )

        count += 1

    # Add remaining attributes as a new relation if not empty
    if all_parent_attributes:
        remaining_relation = Relation(name=str(count), attributes=all_parent_attributes)
        remaining_relation.name = f"Relation_{count}"  # Ensure a unique name

        # Ensure primary key is added to remaining relation
        for pk in parent_relation.primary_key:
            if pk not in remaining_relation.attributes:
                remaining_relation.attributes.append(pk)

        remaining_relation.primary_key = parent_relation.primary_key[:]
        remaining_relation.foreign_keys = parent_relation.foreign_keys[:]
        remaining_relation.candidate_keys = parent_relation.candidate_keys[:]

        # Adjust functional dependencies for the remaining relation
        remaining_relation.functional_dependencies = (
            fix_partial_functional_dependencies(parent_relation, remaining_relation)
        )

        # Detect and fix transitive dependencies for the remaining relation
        remaining_relation.functional_dependencies = (
            fix_transitive_functional_dependencies(remaining_relation)
        )

        decomposed_relation_list = exclude_duplicate_relations(
            remaining_relation, decomposed_relation_list
        )

    return decomposed_relation_list


def normalize_1NF(relation):
    print_normalization_stage("1NF Normalization")
    anomalies = detect_1NF_anomalies(relation)

    print_normalization_stage("Final 1NF Relations")

    if anomalies:
        list_of_1NF_relations = decompose_relation(relation, anomalies)
        for decomposed_relation in list_of_1NF_relations:
            decomposed_relation.print_relation()
        return list_of_1NF_relations
    else:
        relation.print_relation()
        return [relation]


def normalize_2NF(relation):
    print_normalization_stage("2NF Normalization")
    list_of_1NF_relations = normalize_1NF(relation)
    final_2NF_relations = []

    for rel in list_of_1NF_relations:
        anomalies = detect_2NF_anomalies(rel)
        if anomalies:
            list_of_2NF_relations = decompose_relation(rel, anomalies)
            final_2NF_relations.extend(list_of_2NF_relations)
        else:
            final_2NF_relations.append(rel)

    print_normalization_stage("Final 2NF Relations")
    # Ensure each final relation is printed once with unique identifiers
    for index, final_relation in enumerate(final_2NF_relations, start=1):
        final_relation.name = index
        final_relation.print_relation()  # Print each relation

    return final_2NF_relations


def normalize_3NF(relation):
    print_normalization_stage("3NF Normalization")
    relations = normalize_2NF(relation)
    final_3NF_relations = []

    for rel in relations:
        anomalies = detect_3NF_anomalies(rel)
        if anomalies:
            list_of_3NF_relations = decompose_relation(rel, anomalies)
            final_3NF_relations.extend(list_of_3NF_relations)
        else:
            final_3NF_relations.append(rel)

    print_normalization_stage("Final 3NF Relations")
    for final_relation in final_3NF_relations:
        final_relation.print_relation()

    return final_3NF_relations


def normalize_BCNF(relation):
    print_normalization_stage("BCNF Normalization")
    relations = normalize_3NF(relation)
    anomalies = detect_BCNF_anomalies(relation)
    if anomalies:
        list_of_BCNF_relations = decompose_relation(relation, anomalies)
        for decomposed_relation in list_of_BCNF_relations:
            decomposed_relation.print_relation()
        return list_of_BCNF_relations
    else:
        relation.print_relation()
        return relations


def normalize_4NF(relation):
    print_normalization_stage("4NF Normalization")
    relations = normalize_BCNF(relation)
    anomalies = detect_4NF_anomalies(relation)
    if anomalies:
        list_of_4NF_relations = decompose_relation(relation, anomalies)
        for decomposed_relation in list_of_4NF_relations:
            decomposed_relation.print_relation()
        return list_of_4NF_relations
    else:
        relation.print_relation()
        return relations


def normalize_5NF(relation):
    print_normalization_stage("5NF Normalization")
    relations = normalize_4NF(relation)
    anomalies = detect_5NF_anomalies(relation)
    if anomalies:
        list_of_5NF_relations = decompose_relation(relation, anomalies)
        for decomposed_relation in list_of_5NF_relations:
            decomposed_relation.print_relation()
        return list_of_5NF_relations
    else:
        relation.print_relation()
        return relations


# --------------------------------- Anomaly Functions ---------------------------------
# Anomaly Detection
def detect_1NF_anomalies(relation):
    anomalies = []
    for attribute in relation.attributes:
        is_atomic = input(f"Is '{attribute}' atomic? (yes/no): ").strip().lower()
        if is_atomic == "no":
            anomalies.append(attribute)
    return anomalies


def detect_2NF_anomalies(relation):
    anomalies = []
    primary_key = relation.primary_key[:]
    all_keys = primary_key[:]
    for key in relation.candidate_keys + relation.foreign_keys:
        all_keys.extend(key)

    non_keys = [attr for attr in relation.attributes if attr not in all_keys]
    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()
        if set(X).issubset(all_keys) and set(X) != set(primary_key):
            non_key_Y = [y for y in Y if y in non_keys]
            if non_key_Y:
                anomalies.append("|".join(non_key_Y))
    return anomalies


def detect_3NF_anomalies(relation):
    anomalies = []
    primary_key = relation.primary_key[:]
    all_keys = primary_key[:] + relation.candidate_keys + relation.foreign_keys

    # Identify non-key attributes
    non_keys = [attr for attr in relation.attributes if attr not in all_keys]

    for fd in relation.functional_dependencies:
        X = fd.get_x()  # Determinant (left side of FD)
        Y = fd.get_y()  # Dependent attributes (right side of FD)

        # Check if X is not a superkey (does not fully determine the primary key)
        if not set(primary_key).issubset(set(X)):
            for y in Y:
                # Check for transitive dependency if y is a non-key and depends on another non-key attribute
                if y in non_keys:
                    # Create anomaly with primary key and transitive attributes
                    transitive_anomaly = primary_key + X + Y
                    transitive_anomaly_str = "|".join(transitive_anomaly)

                    # Add to anomalies in format "A|B|C"
                    if transitive_anomaly_str not in anomalies:
                        anomalies.append(transitive_anomaly_str)

    return anomalies
