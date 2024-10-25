from classes import *
from helper_functions import *


def decompose_relation(relation, anomaly_list):
    # Initialize a list to hold decomposed Relation objects
    decomposed_relations = []
    count = 1
    remaining_attributes = relation.attributes[:]

    for anomaly in anomaly_list:
        # Initialize a new decomposed Relation object with a count-based name
        decomposed_relation = Relation(name=str(count), attributes=[])

        if "|" not in anomaly:
            # The anomaly isn't nested
            decomposed_relation.attributes.append(anomaly)
            remaining_attributes.remove(anomaly)
        else:
            # Process each character in the anomaly to construct attributes
            attribute_string = ""
            for character in anomaly:
                if character == "|":
                    decomposed_relation.attributes.append(attribute_string)
                    remaining_attributes.remove(attribute_string)
                    attribute_string = ""
                else:
                    # Build up the attribute string character by character
                    attribute_string += character

            # Append the final attribute_string to decomposed attributes (if any)
            if attribute_string:
                decomposed_relation.attributes.append(attribute_string)
                remaining_attributes.remove(attribute_string)

        # Append the parent relation's keys
        decomposed_relation.primary_key.extend(relation.primary_key)
        decomposed_relation.foreign_keys.extend([relation.primary_key])
        decomposed_relation.candidate_keys.extend(relation.candidate_keys)
        decomposed_relation.attributes.append(relation.primary_key)

        # Add the newly created decomposed relation to the list
        decomposed_relations.append(decomposed_relation)

        count += 1

        # Filter out any attributes already included in existing decomposed relations
        remaining_attributes = [
            attr
            for attr in remaining_attributes
            if all(attr not in relation.attributes for relation in decomposed_relations)
        ]

        # If there are truly remaining attributes, create an additional decomposed relation
        if remaining_attributes:
            remaining_relation = Relation(
                name=str(count), attributes=remaining_attributes
            )

            # Add the parent relation's primary key, foreign keys, candidate keys, and functional dependencies
            remaining_relation.primary_key.extend(relation.primary_key)
            remaining_relation.foreign_keys.extend(relation.foreign_keys)
            remaining_relation.candidate_keys.extend(relation.candidate_keys)
            remaining_relation.functional_dependencies.extend(
                relation.functional_dependencies
            )

            # Append the remaining relation to the decomposed relations list
            decomposed_relations.append(remaining_relation)

        # Return the list of decomposed Relation objects
        return decomposed_relations


def normalize_1NF(relation):
    anomalies = detect_1NF_anomalies(relation)  # Detect anomalies in 1NF
    if anomalies:
        # Decompose the relation based on anomalies and return a list of decomposed relations
        list_of_1NF_relations = decompose_relation(relation, anomalies)

        # Use each Relation object's print_relation method
        for decomposed_relation in list_of_1NF_relations:
            decomposed_relation.print_relation()
    else:
        # If no decomposition is needed, print the original relation
        relation.print_relation()


def normalize_2NF(relation):
    relations = normalize_1NF(relation)
    anomalies = detect_2NF_anomalies(relation)
    if anomalies:
        list_of_2NF_relations = decompose_relation(relation, [anomalies])
        print_relation(list_of_2NF_relations)
        return list_of_2NF_relations
    else:
        print_relation(relation)
        return relations


def normalize_3NF(relation):
    relations = normalize_2NF(relation)
    anomalies = detect_3NF_anomalies(relation)
    if anomalies:
        list_of_3NF_relations = decompose_relation(relation, [anomalies])
        print_relation(list_of_3NF_relations)
        return list_of_3NF_relations
    else:
        print_relation(relation)
        return relations


def normalize_BCNF(relation):
    relations = normalize_3NF(relation)
    anomalies = detect_BCNF_anomalies(relation)
    if anomalies:
        list_of_BCNF_relations = decompose_relation(relation, [anomalies])
        print_relation(list_of_BCNF_relations)
        return list_of_BCNF_relations
    else:
        print_relation(relation)
        return relations


def normalize_4NF(relation):
    relations = normalize_BCNF(relation)
    anomalies = detect_4NF_anomalies(relation)
    if anomalies:
        list_of_4NF_relations = decompose_relation(relation, [anomalies])
        print_relation(list_of_4NF_relations)
        return list_of_4NF_relations
    else:
        print_relation(relation)
        return relations


def normalize_5NF(relation):
    relations = normalize_4NF(relation)
    anomalies = detect_5NF_anomalies(relation)
    if anomalies:
        list_of_5NF_relations = decompose_relation(relation, [anomalies])
        print_relation(list_of_5NF_relations)
        return list_of_5NF_relations
    else:
        print_relation(relation)
        return relations


# --------------------------------- Anomaly Functions ---------------------------------
def detect_1NF_anomalies(relation):
    anomalies = []
    delimiter = "|"

    # Iterate over each attribute in the relation
    for attribute in relation.attributes:
        is_atomic = (
            input(f"Is the attribute '{attribute}' atomic? (yes/no): ").strip().lower()
        )

        # If the attribute is non-atomic, add it to the anomalies list
        if is_atomic == "no":
            anomalies.append(attribute)

    return anomalies


def detect_2NF_anomalies(relation):
    anomalies = []
    delimiter = "|"

    prime_key = relation.primary_key
    all_keys = prime_key[:]

    # Add candidate keys and foreign keys to the all_keys list
    for candidate_key in relation.candidate_keys:
        all_keys.extend(candidate_key)
    for foreign_key in relation.foreign_keys:
        all_keys.extend(foreign_key)

    # Non-keys are attributes that are not part of any key (primary, candidate, or foreign)
    non_keys = [attr for attr in relation.attributes if attr not in all_keys]

    # Check functional dependencies for 2NF anomalies (partial dependencies)
    for fd in relation.functional_dependencies:
        X = fd.get_x()  # Determinant (composite key or part of key)
        Y = fd.get_y()  # Dependent attributes

        # Check if X is part of the primary key but not the entire primary key
        if set(X).issubset(prime_key) and set(X) != set(prime_key):
            # Check if Y contains non-key attributes
            if set(Y).issubset(non_keys):
                # Join the composite key and dependent attributes using the delimiter
                composite_anomaly = delimiter.join(X + Y)
                anomalies.append(composite_anomaly)

    return anomalies
