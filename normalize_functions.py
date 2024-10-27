from classes import *
from helper_functions import *


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(f"Starting {stage_name}")
    print_divider()


# Input: relation object, a list of anomalies
# anomaly_list = ['abc', 'def|ghi', 'jkl']
# Output: list of relation objects
# Main decomposition function for detected anomalies
def decompose_relation(parent_relation, anomaly_list):
    if not anomaly_list:
        return [parent_relation]  # No anomalies, return parent relation

    decomposed_relation_list = []
    count = 1
    all_parent_attributes = parent_relation.attributes[:]

    print("\nStarting decomposition for anomalies...\n")

    for anomaly in anomaly_list:
        decomposed_relation = Relation(name=str(count), attributes=[])
        decomposed_relation.name = count

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

        # Include primary keys
        for pk in parent_relation.primary_key:
            if pk not in decomposed_relation.attributes:
                decomposed_relation.attributes.append(pk)

        # Set primary keys, foreign keys, and candidate keys from parent
        decomposed_relation.primary_key = parent_relation.primary_key[:]
        decomposed_relation.foreign_keys = parent_relation.foreign_keys[:]
        decomposed_relation.candidate_keys = parent_relation.candidate_keys[:]

        # Update functional dependencies for partial dependencies
        adjusted_fds = []
        for fd in parent_relation.functional_dependencies:
            if set(fd.get_y()).intersection(decomposed_relation.attributes):
                if set(fd.get_x()) != set(parent_relation.primary_key):
                    # Adjust the FD to use primary key as X if partial dependency
                    fd.adjust_to_primary_key(parent_relation.primary_key)
                # Append adjusted or unmodified FD after ensuring correctness
                adjusted_fds.append(fd)

        # After all FDs are adjusted, assign to the relation and output
        decomposed_relation.functional_dependencies = adjusted_fds
        print(f"Adding new relation: {decomposed_relation.attributes}")
        decomposed_relation_list.append(decomposed_relation)

        # Check for duplicates or subsets
        new_attrs = set(decomposed_relation.attributes)
        to_remove = []

        for existing_relation in decomposed_relation_list:
            existing_attrs = set(existing_relation.attributes)
            if new_attrs == existing_attrs:
                print(
                    f"Skipping exact duplicate relation: {decomposed_relation.attributes}"
                )
                break
            elif existing_attrs.issubset(new_attrs):
                print(
                    f"Removing subset relation: {existing_relation.attributes} in favor of {decomposed_relation.attributes}"
                )
                to_remove.append(existing_relation)
            elif new_attrs.issubset(existing_attrs):
                print(
                    f"Skipping subset relation: {decomposed_relation.attributes} since {existing_relation.attributes} already exists"
                )
                break
        else:
            for relation in to_remove:
                decomposed_relation_list.remove(relation)
            print(f"Adding new relation: {decomposed_relation.attributes}")
            decomposed_relation_list.append(decomposed_relation)

        count += 1

    # Ensure all remaining attributes are accounted for
    if all_parent_attributes:
        remaining_relation = Relation(name=str(count), attributes=all_parent_attributes)
        remaining_relation.name = count
        remaining_relation.primary_key = parent_relation.primary_key[:]
        remaining_relation.foreign_keys = parent_relation.foreign_keys[:]
        remaining_relation.candidate_keys = parent_relation.candidate_keys[:]
        remaining_relation.functional_dependencies = (
            parent_relation.functional_dependencies[:]
        )

        new_attrs = set(remaining_relation.attributes)
        to_remove = []

        for existing_relation in decomposed_relation_list:
            existing_attrs = set(existing_relation.attributes)
            if new_attrs == existing_attrs:
                print(
                    f"Skipping exact duplicate relation: {remaining_relation.attributes}"
                )
                break
            elif existing_attrs.issubset(new_attrs):
                print(
                    f"Removing subset relation: {existing_relation.attributes} in favor of {remaining_relation.attributes}"
                )
                to_remove.append(existing_relation)
            elif new_attrs.issubset(existing_attrs):
                print(
                    f"Skipping subset relation: {remaining_relation.attributes} since {existing_relation.attributes} already exists"
                )
                break
        else:
            for relation in to_remove:
                decomposed_relation_list.remove(relation)
            print(f"Adding new relation: {remaining_relation.attributes}")
            decomposed_relation_list.append(remaining_relation)

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
    anomalies = detect_3NF_anomalies(relation)
    if anomalies:
        list_of_3NF_relations = decompose_relation(relation, anomalies)
        for decomposed_relation in list_of_3NF_relations:
            decomposed_relation.print_relation()
        return list_of_3NF_relations
    else:
        relation.print_relation()
        return relations


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
