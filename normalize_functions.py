from classes import *
from helper_functions import *

# --------------------------------- Print Functions ---------------------------------


# Prints a divider line for visual clarity in console output
def print_divider():
    print("\n-------------------------\n")


# Prints the name of the current normalization stage with dividers
def print_normalization_stage(stage_name):
    print_divider()
    print(stage_name)
    print_divider()


# Prints the data of a relation in a table format, with attribute names as headers
def print_data(relation):
    if not relation.data:
        print("No data available in relation.")
        return

    # Print attribute names as headers
    print("\nData:")
    print(" | ".join(relation.attributes))
    print("-" * (len(relation.attributes) * 15))

    # Print each row by accessing data as dictionaries
    for data_dict in relation.data:
        print(
            " | ".join(str(data_dict[attr]).ljust(15) for attr in relation.attributes)
        )
    print()


# --------------------------------- Fix relations if they have anomalies ---------------------------------


# Removes duplicate attributes from a list of attributes, ensuring unique entries
def remove_duplicate_attributes(attributes):
    seen = set()
    cleaned_attributes = []

    for attr in attributes:
        if isinstance(attr, list):
            for sub_attr in attr:
                sub_attr_str = str(sub_attr)
                if sub_attr_str not in seen:
                    cleaned_attributes.append(sub_attr_str)
                    seen.add(sub_attr_str)
        else:
            attr_str = str(attr)
            if attr_str not in seen:
                cleaned_attributes.append(attr_str)
                seen.add(attr_str)

    return cleaned_attributes


# Fixes non-atomic attributes in a parent relation by creating new relations in 1NF
def fix_non_atomic_attributes(parent_relation, anomalies):
    relations_in_1NF = []

    all_parent_attributes = [str(attr) for attr in parent_relation.attributes]

    for anomaly in anomalies:
        new_relation = Relation(
            name=f"{parent_relation.name}_{anomaly}",
            attributes=parent_relation.primary_key[:],
        )

        new_relation.attributes.append(anomaly)

        relations_in_1NF.append(new_relation)

        if anomaly in all_parent_attributes:
            all_parent_attributes.remove(anomaly)

    if all_parent_attributes:
        new_relation = Relation(
            name=f"{parent_relation.name}_remaining",
            attributes=all_parent_attributes,
        )

        relations_in_1NF.append(new_relation)

    return relations_in_1NF


# Fixes partial functional dependencies by creating relations in 2NF from a parent relation
def fix_partial_functional_dependencies(parent_relation, anomalies):
    relations_in_2NF = []
    all_parent_attributes = [str(attr).strip() for attr in parent_relation.attributes]

    for anomaly in anomalies:
        new_relation = Relation(
            name=f"{parent_relation.name}_{anomaly}",
            attributes=parent_relation.primary_key[:],
        )

        new_relation.attributes.append(anomaly)
        new_relation.add_primary_key(parent_relation.primary_key)
        new_relation.add_functional_dependency(parent_relation.primary_key, anomaly)

        relations_in_2NF.append(new_relation)

        if anomaly in all_parent_attributes:
            all_parent_attributes.remove(anomaly)

    if all_parent_attributes:
        new_relation = Relation(
            name=f"{parent_relation.name}_remaining",
            attributes=all_parent_attributes,
        )
        new_relation.add_primary_key(parent_relation.primary_key)
        relations_in_2NF.append(new_relation)

    return relations_in_2NF


# Fixes transitive functional dependencies, producing relations in 3NF
def fix_transitive_functional_dependencies(parent_relation, transitive_dependencies):
    if len(parent_relation.functional_dependencies) < 2:
        return [parent_relation]

    relations_in_3NF = []
    all_parent_attributes = []
    for attr in parent_relation.attributes:
        if isinstance(attr, list):
            all_parent_attributes.extend(str(sub_attr).strip() for sub_attr in attr)
        else:
            all_parent_attributes.append(str(attr).strip())

    combined_dependencies = set()
    for dependency in transitive_dependencies:
        for attr in dependency.replace("|", ",").split(","):
            cleaned_attr = attr.strip()
            if cleaned_attr:
                combined_dependencies.add(cleaned_attr)

    combined_dependencies = [
        attr
        for attr in combined_dependencies
        if attr not in parent_relation.primary_key
    ]

    if combined_dependencies:
        print_normalization_stage(
            f"Detected transitive functional dependency attributes: {combined_dependencies}"
        )
    else:
        print_normalization_stage("No transitive functional dependencies found.")

    new_relation = Relation(
        name=f"{parent_relation.name}_transitive",
        attributes=combined_dependencies,
    )

    new_relation.add_primary_key(parent_relation.primary_key)
    new_relation.add_functional_dependency(
        parent_relation.primary_key, combined_dependencies
    )

    relations_in_3NF.append(new_relation)

    for attr in combined_dependencies + parent_relation.primary_key:
        if attr in all_parent_attributes:
            all_parent_attributes.remove(attr)

    if all_parent_attributes:
        remaining_relation = Relation(
            name=f"{parent_relation.name}_remaining",
            attributes=all_parent_attributes,
        )
        remaining_relation.add_primary_key(parent_relation.primary_key)
        relations_in_3NF.append(remaining_relation)

    return relations_in_3NF


# Adjusts determinants to equal the primary key, ensuring BCNF compliance
def determinants_equal_superkey(relation):
    primary_key = relation.primary_key
    for fd in relation.functional_dependencies:
        fd.adjust_to_primary_key(primary_key)


# Fixes multi-valued dependencies (MVDs) to achieve 4NF compliance
def fix_mvds(relation, mvds):
    relations_in_4NF = []
    primary_key = relation.primary_key
    pk_values = set()

    for data in relation.data:
        pk_value = tuple(str(data[attr]) for attr in primary_key)
        print(f"Checking primary key value: {pk_value}")

        if pk_value in pk_values:
            print(f"Duplicate primary key value detected: {pk_value}")
            new_pk_value = input(
                "Enter a unique primary key value for the duplicate entry in the secondary relation: "
            )
            data[primary_key[-1]] = new_pk_value.strip()
            pk_value = tuple(str(data[attr]) for attr in primary_key)
            print(f"Updated primary key value to: {pk_value}")

        pk_values.add(pk_value)

    for X, Y in mvds:
        non_pk_attributes = [
            attr for attr in relation.attributes if attr not in primary_key
        ]

        table1 = Relation(
            name=f"{relation.name}_{non_pk_attributes[0]}",
            attributes=X + [non_pk_attributes[0]],
        )
        table2 = Relation(
            name=f"{relation.name}_{non_pk_attributes[1]}",
            attributes=X + [non_pk_attributes[1]],
        )

        for data in relation.data:
            data_table1 = {attr: str(data[attr]) for attr in table1.attributes}
            data_table2 = {attr: str(data[attr]) for attr in table2.attributes}
            print(f"Adding data to table1: {data_table1}")
            print(f"Adding data to table2: {data_table2}")
            table1.add_tuple(data_table1)
            table2.add_tuple(data_table2)

        table1.add_functional_dependency(X, [non_pk_attributes[0]])
        table2.add_functional_dependency(X, [non_pk_attributes[1]])

        relations_in_4NF.append(table1)
        relations_in_4NF.append(table2)

    return relations_in_4NF


# Adds a functional dependency to the relation if primary key and X are equal
def add_functional_dependency_if_pk_equal(relation, primary_key, X, Y):
    if len(primary_key) == len(X) and all(pk == x for pk, x in zip(primary_key, X)):
        relation.add_functional_dependency(X, Y)


# Ensures join dependencies are satisfied to achieve 5NF compliance
def ensure_join_dependencies(relation, anomalies):
    new_relations = []
    decomposed_relations = {}

    for anomaly in anomalies:
        determinant, dependent = anomaly
        determinant_key = tuple(determinant)

        if determinant_key not in decomposed_relations:
            new_relation = Relation(
                name=f"{relation.name}_{'_'.join(determinant)}",
                attributes=determinant + dependent,
            )
            new_relation.add_primary_key(determinant)
            new_relation.add_foreign_key(determinant)
            decomposed_relations[determinant_key] = new_relation
            new_relations.append(new_relation)

        for data in relation.data:
            new_tuple = {attr: data[attr] for attr in determinant + dependent}
            decomposed_relations[determinant_key].add_tuple(new_tuple)

    remaining_attributes = [
        attr
        for attr in relation.attributes
        if all(attr not in dep for _, dep in anomalies)
    ]
    if remaining_attributes:
        final_relation = Relation(
            name=f"{relation.name}_remaining", attributes=remaining_attributes
        )
        final_relation.add_primary_key(relation.primary_key)
        final_relation.data = relation.data[:]
        new_relations.append(final_relation)

    return new_relations


# --------------------------------- Normalize Functions ---------------------------------


# Normalizes a relation to 1NF by eliminating non-atomic attributes
def normalize_1NF(relation):
    print_normalization_stage("1NF Normalization Started")
    anomalies = detect_1NF_anomalies(relation)

    if anomalies:
        print_normalization_stage(
            f"Detected non-atomic attribute(s): {', '.join(anomalies)}"
        )
    else:
        print_normalization_stage("No non-atomic attributes found.")

    print_normalization_stage("Relations in 1NF")

    stored_fds = relation.functional_dependencies[:]
    stored_data = relation.data[:]
    final_1NF_relations = []

    if anomalies:
        new_relations = fix_non_atomic_attributes(relation, anomalies)
        for new_relation in new_relations:
            for fd in stored_fds:
                new_relation.add_functional_dependency(fd.get_x(), fd.get_y())
            new_relation.data = stored_data[:]
            final_1NF_relations.append(new_relation)
    else:
        final_1NF_relations.append(relation)

    for final_relation in final_1NF_relations:
        if not final_relation.primary_key:
            primary_key_name = f"{relation.name}_id"
            final_relation.add_primary_key([primary_key_name])
    for count, final_relation in enumerate(final_1NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()

    return final_1NF_relations


# Normalizes a relation to 2NF by addressing partial functional dependencies
def normalize_2NF(relation):
    print_normalization_stage("2NF Normalization Started")
    list_of_1NF_relations = normalize_1NF(relation)
    final_2NF_relations = []

    for rel in list_of_1NF_relations:
        anomalies = detect_2NF_anomalies(rel)
        stored_data = rel.data[:]

        if anomalies:
            print_normalization_stage(
                f"Detected partial functional dependencies: {', '.join(anomalies)}"
            )
            new_relations = fix_partial_functional_dependencies(rel, anomalies)

            for new_relation in new_relations:
                new_relation.data = stored_data[:]
                final_2NF_relations.append(new_relation)
        else:
            print_normalization_stage("No partial functional dependencies found.")
            final_2NF_relations.append(rel)

    print_normalization_stage("Relations in 2NF")
    for count, final_relation in enumerate(final_2NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()

    return final_2NF_relations


# Normalizes a relation to 3NF by addressing transitive dependencies
def normalize_3NF(relation):
    print_normalization_stage("3NF Normalization Started")
    relations = normalize_2NF(relation)
    final_3NF_relations = []

    for rel in relations:
        anomalies = detect_3NF_anomalies(rel)
        stored_data = rel.data[:]

        if anomalies:
            print_normalization_stage(
                f"Detected transitive dependencies: {', '.join(anomalies)}"
            )
            new_relations = fix_transitive_functional_dependencies(rel, anomalies)

            for new_relation in new_relations:
                new_relation.data = stored_data[:]
                final_3NF_relations.append(new_relation)
        else:
            print_normalization_stage("No transitive dependencies found.")
            final_3NF_relations.append(rel)

    print_normalization_stage("Relations in 3NF")
    for count, final_relation in enumerate(final_3NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()

    return final_3NF_relations


# Normalizes a relation to BCNF by ensuring every determinant is a superkey
def normalize_BCNF(relation):
    print_normalization_stage("BCNF Normalization Started")
    list_of_3NF_relations = normalize_3NF(relation)
    final_BCNF_relations = []

    for rel in list_of_3NF_relations:
        anomalies = detect_BCNF_anomalies(rel)
        stored_data = rel.data[:]

        if anomalies:
            print_normalization_stage(
                f"Detected determinants that are not superkeys: {', '.join(str(anomaly) for anomaly in anomalies)}"
            )
            determinants_equal_superkey(rel)
            rel.data = stored_data[:]
            final_BCNF_relations.append(rel)
        else:
            print_normalization_stage("No BCNF violations found.")
            final_BCNF_relations.append(rel)

    print_normalization_stage("Relations in BCNF")
    for count, final_relation in enumerate(final_BCNF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()
        print_data(final_relation)

    return final_BCNF_relations


# Normalizes a relation to 4NF by addressing multi-valued dependencies
def normalize_4NF(relation):
    print_normalization_stage("4NF Normalization Started")
    bcnf_relations = normalize_BCNF(relation)
    final_4NF_relations = []

    for bcnf_relation in bcnf_relations:
        mvds = detect_4NF_anomalies(bcnf_relation)
        stored_fds = bcnf_relation.functional_dependencies[:]
        stored_data = bcnf_relation.data[:]

        if mvds:
            print_normalization_stage(
                f"Detected multivalued dependencies: {', '.join(str(mvd) for mvd in mvds)}"
            )
            decomposed_relations_4NF = fix_mvds(bcnf_relation, mvds)
            for rel in decomposed_relations_4NF:
                rel.functional_dependencies = stored_fds[:]
                rel.data = stored_data[:]
                final_4NF_relations.append(rel)
        else:
            print_normalization_stage("No multivalued dependencies found.")
            final_4NF_relations.append(bcnf_relation)

    print_normalization_stage("Relations in 4NF")
    for count, final_relation in enumerate(final_4NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()
        print_data(final_relation)

    return final_4NF_relations


# Normalizes a relation to 5NF by handling join dependencies
def normalize_5NF(relation):
    print_normalization_stage("5NF Normalization Started")
    relations = normalize_4NF(relation)
    final_5NF_relations = []

    for rel in relations:
        keys = rel.primary_key

        if isinstance(rel.data, list) and all(isinstance(d, dict) for d in rel.data):
            anomalies = detect_5NF_anomalies(rel)
            stored_fds = rel.functional_dependencies[:]
            stored_data = rel.data[:]

            if anomalies:
                print_normalization_stage(
                    f"Detected join dependencies: {', '.join(str(anomaly) for anomaly in anomalies)}"
                )
                list_of_5NF_relations = ensure_join_dependencies(rel, anomalies)
                for decomposed_relation in list_of_5NF_relations:
                    for fd in stored_fds:
                        add_functional_dependency_if_pk_equal(
                            decomposed_relation,
                            decomposed_relation.primary_key,
                            fd.get_x(),
                            fd.get_y(),
                        )
                    decomposed_relation.data = stored_data[:]
                    final_5NF_relations.append(decomposed_relation)
            else:
                print_normalization_stage("No join dependencies found.")
                final_5NF_relations.append(rel)

    print_normalization_stage("Relations in 5NF")
    for count, final_relation in enumerate(final_5NF_relations, start=1):
        final_relation.name = count
        final_relation.print_relation()
        print_data(final_relation)

    return final_5NF_relations


# --------------------------------- Detect Anomaly Functions ---------------------------------


# Detects anomalies in 1NF by checking for non-atomic attributes
def detect_1NF_anomalies(relation):
    anomalies = []
    for attribute in relation.attributes:
        is_atomic = input(f"Is '{attribute}' atomic? (yes/no): ").strip().lower()
        if is_atomic == "no":
            anomalies.append(attribute)
    return anomalies


# Detects anomalies in 2NF by identifying partial dependencies
def detect_2NF_anomalies(relation):
    anomalies = []

    primary_key = set()
    for pk in relation.primary_key:
        if isinstance(pk, list):
            primary_key.update(str(attr).strip() for attr in pk)
        else:
            primary_key.add(str(pk).strip())

    all_keys = set()
    for sublist in [relation.candidate_keys + relation.foreign_keys]:
        for key in sublist:
            if isinstance(key, list):
                all_keys.update([",".join(map(str.strip, key))])
            else:
                all_keys.add(str(key).strip())

    all_keys = all_keys.union({str(key).strip() for key in primary_key})

    flat_attributes = (
        {str(attr).strip() for sublist in relation.attributes for attr in sublist}
        if any(isinstance(attr, list) for attr in relation.attributes)
        else {str(attr).strip() for attr in relation.attributes}
    )
    non_keys = [attr for attr in flat_attributes if attr not in all_keys]

    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()
        X_set = set(str(attr).strip() for attr in X)

        if X_set.issubset(primary_key) and X_set != primary_key:
            if all(y in non_keys for y in Y):
                anomalies.extend(Y)

    return anomalies


# Detects anomalies in 3NF by identifying transitive dependencies
def detect_3NF_anomalies(relation):
    anomalies = []
    primary_key_sets = []

    for pk in relation.primary_key:
        pk_str = pk if isinstance(pk, str) else ",".join(pk)
        primary_key_sets.append(pk_str)

    non_keys = [
        attr
        for attr in relation.attributes
        if isinstance(attr, str)
        and attr
        not in {item for sublist in primary_key_sets for item in sublist.split(",")}
    ]

    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()

        if not any(
            set(primary_key.split(",")).issubset(set(X))
            for primary_key in primary_key_sets
        ):
            for y in Y:
                if y in non_keys:
                    primary_keys_str = "|".join(
                        ["|".join(pk.split(",")) for pk in primary_key_sets]
                    )
                    X_str = "|".join(X)
                    Y_str = "|".join(Y)
                    anomalies.append(f"{primary_keys_str}|{X_str}|{Y_str}")

    return anomalies


# Detects BCNF anomalies by ensuring all determinants are superkeys
def detect_BCNF_anomalies(relation):
    anomalies = []
    primary_key_sets = [
        set(pk) if isinstance(pk, list) else {pk} for pk in relation.primary_key
    ]

    for fd in relation.functional_dependencies:
        determinant_set = set(fd.get_x())

        if not any(determinant_set.issuperset(pk_set) for pk_set in primary_key_sets):
            anomalies.append(fd)

    return anomalies


# Detects 4NF anomalies by identifying multi-valued dependencies (MVDs)
def detect_4NF_anomalies(relation):
    mvds = []

    primary_key_attribute = str(relation.primary_key[0]).strip("[]'\" ,")

    attribute_positions = list(relation.data[0].keys())
    primary_key_position = None

    for count, attr in enumerate(attribute_positions):
        current_attr = str(attr).strip("[]'\" ,")

        if primary_key_attribute == current_attr:
            primary_key_position = current_attr
            break

    if primary_key_position is None:
        return []

    unique_keys = set()

    for i, data in enumerate(relation.data):
        primary_key_value = str(data[primary_key_position]).strip("[]'\" ,")

        if primary_key_value in unique_keys:
            print_divider()
            print(
                f"Anomaly detected in tuple {i} with primary key value = '{primary_key_value}'"
            )
            new_value = str(
                input(
                    f"Enter a unique value for the primary key attribute '{primary_key_position}': "
                )
            ).strip("[]'\" ,")
            print_divider()
            data[primary_key_position] = new_value
        else:
            unique_keys.add(primary_key_value)

    for idx, data in enumerate(relation.data, start=1):
        print(f"Tuple {idx}: {data}")

    return mvds


# Detects 5NF anomalies by identifying join dependencies in the relation
def detect_5NF_anomalies(relation):
    join_dependencies = []
    attributes = relation.attributes

    for i in range(len(attributes)):
        X = attributes[:i] + attributes[i + 1 :]
        Y = [attributes[i]]

        if check_join_dependency(relation, X, Y):
            join_dependencies.append((X, Y))

    return join_dependencies


# Checks if a join dependency exists between attribute sets X and Y
def check_join_dependency(relation, X, Y):
    for data in relation.data:
        if all(attr in data for attr in X + Y):
            return True
    return False
