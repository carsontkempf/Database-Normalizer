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
    attributes = [
        attr.strip() for attr in attributes if attr.strip()
    ]  # Ignore empty attributes

    primary_key_input = input(
        "Enter primary key(s) (comma-separated for each key, semicolon-separated for multiple keys), or press Enter for default: "
    ).strip()
    if not primary_key_input:
        primary_key = [[f"{name}_id"]]  # Ensures primary key format as list of lists
        if (
            primary_key[0][0] not in attributes
        ):  # Ensure default primary key is added to attributes
            attributes.append(primary_key[0][0])
        print(f"Default primary key '{primary_key[0][0]}' will be used.")
    else:
        primary_key = [
            key_group.strip().split(",")
            for key_group in primary_key_input.split(";")
            if key_group.strip()
        ] or None  # Set to None if no valid input is given

    candidate_keys_input = input(
        "Enter candidate key(s) (comma-separated for each key, semicolon-separated for multiple keys): "
    ).strip()
    candidate_keys = (
        [
            key.strip().split(",")
            for key in candidate_keys_input.split(";")
            if key.strip()
        ]
        if candidate_keys_input
        else None
    )  # Set to None if input is empty

    foreign_keys_input = input(
        "Enter foreign key(s) (comma-separated for each key, semicolon-separated for multiple keys): "
    ).strip()
    foreign_keys = (
        [key.strip().split(",") for key in foreign_keys_input.split(";") if key.strip()]
        if foreign_keys_input
        else None
    )  # Set to None if input is empty

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

    # Strip whitespace and filter out empty strings in X and Y
    X = [x.strip() for x in X if x.strip()]
    Y = [y.strip() for y in Y if y.strip()]

    # Only add the functional dependency if both X and Y are non-empty
    if X and Y:
        relation.add_functional_dependency(X, Y)
    else:
        print("Empty functional dependency not added.")


def input_data(relation):
    # Prompt for tuple values
    data = (
        input(f"Enter tuple values (comma-separated for {relation.attributes}): ")
        .strip()
        .split(",")
    )

    # Map input to relation attributes and clean whitespace
    data_dict = dict(zip(relation.attributes, [value.strip() for value in data]))

    # Add the tuple to the relation
    relation.add_tuple(data_dict)


# --------------------------------- Print Functions ---------------------------------


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(f"Starting {stage_name}")
    print_divider()
