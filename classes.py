class FunctionalDependency:
    def __init__(self, X, Y):
        self.X = X if isinstance(X, list) else [X]
        self.Y = Y if isinstance(Y, list) else [Y]

    def get_x(self):
        return self.X

    def get_y(self):
        return self.Y

    def __repr__(self):
        return f"{self.X} -> {self.Y}"


class Relation:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes
        self.primary_key = []
        self.foreign_keys = []
        self.candidate_keys = []
        self.functional_dependencies = []

    def add_primary_key(self, key):
        if isinstance(key, list):
            self.primary_key.extend(key)
        else:
            self.primary_key.append(key)

    def add_foreign_key(self, key):
        if isinstance(key, list):
            self.foreign_keys.append(key)
        else:
            self.foreign_keys.append([key])

    def add_candidate_key(self, key):
        if isinstance(key, list):
            self.candidate_keys.append(key)
        else:
            self.candidate_keys.append([key])

    def add_functional_dependency(self, X, Y):
        self.functional_dependencies.append(FunctionalDependency(X, Y))

    def __repr__(self):
        return (
            f"Relation(Name: {self.name}, Attributes: {self.attributes}, "
            f"Primary Key: {self.primary_key}, Foreign Keys: {self.foreign_keys}, "
            f"Candidate Keys: {self.candidate_keys}, Functional Dependencies: {self.functional_dependencies})"
        )
