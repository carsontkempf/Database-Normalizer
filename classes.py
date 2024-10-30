class FunctionalDependency:
    # Initializes a functional dependency with determinant (X) and dependent (Y) attributes
    def __init__(self, X, Y):
        self.X = X if isinstance(X, list) else [X]
        self.Y = Y if isinstance(Y, list) else [Y]

    # Adjusts the determinant to align with the primary key structure
    def adjust_to_primary_key(self, primary_key):
        primary_key_tuple = tuple(tuple(pk) for pk in primary_key)
        self.X = [list(pk) for pk in primary_key_tuple]

    # Returns the determinant attributes of the functional dependency
    def get_x(self):
        return self.X

    # Returns the dependent attributes of the functional dependency
    def get_y(self):
        return self.Y

    # Provides a string representation of the functional dependency
    def __repr__(self):
        return f"{self.X} -> {self.Y}"


class Relation:
    # Initializes a relation with name, attributes, and other structural properties
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes
        self.primary_key = []
        self.foreign_keys = []
        self.candidate_keys = []
        self.functional_dependencies = []
        self.data = []

    # Adds a primary key to the relation; supports composite keys
    def add_primary_key(self, key):
        if isinstance(key, list):
            self.primary_key.append(key)
        else:
            self.primary_key.append([key])

    # Adds a candidate key to the relation; supports composite candidate keys
    def add_candidate_key(self, candidate_key):
        if isinstance(candidate_key, list):
            self.candidate_keys.append(candidate_key)
        else:
            self.candidate_keys.append([candidate_key])

    # Adds a foreign key to the relation; supports composite foreign keys
    def add_foreign_key(self, foreign_key):
        if isinstance(foreign_key, list):
            self.foreign_keys.append(foreign_key)
        else:
            self.foreign_keys.append([foreign_key])

    # Adds an attribute to the relation if it does not already exist
    def add_attribute(self, attribute):
        if attribute not in self.attributes:
            self.attributes.append(attribute)

    # Adds a functional dependency to the relation if all attributes in X and Y are present
    def add_functional_dependency(self, X, Y):
        all_attributes = [
            attr
            for sublist in (X, Y)
            for attr in (sublist if isinstance(sublist, list) else [sublist])
        ]

        # Check if all attributes in X and Y are in the relation's attributes
        if all(attr in self.attributes for attr in all_attributes):
            self.functional_dependencies.append(FunctionalDependency(X, Y))
        else:
            missing_attrs = [
                attr for attr in all_attributes if attr not in self.attributes
            ]

    # Adds a data tuple to the relation; raises an error if attribute count mismatches
    def add_tuple(self, data_instance):
        if len(data_instance) != len(self.attributes):
            raise ValueError(
                f"Expected {len(self.attributes)} attributes, got {len(data_instance)}."
            )
        self.data.append(data_instance)

    # Prints details of the relation, including keys and functional dependencies
    def print_relation(self):
        print(f"\nRelation: {self.name}")
        print(f"Attributes: {', '.join(map(str, self.attributes))}")
        primary_key_display = ", ".join(f"({', '.join(pk)})" for pk in self.primary_key)
        print(f"Primary Key: {primary_key_display}")

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

    # Provides a string representation of the relation, including all structural elements
    def __repr__(self):
        return (
            f"Relation(Name: {self.name}, Attributes: {self.attributes}, "
            f"Primary Key: {self.primary_key}, Foreign Keys: {self.foreign_keys}, "
            f"Candidate Keys: {self.candidate_keys}, Functional Dependencies: {self.functional_dependencies})"
        )
