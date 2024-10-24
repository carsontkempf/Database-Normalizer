from classes import *


# --------------------------------- Normalization Functions ---------------------------------
def add_relation(
    name, attributes, primary_key=None, candidate_keys=None, foreign_keys=None
):
    # Create the Relation object
    relation = Relation(name, attributes)

    # Add the primary key
    if primary_key:
        if isinstance(primary_key, list):
            relation.add_primary_key(primary_key)
        else:
            relation.add_primary_key([primary_key])

    # Add the candidate keys (if provided)
    if candidate_keys:
        for candidate_key in candidate_keys:
            if isinstance(candidate_key, list):
                relation.add_candidate_key(candidate_key)
            else:
                relation.add_candidate_key([candidate_key])

    # Add the foreign keys (if provided)
    if foreign_keys:
        for foreign_key in foreign_keys:
            if isinstance(foreign_key, list):
                relation.add_foreign_key(foreign_key)
            else:
                relation.add_foreign_key([foreign_key])

    return relation


def delete_attribute(relation, attribute_list):
    # Remove each attribute in attribute_list from the relation's attributes
    for attribute in attribute_list:
        if attribute in relation.attributes:
            relation.attributes.remove(attribute)


def detect_1NF_anomalies(relation):
    anomalies = []

    # Iterate over each attribute in the relation
    for attribute in relation.attributes:
        # Ask the user if the attribute is atomic
        is_atomic = (
            input(f"Is the attribute '{attribute}' atomic? (yes/no): ").strip().lower()
        )

        # If the attribute is non-atomic (user says 'no'), add it to the anomalies list
        if is_atomic == "no":
            anomalies.append(attribute)

    return anomalies


def decompose(relation, anomalies):
    list_of_1NF_relations = []  # This will store the new relations
    relation_counter = 1  # To name the new relations as R1, R2, ...

    # Iterate through each anomaly (or group of anomalies)
    for anomaly in anomalies:
        # Generate a new relation name (e.g., "R1", "R2", etc.)
        new_relation_name = f"R{relation_counter}"

        # New relation should have the anomaly attributes plus the parent's primary key
        new_relation_attributes = relation.primary_key + (
            anomaly if isinstance(anomaly, list) else [anomaly]
        )

        # Add the primary key (same as parent's) and foreign key (also same as parent's)
        new_relation = add_relation(
            name=new_relation_name,
            attributes=new_relation_attributes,
            primary_key=relation.primary_key,
            foreign_keys=[relation.primary_key],
        )

        # Add the new relation to the list
        list_of_1NF_relations.append(new_relation)

        # Delete the anomaly attributes from the parent relation
        delete_attribute(relation, anomaly if isinstance(anomaly, list) else [anomaly])

        # Increment the relation counter for the next new relation
        relation_counter += 1

    remaining_relation = add_relation(
        name=relation.name,
        attributes=relation.attributes,
        primary_key=relation.primary_key,
        foreign_keys=relation.foreign_keys,
    )

    # Add the remaining relation to the list
    list_of_1NF_relations.append(remaining_relation)

    return list_of_1NF_relations


# --------------------------------- User Input Functions ---------------------------------
def input_relation():
    # Get relation name from the user
    name = input("Enter the name of the relation: ").strip()

    # Get attributes from the user
    attributes = input("Enter attributes (comma-separated): ").split(",")
    attributes = [attr.strip() for attr in attributes]

    # Ask for the primary key or use a default if none is provided
    primary_key_input = input(
        "Enter primary key (comma-separated if composite), or press Enter for default: "
    ).strip()
    if not primary_key_input:
        # If no input, use a default primary key based on the relation name (e.g., 'relation_name_id')
        primary_key = [f"{name}_id"]
        print(f"Default primary key '{primary_key[0]}' will be used.")
        # Ensure that the primary key exists in attributes
        if primary_key[0] not in attributes:
            attributes.append(
                primary_key[0]
            )  # Add the default primary key to attributes if missing
    else:
        primary_key = [key.strip() for key in primary_key_input.split(",")]

    # Ensure primary key is part of the relation attributes
    if not set(primary_key).issubset(attributes):
        raise ValueError("Primary key must be a subset of the relation's attributes.")

    # Ask for candidate keys (optional)
    candidate_keys_input = input(
        "Enter candidate key(s) (comma-separated for each key, semicolon-separated for multiple keys): "
    ).strip()
    candidate_keys = None
    if candidate_keys_input:
        candidate_keys = [
            key.strip().split(",") for key in candidate_keys_input.split(";")
        ]

    # Ask for foreign keys (optional)
    foreign_keys_input = input(
        "Enter foreign key(s) (comma-separated for each key, semicolon-separated for multiple keys): "
    ).strip()
    foreign_keys = None
    if foreign_keys_input:
        foreign_keys = [key.strip().split(",") for key in foreign_keys_input.split(";")]

    # Use the add_relation function to create the Relation object
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

        # Ask if the user wants to add another data tuple
        more_input = (
            input("Do you want to add another data tuple? (yes/no): ").strip().lower()
        )
        if more_input == "no":
            break


# --------------------------------- Print Functions ---------------------------------


def print_relation(relations):
    for index, relation in enumerate(relations, start=1):
        print(f"\nRelation {index}: {relation.name}")
        print(f"Attributes: {', '.join(relation.attributes)}")
        print(f"Primary Key: {', '.join(relation.primary_key)}")

        if relation.candidate_keys:
            print("Candidate Keys:")
            for candidate_key in relation.candidate_keys:
                print(f"  - {', '.join(candidate_key)}")
        else:
            print("Candidate Keys: None")

        if relation.foreign_keys:
            print("Foreign Keys:")
            for foreign_key in relation.foreign_keys:
                print(f"  - {', '.join(foreign_key)}")
        else:
            print("Foreign Keys: None")

        if relation.functional_dependencies:
            print("Functional Dependencies:")
            for fd in relation.functional_dependencies:
                print(f"  - {fd}")
        else:
            print("Functional Dependencies: None")


def print_message(message):
    print("\n" + "-" * 50)
    print(message)
    print("-" * 50 + "\n")


def print_functional_dependency(relation):
    print("Functional Dependencies:")
    for fd in relation.functional_dependencies:
        print(f"{fd}")
