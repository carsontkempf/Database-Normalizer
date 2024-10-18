# How to add a relation
relation = Relation("Students", ["student_id", "name", "address", "course_id", "phone"])

# How to add keys to a relation
relation.add_primary_key(["student_id", "course_id"])
relation.add_foreign_key("course_id")
relation.add_candidate_key(["student_id", "phone"])

# How to add functional dependencies
relation.add_functional_dependency(["student_id"], ["name", "address"])
relation.add_functional_dependency("course_id", "phone")

# get functional dependencies
for fd in relation.functional_dependencies:
    print(f"Functional Dependency: {fd}")
    print(f"X: {fd.X}, Y: {fd.Y}")

# Output the relation details
print(relation)