from classes import *
from helper_functions import *

# --------------------------------- Print Functions ---------------------------------


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(f"Starting {stage_name}")
    print_divider()


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


def fix_partial_functional_dependencies(parent_relation, decomposed_relation):
    adjusted_fds = []

    for fd in parent_relation.functional_dependencies:
        fd_x = set(fd.get_x())
        fd_y = set(fd.get_y())
        primary_key_sets = [set(pk.split("|")) for pk in parent_relation.primary_key]

        # Check if the X attributes (determinants) are in the decomposed relation
        if fd_x.issubset(decomposed_relation.attributes):
            # Ensure all Y attributes (dependents) are added to the decomposed relation
            for y_attr in fd_y:
                if y_attr not in decomposed_relation.attributes:
                    decomposed_relation.attributes.append(y_attr)

            # Check if the FD is a partial dependency
            if any(fd_x.issubset(pk) and fd_x != pk for pk in primary_key_sets):
                print(f"Partial dependency detected: {fd_x} -> {fd_y}")
                adjusted_fd = FunctionalDependency(list(fd_x), list(fd_y))
                adjusted_fds.append(adjusted_fd)
            else:
                adjusted_fds.append(fd)

    return adjusted_fds


def fix_transitive_functional_dependencies(relation):
    primary_key_sets = [set(str(pk).split("|")) for pk in relation.primary_key]
    transitive_dependents = set()
    new_fds = []
    direct_dependencies = set()

    for fd in relation.functional_dependencies:
        fd_x = set(fd.get_x())
        fd_y = set(fd.get_y())

        # Check if fd_x exactly matches any primary key set
        if any(fd_x == pk for pk in primary_key_sets):
            new_fds.append(fd)
            direct_dependencies.update(fd_y)
        else:
            if fd_x.issubset(direct_dependencies):
                print(f"Transitive dependency detected: {fd_x} -> {fd_y}")
                transitive_dependents.update(fd_y)

    if transitive_dependents:
        consolidated_fd = FunctionalDependency(
            list(primary_key_sets[0]), list(transitive_dependents)
        )
        new_fds.append(consolidated_fd)

    return new_fds


def fix_mvds(relation, mvds):
    new_relations = []
    primary_key = relation.primary_key  # Keep as list of strings

    pk_values = set()
    for data in relation.data:
        pk_value = tuple(data[attr] for attr in primary_key)
        while pk_value in pk_values:
            print(f"Duplicate primary key value detected: {pk_value}")
            new_pk_value = input(
                f"Enter a unique primary key value for {primary_key}: "
            )
            for attr in primary_key:
                data[attr] = new_pk_value.strip()
            pk_value = tuple(data[attr] for attr in primary_key)
        pk_values.add(pk_value)

    for X, Y in mvds:
        attributes = X + Y
        new_relation = Relation(
            name=f"{relation.name}_{'_'.join(Y)}", attributes=attributes
        )
        new_relation.primary_key = X
        new_relation.functional_dependencies = [FunctionalDependency(X, Y)]

        for data in relation.data:
            new_data = {attr: data[attr] for attr in attributes}
            new_relation.add_tuple(new_data)

        new_relations.append(new_relation)

    return new_relations


def nested_to_tuple(lst):
    # Recursively convert lists within lists to tuples
    return tuple(nested_to_tuple(i) if isinstance(i, list) else i for i in lst)


def exclude_duplicate_relations(
    decomposed_relation, decomposed_relation_list, original_attributes
):
    # Define allowed attributes dynamically from the parent relation's original attributes
    allowed_attributes = set(original_attributes)

    # Create a list to hold only the allowed attributes from non-nested values
    flattened_attrs = []

    # Iterate through each attribute in decomposed_relation, capturing only simple strings that are allowed
    for attr in decomposed_relation.attributes:
        if isinstance(attr, str) and attr in allowed_attributes:
            flattened_attrs.append(attr)

    # Remove duplicates to ensure only unique allowed attributes remain
    unique_flattened_attrs = list(set(flattened_attrs))

    # Check if the unique list matches the allowed attributes exactly
    if set(unique_flattened_attrs) != allowed_attributes:
        print(
            f"Duplicate or invalid attributes detected in {unique_flattened_attrs}, skipping addition."
        )
        return decomposed_relation_list  # Skip if attributes don't match exactly

    # Prepare the unique list of attributes to add
    decomposed_relation.attributes = (
        unique_flattened_attrs  # Assign the filtered unique attributes
    )

    # Check against existing relations to avoid exact duplicates or subset relations
    to_remove = []
    for existing_relation in decomposed_relation_list:
        # Filter existing relation to match only the allowed attributes
        existing_flattened_attrs = [
            attr for attr in existing_relation.attributes if attr in allowed_attributes
        ]

        # Compare attribute sets to detect exact duplicates or subsets
        if set(unique_flattened_attrs) == set(existing_flattened_attrs):
            print(f"Skipping exact duplicate relation: {unique_flattened_attrs}")
            return decomposed_relation_list
        elif set(existing_flattened_attrs).issubset(unique_flattened_attrs):
            print(
                f"Removing subset relation: {existing_relation.attributes} in favor of {unique_flattened_attrs}"
            )
            to_remove.append(existing_relation)
        elif set(unique_flattened_attrs).issubset(existing_flattened_attrs):
            print(
                f"Skipping subset relation: {unique_flattened_attrs} since {existing_relation.attributes} already exists"
            )
            return decomposed_relation_list

    # Remove identified duplicates or subsets
    for relation in to_remove:
        decomposed_relation_list.remove(relation)

    # Append the unique relation
    decomposed_relation_list.append(decomposed_relation)
    print(f"Adding new relation: {unique_flattened_attrs}")

    return decomposed_relation_list


# --------------------------------- Decompose ---------------------------------


def filter_functional_dependencies(
    parent_relation, decomposed_relation, normalization_stage, stored_fds
):
    decomposed_relation.primary_key = parent_relation.primary_key[:]
    decomposed_relation.foreign_keys = parent_relation.foreign_keys[:]
    decomposed_relation.candidate_keys = parent_relation.candidate_keys[:]
    decomposed_relation.functional_dependencies = []

    for fd in stored_fds:
        # Only add FDs relevant to the decomposed relation’s attributes
        if set(fd.get_x()).issubset(decomposed_relation.attributes):
            if normalization_stage == "1":
                if set(fd.get_y()).issubset(decomposed_relation.attributes):
                    decomposed_relation.functional_dependencies.append(fd)
            elif normalization_stage == "2":
                decomposed_relation.functional_dependencies.extend(
                    fix_partial_functional_dependencies(
                        parent_relation, decomposed_relation
                    )
                )
            elif normalization_stage == "3":
                decomposed_relation.functional_dependencies.extend(
                    fix_transitive_functional_dependencies(decomposed_relation)
                )
            elif normalization_stage == "B":
                if any(
                    set(fd.get_x()).issuperset(set(str(pk).split("|")))
                    for pk in decomposed_relation.primary_key
                ):
                    decomposed_relation.functional_dependencies.append(fd)
            elif normalization_stage == "4":
                # Detect MVDs for 4NF and include relevant functional dependencies
                mvds = detect_4NF_anomalies(parent_relation)
                if mvds:
                    for X, Y in mvds:
                        if set(X).issubset(decomposed_relation.attributes) and set(
                            Y
                        ).issubset(decomposed_relation.attributes):
                            decomposed_relation.functional_dependencies.append(
                                FunctionalDependency(X, Y)
                            )

    return [decomposed_relation]


def decompose_relation(parent_relation, anomaly_list, normalization_stage, stored_fds):
    if not anomaly_list:
        return []

    decomposed_relation_list = []
    count = 1
    all_parent_attributes = parent_relation.attributes[:]

    print("\nStarting decomposition for anomalies...\n")

    for anomaly in anomaly_list:
        decomposed_relation = Relation(name=str(count), attributes=[])
        count += 1  # Unique naming for each relation

        # Handle anomaly attributes
        if isinstance(anomaly, FunctionalDependency):
            anomaly_attributes = anomaly.get_x() + anomaly.get_y()
        else:
            anomaly_attributes = anomaly

        for attr in anomaly_attributes:
            if attr in all_parent_attributes:
                all_parent_attributes.remove(attr)
            decomposed_relation.attributes.append(attr)

        # Ensure primary keys and functional dependencies are passed down
        decomposed_relation.primary_key = parent_relation.primary_key
        decomposed_relation.functional_dependencies = stored_fds[:]  # Pass down FDs

        for pk in parent_relation.primary_key:
            pk_str = str(pk)  # Convert pk to a string if it isn't already
            for attr in pk_str.split("|"):
                if attr not in decomposed_relation.attributes:
                    decomposed_relation.attributes.append(attr)

        # Filter functional dependencies for the decomposed relation
        filtered_relations = filter_functional_dependencies(
            parent_relation, decomposed_relation, normalization_stage, stored_fds
        )

        for relation in filtered_relations:
            decomposed_relation_list = exclude_duplicate_relations(
                relation, decomposed_relation_list, parent_relation.attributes
            )

    # Handle remaining attributes as a final relation if they exist
    if all_parent_attributes:
        remaining_relation = Relation(name=str(count), attributes=all_parent_attributes)
        remaining_relation.primary_key = parent_relation.primary_key
        remaining_relation.functional_dependencies = stored_fds[:]

        filtered_relations = filter_functional_dependencies(
            parent_relation, remaining_relation, normalization_stage, stored_fds
        )

        for relation in filtered_relations:
            decomposed_relation_list = exclude_duplicate_relations(
                relation, decomposed_relation_list, parent_relation.attributes
            )

    return decomposed_relation_list


# --------------------------------- Normalize Functions ---------------------------------


def normalize_1NF(relation):
    print_normalization_stage("1NF Normalization")
    anomalies = detect_1NF_anomalies(relation)

    print_normalization_stage("Final 1NF Relations")

    # Store the original functional dependencies and data
    stored_fds = relation.functional_dependencies[:]
    stored_data = relation.data[:]

    if anomalies:
        list_of_1NF_relations = decompose_relation(relation, anomalies, "1", stored_fds)
        for decomposed_relation in list_of_1NF_relations:
            decomposed_relation.functional_dependencies = stored_fds[:]
            decomposed_relation.data = stored_data[:]
            decomposed_relation.print_relation()
        return list_of_1NF_relations
    else:
        relation.print_relation()
        return [relation]


def normalize_2NF(relation):
    print_normalization_stage("2NF Normalization")
    list_of_1NF_relations = normalize_1NF(relation)
    final_2NF_relations = []

    for rel in list_of_1NF_relations:
        anomalies = detect_2NF_anomalies(rel)

        # Store and pass down functional dependencies and data
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]

        if anomalies:
            list_of_2NF_relations = decompose_relation(rel, anomalies, "2", stored_fds)
            for decomposed_relation in list_of_2NF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                final_2NF_relations.append(decomposed_relation)
        else:
            rel.functional_dependencies = stored_fds[:]
            rel.data = stored_data[:]
            final_2NF_relations.append(rel)

    print_normalization_stage("Final 2NF Relations")
    for index, final_relation in enumerate(final_2NF_relations, start=1):
        final_relation.name = index
        final_relation.print_relation()

    return final_2NF_relations


def normalize_3NF(relation):
    print_normalization_stage("3NF Normalization")
    relations = normalize_2NF(relation)
    final_3NF_relations = []
    relation_counter = 1

    for rel in relations:
        anomalies = detect_3NF_anomalies(rel)

        # Store and pass down functional dependencies and data
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]

        if anomalies:
            list_of_3NF_relations = decompose_relation(rel, anomalies, "3", stored_fds)
            for decomposed_relation in list_of_3NF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                decomposed_relation.name = relation_counter
                final_3NF_relations.append(decomposed_relation)
                relation_counter += 1
        else:
            rel.functional_dependencies = stored_fds[:]
            rel.data = stored_data[:]
            rel.name = relation_counter
            final_3NF_relations.append(rel)
            relation_counter += 1

    print_normalization_stage("Final 3NF Relations")
    for final_relation in final_3NF_relations:
        final_relation.print_relation()

    return final_3NF_relations


def normalize_BCNF(relation):
    print_normalization_stage("BCNF Normalization")
    relations = normalize_3NF(relation)
    final_BCNF_relations = []
    relation_counter = 1

    for rel in relations:
        anomalies = detect_BCNF_anomalies(rel)

        # Store and pass down functional dependencies and data
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]

        if anomalies:
            list_of_BCNF_relations = decompose_relation(rel, anomalies, "B", stored_fds)
            for decomposed_relation in list_of_BCNF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                decomposed_relation.name = relation_counter
                final_BCNF_relations.append(decomposed_relation)
                relation_counter += 1
        else:
            rel.functional_dependencies = stored_fds[:]
            rel.data = stored_data[:]
            rel.name = relation_counter
            final_BCNF_relations.append(rel)
            relation_counter += 1

    print_normalization_stage("Final BCNF Relations")
    for final_relation in final_BCNF_relations:
        final_relation.print_relation()
        print_data(final_relation)  # Print data for each BCNF relation

    return final_BCNF_relations


def normalize_4NF(relation):
    print_normalization_stage("4NF Normalization")
    bcnf_relations = normalize_BCNF(relation)
    final_4NF_relations = []
    relation_counter = 1

    for bcnf_relation in bcnf_relations:
        mvds = detect_4NF_anomalies(bcnf_relation)

        # Store and pass down functional dependencies and data
        stored_fds = bcnf_relation.functional_dependencies[:]
        stored_data = bcnf_relation.data[:]

        if mvds:
            decomposed_relations_4NF = fix_mvds(bcnf_relation, mvds)
            for rel in decomposed_relations_4NF:
                rel.functional_dependencies = stored_fds[:]
                rel.data = stored_data[:]
                rel.name = relation_counter
                final_4NF_relations.append(rel)
                relation_counter += 1
        else:
            bcnf_relation.functional_dependencies = stored_fds[:]
            bcnf_relation.data = stored_data[:]
            bcnf_relation.name = relation_counter
            final_4NF_relations.append(bcnf_relation)
            relation_counter += 1

    print_normalization_stage("Final 4NF Relations")
    for final_relation in final_4NF_relations:
        final_relation.print_relation()
        print_data(final_relation)

    return final_4NF_relations


def normalize_5NF(relation):
    print_normalization_stage("5NF Normalization")
    relations = normalize_4NF(relation)
    final_5NF_relations = []
    relation_counter = 1

    for rel in relations:
        anomalies = detect_5NF_anomalies(rel)

        # Store and pass down functional dependencies and data
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]

        if anomalies:
            list_of_5NF_relations = decompose_relation(rel, anomalies, "5", stored_fds)
            for decomposed_relation in list_of_5NF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                decomposed_relation.name = relation_counter
                final_5NF_relations.append(decomposed_relation)
                relation_counter += 1
        else:
            rel.functional_dependencies = stored_fds[:]
            rel.data = stored_data[:]
            rel.name = relation_counter
            final_5NF_relations.append(rel)
            relation_counter += 1

    print_normalization_stage("Final 5NF Relations")
    for final_relation in final_5NF_relations:
        final_relation.print_relation()
        print_data(final_relation)

    return final_5NF_relations


# --------------------------------- Detect Anomaly Functions ---------------------------------


def detect_1NF_anomalies(relation):
    anomalies = []
    for attribute in relation.attributes:
        is_atomic = input(f"Is '{attribute}' atomic? (yes/no): ").strip().lower()
        if is_atomic == "no":
            anomalies.append(attribute)
    return anomalies


def detect_2NF_anomalies(relation):
    anomalies = []
    primary_key = relation.primary_key
    all_keys = primary_key[:]
    for key in relation.candidate_keys + relation.foreign_keys:
        all_keys.extend(key)

    non_keys = [attr for attr in relation.attributes if attr not in all_keys]
    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()
        for pk in primary_key:
            if isinstance(pk, list):
                pk = "|".join(pk)
            if set(X).issubset(set(pk.split("|"))) and set(X) != set(pk.split("|")):
                non_key_Y = [y for y in Y if y in non_keys]
                if non_key_Y:
                    anomalies.append("|".join(non_key_Y))
    return anomalies


def detect_3NF_anomalies(relation):
    anomalies = []
    primary_key_sets = []

    # Ensure each pk becomes a string and split it on "," to build primary_key_sets
    for pk in relation.primary_key:
        pk_str = str(pk)  # Convert pk to a string if not already
        primary_key_sets.append(set(pk_str.split(",")))

    non_keys = [
        attr
        for attr in relation.attributes
        if attr not in {item for sublist in primary_key_sets for item in sublist}
    ]

    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()

        # Check if X is a superkey by comparing against primary_key_sets
        if not any(
            set(primary_key).issubset(set(X)) for primary_key in primary_key_sets
        ):
            for y in Y:
                if y in non_keys:
                    # Join primary keys, X, and Y as strings for the anomaly output
                    primary_keys_str = "|".join(
                        ["|".join(pk) for pk in primary_key_sets]
                    )
                    X_str = "|".join(X)
                    Y_str = "|".join(Y)
                    anomalies.append(f"{primary_keys_str}|{X_str}|{Y_str}")

    return anomalies


def detect_BCNF_anomalies(relation):
    anomalies = []
    primary_key_sets = [set(str(pk).split("|")) for pk in relation.primary_key]
    for fd in relation.functional_dependencies:
        fd_x = set(fd.get_x())
        if not any(fd_x.issuperset(pk) for pk in primary_key_sets):
            anomalies.append(fd)
    return anomalies


def detect_4NF_anomalies(relation):
    mvds = []
    primary_key_sets = [set(str(pk).split("|")) for pk in relation.primary_key]
    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()
        if set(X) in primary_key_sets:
            x_values = {tuple(data[attr] for attr in X) for data in relation.data}
            y_values = {tuple(data[attr] for attr in Y) for data in relation.data}
            if len(y_values) > 1:
                mvds.append((X, Y))
    return mvds


def has_independent_values(attribute, relation):
    independent_values = set()
    if attribute not in relation.attributes:
        return False

    try:
        for row in relation.data:
            independent_values.add(row[relation.attributes.index(attribute)])
    except KeyError:
        return False

    return len(independent_values) > 1
