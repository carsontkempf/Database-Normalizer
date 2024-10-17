class FunctionalDependency:
    def __init__(self, X, Y):
        # X and Y are either single attributes or a combination of attributes (represented as lists)
        self.X = X if isinstance(X, list) else [X]  # Ensure X is a list of attributes
        self.Y = Y if isinstance(Y, list) else [Y]  # Ensure Y is a list of attributes

    def __repr__(self):
        return f"FunctionalDependency({self.X} -> {self.Y})"

    class Relation:
        def __init__(self, name, attributes):
            self.name = name  # Name of the relation
            self.attributes = attributes  # List of attributes (strings)
            self.primary_key = []  # Composite primary key (list of attributes)
            self.foreign_keys = []  # List of foreign keys (can be composite)
            self.candidate_keys = []  # List of candidate keys (can be composite)
            self.functional_dependencies = []  # List of functional dependencies

        def add_primary_key(self, key):
            if isinstance(key, list):
                self.primary_key.extend(key)  # Adding composite key
            else:
                self.primary_key.append(key)

        def add_foreign_key(self, key):
            if isinstance(key, list):
                self.foreign_keys.append(key)  # Adding composite foreign key
            else:
                self.foreign_keys.append([key])

        def add_candidate_key(self, key):
            if isinstance(key, list):
                self.candidate_keys.append(key)  # Adding composite candidate key
            else:
                self.candidate_keys.append([key])

        def add_functional_dependency(self, X, Y):
            self.functional_dependencies.append(FunctionalDependency(X, Y))

        def __repr__(self):
            return (f"Relation(Name: {self.name}, Attributes: {self.attributes}, "
                    f"Primary Key: {self.primary_key}, Foreign Keys: {self.foreign_keys}, "
                    f"Candidate Keys: {self.candidate_keys}, Functional Dependencies: {self.functional_dependencies})")

        # Create a relation with attributes
        relation = Relation("Students", ["student_id", "name", "address", "course_id", "phone"])

        # Define keys
        relation.add_primary_key(["student_id", "course_id"])  # Composite primary key
        relation.add_foreign_key("course_id")
        relation.add_candidate_key(["student_id", "phone"])  # Composite candidate key

        # Add functional dependencies
        relation.add_functional_dependency(["student_id"], ["name", "address"])
        relation.add_functional_dependency("course_id", "phone")

        # Output the relation details
        print(relation)