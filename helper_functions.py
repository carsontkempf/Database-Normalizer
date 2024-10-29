from classes import *
from normalize_functions import *


# --------------------------------- Class Functions ---------------------------------


def add_candidate_keys(relation, candidate_keys):
    if candidate_keys:
        for candidate_key in candidate_keys:
            relation.add_candidate_key(candidate_key)


def add_foreign_keys(relation, foreign_keys):
    if foreign_keys:
        for foreign_key in foreign_keys:
            relation.add_foreign_key(foreign_key)


def create_relation(name, attributes):
    return Relation(name, attributes)


def build_relation(
    name, attributes, primary_key=None, candidate_keys=None, foreign_keys=None
):
    """Build a complete relation by initializing and adding keys."""
    # Create a new Relation object
    relation = Relation(name, attributes)

    # Add the primary key using the Relation instance method
    if primary_key:
        relation.add_primary_key(primary_key)

    # Add candidate keys
    if candidate_keys:
        for candidate_key in candidate_keys:
            relation.add_candidate_key(candidate_key)

    # Add foreign keys
    if foreign_keys:
        for foreign_key in foreign_keys:
            relation.add_foreign_key(foreign_key)

    return relation


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

    return build_relation(
        name=name,
        attributes=attributes,
        primary_key=primary_key,
        candidate_keys=candidate_keys,
        foreign_keys=foreign_keys,
    )


def input_functional_dependency(relation):
    X = input("Enter the determinant attributes (X) (comma-separated): ").split(",")
    Y = input("Enter the dependent attributes (Y) (comma-separated): ").split(",")
    relation.add_functional_dependency([x.strip() for x in X], [y.strip() for y in Y])


def input_data(relation):
    # Always enter the first tuple
    data = input(
        f"Enter tuple values (comma-separated for {relation.attributes}): "
    ).split(",")
    data_dict = dict(zip(relation.attributes, [value.strip() for value in data]))
    relation.add_tuple(data_dict)

    # Now ask if the user wants to add more tuples
    while True:
        more_input = (
            input("Do you want to add another data tuple? (yes/no): ").strip().lower()
        )
        if more_input == "no":
            break

        # Prompt for the next tuple if 'yes'
        data = input(
            f"Enter tuple values (comma-separated for {relation.attributes}): "
        ).split(",")
        data_dict = dict(zip(relation.attributes, [value.strip() for value in data]))
        relation.add_tuple(data_dict)


# --------------------------------- Print Functions ---------------------------------


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(f"Starting {stage_name}")
    print_divider()
