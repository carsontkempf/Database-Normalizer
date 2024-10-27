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
def decompose_relation(parent_relation, anomaly_list):
    # If no anomalies, return the parent relation as a single-item list
    if not anomaly_list:
        return [parent_relation]

    decomposed_relation_list = []
    count = 1
    all_parent_attributes = parent_relation.attributes[:]

    print("\nStarting decomposition for anomalies...\n")

    for anomaly in anomaly_list:
        decomposed_relation = Relation(name=str(count), attributes=[])
        if anomaly in all_parent_attributes:
            all_parent_attributes.remove(anomaly)

        # If the anomaly isn't nested
        if "|" in anomaly:
            anomaly_attributes = anomaly.split("|")
            for attr in anomaly_attributes:
                if attr in all_parent_attributes:
                    all_parent_attributes.remove(attr)
        else:
            remove_part, *nested_attributes = anomaly.split("|")
            for nested_attr in nested_attributes:
                decomposed_relation.attributes.append(nested_attr)

        # Ensure the parent relation's primary keys are included in the decomposed relation
        for pk in parent_relation.primary_key:
            if pk not in decomposed_relation.attributes:
                decomposed_relation.attributes.append(pk)

        # Append the parent relation's keys to the decomposed relation
        decomposed_relation.primary_key.extend(parent_relation.primary_key)
        decomposed_relation.foreign_keys.extend(parent_relation.foreign_keys)
        decomposed_relation.add_foreign_key(parent_relation.primary_key)
        decomposed_relation.candidate_keys.extend(parent_relation.candidate_keys)
        decomposed_relation.functional_dependencies.extend(
            parent_relation.functional_dependencies
        )

        new_attrs = set(decomposed_relation.attributes)
        to_remove = []

        # Check for duplicates and subsets in the current relation list
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

    # If there are remaining attributes, create an additional decomposed relation
    if all_parent_attributes:
        remaining_relation = Relation(name=str(count), attributes=all_parent_attributes)
        remaining_relation.primary_key.extend(parent_relation.primary_key)
        remaining_relation.foreign_keys.extend(parent_relation.foreign_keys)
        remaining_relation.add_foreign_key(parent_relation.primary_key)
        remaining_relation.candidate_keys.extend(parent_relation.candidate_keys)
        remaining_relation.functional_dependencies.extend(
            parent_relation.functional_dependencies
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

    # Return decomposed relations list
    return decomposed_relation_list


def normalize_1NF(relation):
    print_normalization_stage("1NF Normalization")
    anomalies = detect_1NF_anomalies(relation)  # Detect anomalies in 1NF

    if anomalies:
        # Decompose the relation based on anomalies and return a list of decomposed relations
        list_of_1NF_relations = decompose_relation(relation, anomalies)
        for decomposed_relation in list_of_1NF_relations:
            decomposed_relation.print_relation()
        return list_of_1NF_relations
    else:
        # If no decomposition is needed, print the original relation and return it as a list
        relation.print_relation()
        return [relation]  # Return as list for consistency


def normalize_2NF(relation):
    print_normalization_stage("2NF Normalization")
    list_of_1NF_relations = normalize_1NF(relation)  # Ensures we get a list back
    final_2NF_relations = []

    for rel in list_of_1NF_relations:
        anomalies = detect_2NF_anomalies(rel)
        if anomalies:
            # Decompose each relation based on its anomalies for partial dependencies
            list_of_2NF_relations = decompose_relation(rel, anomalies)
            for decomposed_relation in list_of_2NF_relations:
                decomposed_relation.print_relation()
            final_2NF_relations.extend(list_of_2NF_relations)
        else:
            # If no decomposition needed, add the original relation to 2NF relations
            rel.print_relation()
            final_2NF_relations.append(rel)

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
def detect_1NF_anomalies(relation):
    anomalies = []

    # Iterate over each attribute in the relation
    for attribute in relation.attributes:
        is_atomic = (
            input(f"Is the attribute '{attribute}' atomic? (yes/no): ").strip().lower()
        )

        # If the attribute is non-atomic, add it to the anomalies list
        if is_atomic == "no":
            anomalies.append(attribute)

    return anomalies


# Adjust detect_2NF_anomalies to catch partial dependencies specifically
def detect_2NF_anomalies(relation):
    anomalies = []
    delimiter = "|"

    prime_key = relation.primary_key
    all_keys = prime_key[:]

    for candidate_key in relation.candidate_keys:
        all_keys.extend(candidate_key)
    for foreign_key in relation.foreign_keys:
        all_keys.extend(foreign_key)

    non_keys = [attr for attr in relation.attributes if attr not in all_keys]

    for fd in relation.functional_dependencies:
        X = fd.get_x()
        Y = fd.get_y()

        if set(X).issubset(set(all_keys)) and set(X) != set(prime_key):
            non_key_Y = [y for y in Y if y in non_keys]
            if non_key_Y:
                composite_anomaly = delimiter.join(non_key_Y)
                anomalies.append(composite_anomaly)

    return anomalies
