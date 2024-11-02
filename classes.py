# Class representing a Functional Dependency (FD) in a relation
class FunctionalDependency:
    def __init__(self, X, Y):
        # Initialize FD with left-hand side (X) and right-hand side (Y)
        # Ensures both X and Y are lists, even if given as single values
        self.X = X if isinstance(X, list) else [X]
        self.Y = Y if isinstance(Y, list) else [Y]

    def adjust_to_primary_key(self, primary_key):
        # Adjusts FD's left-hand side (X) to match the primary key format
        primary_key_tuple = tuple(tuple(pk) for pk in primary_key)
        self.X = [list(pk) for pk in primary_key_tuple]

    def get_x(self):
        # Returns the left-hand side (X) of the FD
        return self.X

    def get_y(self):
        # Returns the right-hand side (Y) of the FD
        return self.Y

    def __repr__(self):
        # Provides a string representation of the FD in "X -> Y" format
        return f"{self.X} -> {self.Y}"


# Class representing a Relation with attributes and constraints
class Relation:
    def __init__(self, name, attributes):
        # Initializes the relation with a name and a list of attributes
        self.name = name
        self.attributes = attributes
        self.primary_key = []  # Stores the primary key
        self.foreign_keys = []  # Stores foreign keys
        self.candidate_keys = []  # Stores candidate keys
        self.functional_dependencies = []  # Stores functional dependencies (FDs)
        self.data = []  # Stores data tuples for the relation

    def add_primary_key(self, key):
        # Adds a primary key or appends to it if it’s a composite key
        if isinstance(key, list):
            self.primary_key.extend(key)
        else:
            self.primary_key.append(key)

    def add_candidate_key(self, candidate_key):
        # Adds a candidate key to the relation; supports single or composite keys
        if isinstance(candidate_key, list):
            self.candidate_keys.append(candidate_key)
        else:
            self.candidate_keys.append([candidate_key])

    def add_foreign_key(self, foreign_key):
        # Adds a foreign key to the relation; supports single or composite keys
        if isinstance(foreign_key, list):
            self.foreign_keys.append(foreign_key)
        else:
            self.foreign_keys.append([foreign_key])

    def add_attribute(self, attribute):
        # Adds a new attribute to the relation if it does not already exist
        if attribute not in self.attributes:
            self.attributes.append(attribute)

    def add_functional_dependency(self, X, Y):
        # Adds a functional dependency if all attributes in X and Y exist in relation's attributes
        all_attributes = [
            attr
            for sublist in (X, Y)
            for attr in (sublist if isinstance(sublist, list) else [sublist])
        ]
        if all(attr in self.attributes for attr in all_attributes):
            self.functional_dependencies.append(FunctionalDependency(X, Y))
        else:
            # Tracks any missing attributes in case some attributes do not exist in the relation
            missing_attrs = [
                attr for attr in all_attributes if attr not in self.attributes
            ]

    def add_tuple(self, data_instance):
        # Adds a tuple of data to the relation, ensuring it matches the relation's attributes
        if len(data_instance) != len(self.attributes):
            raise ValueError(
                f"Expected {len(self.attributes)} attributes, got {len(data_instance)}."
            )
        self.data.append(data_instance)

    def print_relation(self):
        # Prints the details of the relation, including its attributes, keys, and FDs
        print(f"\nRelation: {self.name}")
        print(f"Attributes: {', '.join(map(str, self.attributes))}")
        print(f"Primary Key: {', '.join(map(str, self.primary_key))}")

        if self.candidate_keys:
            print("Candidate Keys:")
            for candidate_key in self.candidate_keys:
                print(f"  - {', '.join(map(str, candidate_key))}")
        else:
            print("Candidate Keys: None")

        if self.foreign_keys:
            print("Foreign Keys:")
            for foreign_key in self.foreign_keys:
                print(f"  - {', '.join(map(str, foreign_key))}")
        else:
            print("Foreign Keys: None")

        if self.functional_dependencies:
            print("Functional Dependencies:")
            for fd in self.functional_dependencies:
                print(f"  - {fd}")
        else:
            print("Functional Dependencies: None")

    def __repr__(self):
        # Returns a string representation of the relation with its main properties
        return (
            f"Relation(Name: {self.name}, Attributes: {self.attributes}, "
            f"Primary Key: {self.primary_key}, Foreign Keys: {self.foreign_keys}, "
            f"Candidate Keys: {self.candidate_keys}, Functional Dependencies: {self.functional_dependencies})"
        )
