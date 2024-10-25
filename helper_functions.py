from classes import *


# --------------------------------- Class Functions ---------------------------------
def add_relation(
    name, attributes, primary_key=None, candidate_keys=None, foreign_keys=None
):
    relation = Relation(name, attributes)

    if primary_key:
        if isinstance(primary_key, list):
            relation.add_primary_key(primary_key)
        else:
            relation.add_primary_key([primary_key])

    if candidate_keys:
        for candidate_key in candidate_keys:
            if isinstance(candidate_key, list):
                relation.add_candidate_key(candidate_key)
            else:
                relation.add_candidate_key([candidate_key])

    if foreign_keys:
        for foreign_key in foreign_keys:
            if isinstance(foreign_key, list):
                relation.add_foreign_key(foreign_key)
            else:
                relation.add_foreign_key([foreign_key])

    return relation


def delete_relation(relation_name, relations_list):
    return [relation for relation in relations_list if relation.name != relation_name]


def delete_attribute(relation, attribute_list):
    for attribute in attribute_list:
        if attribute in relation.attributes:
            relation.attributes.remove(attribute)


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


def decompose_relation(relation, anomalies):
    list_of_relations = []
    relation_counter = 1
    delimiter = "|"  # Predefined delimiter for composite anomalies

    # Make a copy of all attributes, excluding the primary key
    all_attributes = [
        attr for attr in relation.attributes if attr not in relation.primary_key
    ]

    # Process each anomaly in the list
    for anomaly in anomalies:
        new_relation_attributes = []

        # If the anomaly is composite (contains the delimiter), split it into multiple attributes
        if delimiter in anomaly:
            composite_attributes = anomaly.split(delimiter)
            for composite_attr in composite_attributes:
                if composite_attr in all_attributes:
                    new_relation_attributes.append(composite_attr)
                    all_attributes.remove(composite_attr)
        else:
            # Single attribute case
            if anomaly in all_attributes:
                new_relation_attributes.append(anomaly)
                all_attributes.remove(anomaly)

        # Always include the primary key in the new relation, but do not treat it as a separate attribute
        if new_relation_attributes:
            new_relation_attributes += relation.primary_key

            # Create the new relation for this anomaly or composite anomaly
            new_relation = add_relation(
                name=f"R{relation_counter}",
                attributes=new_relation_attributes,
                primary_key=relation.primary_key,
                foreign_keys=relation.foreign_keys,
            )

            # Append new relation to the list
            list_of_relations.append(new_relation)
            relation_counter += 1

    # Create a final relation for all the remaining atomic attributes
    if all_attributes:
        remaining_relation_attributes = all_attributes + relation.primary_key
        remaining_relation = add_relation(
            name=f"R{relation_counter}",
            attributes=remaining_relation_attributes,
            primary_key=relation.primary_key,
            foreign_keys=relation.foreign_keys,
        )
        list_of_relations.append(remaining_relation)

    return list_of_relations


# --------------------------------- User Input Functions ---------------------------------
def input_relation():
    name = input("Enter the name of the relation: ").strip()
    attributes = input("Enter attributes (comma-separated): ").split(",")
    attributes = [attr.strip() for attr in attributes]

    primary_key_input = input(
        "Enter primary key (comma-separated if composite), or press Enter for default: "
    ).strip()
    if not primary_key_input:
        primary_key = [f"{name}_id"]
        print(f"Default primary key '{primary_key[0]}' will be used.")
        if primary_key[0] not in attributes:
            attributes.append(primary_key[0])
    else:
        primary_key = [key.strip() for key in primary_key_input.split(",")]

    if not set(primary_key).issubset(attributes):
        raise ValueError("Primary key must be a subset of the relation's attributes.")

    candidate_keys_input = input(
        "Enter candidate key(s) (comma-separated for each key, semicolon-separated for multiple keys): "
    ).strip()
    candidate_keys = None
    if candidate_keys_input:
        candidate_keys = [
            key.strip().split(",") for key in candidate_keys_input.split(";")
        ]

    foreign_keys_input = input(
        "Enter foreign key(s) (comma-separated for each key, semicolon-separated for multiple keys): "
    ).strip()
    foreign_keys = None
    if foreign_keys_input:
        foreign_keys = [key.strip().split(",") for key in foreign_keys_input.split(";")]

    relation_object = add_relation(
        name=name,
        attributes=attributes,
        primary_key=primary_key,
        candidate_keys=candidate_keys,
        foreign_keys=foreign_keys,
    )

    return relation_object


def add_functional_dependency(relation):
    X = input("Enter the determinant attributes (X) (comma-separated): ").split(",")
    Y = input("Enter the dependent attributes (Y) (comma-separated): ").split(",")
    relation.add_functional_dependency([x.strip() for x in X], [y.strip() for y in Y])


def add_data(relation):
    while True:
        data = input(
            f"Enter tuple values (comma-separated for {relation.attributes}): "
        ).split(",")
        relation.add_tuple([value.strip() for value in data])

        more_input = (
            input("Do you want to add another data tuple? (yes/no): ").strip().lower()
        )
        if more_input == "no":
            break


# --------------------------------- Print Functions ---------------------------------
def print_relation(relation):
    if isinstance(relation, list):
        for index, rel in enumerate(relation, start=1):
            print(f"\nRelation {index}: {rel.name}")
            print(f"Attributes: {', '.join(map(str, rel.attributes))}")
            print(f"Primary Key: {', '.join(map(str, rel.primary_key))}")

            if rel.candidate_keys:
                print("Candidate Keys:")
                for candidate_key in rel.candidate_keys:
                    print(f"  - {', '.join(map(str, candidate_key))}")
            else:
                print("Candidate Keys: None")

            if rel.foreign_keys:
                print("Foreign Keys:")
                for foreign_key in rel.foreign_keys:
                    print(f"  - {', '.join(map(str, foreign_key))}")
            else:
                print("Foreign Keys: None")

            if rel.functional_dependencies:
                print("Functional Dependencies:")
                for fd in rel.functional_dependencies:
                    print(f"  - {fd}")
            else:
                print("Functional Dependencies: None")
    else:
        print(f"\nRelation: {relation.name}")
        print(f"Attributes: {', '.join(map(str, relation.attributes))}")
        print(f"Primary Key: {', '.join(map(str, relation.primary_key))}")

        if relation.candidate_keys:
            print("Candidate Keys:")
            for candidate_key in relation.candidate_keys:
                print(f"  - {', '.join(map(str, candidate_key))}")
        else:
            print("Candidate Keys: None")

        if relation.foreign_keys:
            print("Foreign Keys:")
            for foreign_key in relation.foreign_keys:
                print(f"  - {', '.join(map(str, foreign_key))}")
        else:
            print("Foreign Keys: None")

        if relation.functional_dependencies:
            print("Functional Dependencies:")
            for fd in relation.functional_dependencies:
                print(f"  - {fd}")
        else:
            print("Functional Dependencies: None")
