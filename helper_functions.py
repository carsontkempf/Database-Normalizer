from classes import *
from normalize_functions import *

# --------------------------------- Class Functions ---------------------------------


# Adds candidate keys to a relation if provided
def add_candidate_keys(relation, candidate_keys):
    if candidate_keys:
        for candidate_key in candidate_keys:
            relation.add_candidate_key(candidate_key)


# Adds foreign keys to a relation if provided
def add_foreign_keys(relation, foreign_keys):
    if foreign_keys:
        for foreign_key in foreign_keys:
            relation.add_foreign_key(foreign_key)


# Creates a relation instance with specified attributes, primary key, candidate keys, and foreign keys
def create_relation(
    name, attributes, primary_key=None, candidate_keys=None, foreign_keys=None
):
    relation = Relation(name, attributes)

    # Add the primary key using the Relation instance method
    if primary_key:
        relation.add_primary_key(primary_key)

    # Add candidate keys to the relation
    if candidate_keys:
        for candidate_key in candidate_keys:
            relation.add_candidate_key(candidate_key)

    # Add foreign keys to the relation
    if foreign_keys:
        for foreign_key in foreign_keys:
            relation.add_foreign_key(foreign_key)

    return relation


# --------------------------------- User Input Functions ---------------------------------


# Captures and creates a relation from user input, including attributes and keys
def input_relation():
    name = input("Enter the name of the relation: ").strip()
    attributes = input("Enter attributes (comma-separated): ").split(",")
    attributes = [attr.strip() for attr in attributes if attr.strip()]

    primary_key_input = input(
        "Enter primary keys (keys separated by comma, attributes separated by semicolon): "
    )

    # If no primary key input is provided, create a default primary key based on relation name
    if not primary_key_input:
        primary_key = [[f"{name}_id"]]
        attributes.append(f"{name}_id")

    else:
        # Parse input for primary keys, splitting by commas and semicolons to allow composite keys
        primary_key = [key.strip().split(",") for key in primary_key_input.split(";")]

    candidate_keys_input = input(
        "Enter candidate keys (keys separated by comma, attributes separated by semicolon): "
    ).strip()
    candidate_keys = [key.split(",") for key in candidate_keys_input.split(";")]

    foreign_keys_input = input(
        "Enter foreign keys (keys separated by comma, attributes separated by semicolon): "
    ).strip()
    foreign_keys = [key.split(",") for key in foreign_keys_input.split(";")]

    return create_relation(
        name=name,
        attributes=attributes,
        primary_key=primary_key,
        candidate_keys=candidate_keys,
        foreign_keys=foreign_keys,
    )


# Captures and adds a functional dependency to the relation based on user input
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


# Captures a data tuple from user input and adds it to the relation
def input_data(relation):
    data = (
        input(f"Enter tuple values (comma-separated for {relation.attributes}): ")
        .strip()
        .split(",")
    )

    # Map input values to relation attributes and clean whitespace
    data_dict = dict(zip(relation.attributes, [value.strip() for value in data]))

    # Add the tuple to the relation
    relation.add_tuple(data_dict)
