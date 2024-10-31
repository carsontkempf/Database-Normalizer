from classes import *
from helper_functions import *

# --------------------------------- Print Functions ---------------------------------


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(stage_name)
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

    # If there are remaining attributes, add them as a final relation
    if all_parent_attributes:
        uncleaned_remaining_attributes = primary_key + all_parent_attributes
        cleaned_remaining_attributes = remove_duplicate_attributes(
            uncleaned_remaining_attributes
        )
        remaining_relation = Relation(
            name=f"{parent_relation.name}_remaining",
            attributes=cleaned_remaining_attributes,
        )
        remaining_relation.primary_key = primary_key[:]
        new_relations.append(remaining_relation)

    return new_relations


def fix_partial_functional_dependencies(parent_relation, anomalies):
    # Initialize a list to store the 2NF relations
    relations_in_2NF = []

    # Collect all attributes of the parent relation for reference
    all_parent_attributes = [str(attr).strip() for attr in parent_relation.attributes]

    # Create a new relation for each anomaly
    for anomaly in anomalies:
        # Initialize a new relation with the primary key and the anomaly as attributes
        new_relation = Relation(
            name=f"{parent_relation.name}_{anomaly}",
            attributes=parent_relation.primary_key[:],  # Copy primary key
        )

        # Add the anomaly attribute to the new relation
        new_relation.attributes.append(anomaly)
        new_relation.add_primary_key(parent_relation.primary_key)

        new_relation.add_functional_dependency(parent_relation.primary_key, anomaly)

        relations_in_2NF.append(new_relation)

        # Remove the anomaly attribute from all_parent_attributes to prevent duplication
        if anomaly in all_parent_attributes:
            all_parent_attributes.remove(anomaly)

    # If there are remaining attributes, add them to a final relation
    if all_parent_attributes:
        new_relation = Relation(
            name=f"{parent_relation.name}_remaining",
            attributes=all_parent_attributes,
        )
        new_relation.add_primary_key(parent_relation.primary_key)
        relations_in_2NF.append(new_relation)

    return relations_in_2NF


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
    allowed_attributes = set(original_attributes)
    unflattened_attributes = []

    # Collect attributes that are allowed based on the parent relation
    for attr in decomposed_relation.attributes:
        if isinstance(attr, str) and attr in allowed_attributes:
            unflattened_attributes.append(attr)

    unique_flattened_attrs = remove_duplicate_attributes(unflattened_attributes)

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
    print_normalization_stage("1NF Normalization Started")
    anomalies = detect_1NF_anomalies(relation)

    # Print detected non-atomic attributes if any
    if anomalies:
        print(f"Detected non-atomic attribute(s): {', '.join(anomalies)}")
    else:
        print("No non-atomic attributes found.")

    print_normalization_stage("Relations in 1NF")

    # Store original functional dependencies and data
    stored_fds = relation.functional_dependencies[:]
    stored_data = relation.data[:]
    final_1NF_relations = []

    # Fix non-atomic attributes by decomposing into new relations
    if anomalies:
        new_relations = fix_non_atomic_attributes(relation, anomalies)
        for new_relation in new_relations:
            new_relation.functional_dependencies = stored_fds[:]
            new_relation.data = stored_data[:]
            final_1NF_relations.append(new_relation)
    else:
        final_1NF_relations.append(relation)

    # Print final 1NF relations with naming as 1, 2, 3, ...
    for count, final_relation in enumerate(final_1NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()

    return final_1NF_relations


def normalize_2NF(relation):
    print_normalization_stage("2NF Normalization Started")
    list_of_1NF_relations = normalize_1NF(relation)
    final_2NF_relations = []

    for rel in list_of_1NF_relations:
        anomalies = detect_2NF_anomalies(rel)
        stored_data = rel.data[:]  # Store original data for each relation

        if anomalies:
            print_normalization_stage(
                f"Detected partial functional dependencies: {', '.join(anomalies)}"
            )

            # Call fix_partial_functional_dependencies, which returns multiple relations
            new_relations = fix_partial_functional_dependencies(rel, anomalies)

            # For each new relation, assign the stored data and add it to final_2NF_relations
            for new_relation in new_relations:
                new_relation.data = stored_data[
                    :
                ]  # Copy stored data to each new relation
                final_2NF_relations.append(new_relation)
        else:
            print("No partial functional dependencies found.")
            final_2NF_relations.append(rel)

    print_normalization_stage("Relations in 2NF")
    for count, final_relation in enumerate(final_2NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()

    return final_2NF_relations


def normalize_3NF(relation):
    print_normalization_stage("3NF Normalization Started")
    relations = normalize_2NF(relation)
    final_3NF_relations = []

    for rel in relations:
        anomalies = detect_3NF_anomalies(rel)
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]
        if anomalies:
            print(f"Detected transitive dependencies: {', '.join(anomalies)}")
        else:
            print("No anomalies detected for 3NF.")

        if anomalies:
            list_of_3NF_relations = decompose_relation(rel, anomalies, "3", stored_fds)
            for decomposed_relation in list_of_3NF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                final_3NF_relations.append(decomposed_relation)
        else:
            final_3NF_relations.append(rel)

    print_normalization_stage("Relations in 3NF")
    for count, final_relation in enumerate(final_3NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()
        print_data(final_relation)

    return final_3NF_relations


def normalize_BCNF(relation):
    print_normalization_stage("BCNF Normalization Started")
    relations = normalize_3NF(relation)
    final_BCNF_relations = []

    for rel in relations:
        anomalies = detect_BCNF_anomalies(rel)
        if anomalies:
            print(f"Detected BCNF anomalies: {', '.join(str(a) for a in anomalies)}")
        else:
            print("All determinants are equal to a primary key.")
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]

        if anomalies:
            list_of_BCNF_relations = decompose_relation(rel, anomalies, "B", stored_fds)
            for decomposed_relation in list_of_BCNF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                final_BCNF_relations.append(decomposed_relation)
        else:
            final_BCNF_relations.append(rel)

    print_normalization_stage("Relations in BCNF")
    for count, final_relation in enumerate(final_BCNF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()
        print_data(final_relation)

    return final_BCNF_relations


def normalize_4NF(relation):
    print_normalization_stage("4NF Normalization Started")
    bcnf_relations = normalize_BCNF(relation)
    final_4NF_relations = []

    for bcnf_relation in bcnf_relations:
        mvds = detect_4NF_anomalies(bcnf_relation)
        stored_fds = bcnf_relation.functional_dependencies[:]
        stored_data = bcnf_relation.data[:]

        if mvds:
            decomposed_relations_4NF = fix_mvds(bcnf_relation, mvds)
            for rel in decomposed_relations_4NF:
                rel.functional_dependencies = stored_fds[:]
                rel.data = stored_data[:]
                final_4NF_relations.append(rel)
        else:
            final_4NF_relations.append(bcnf_relation)

        if mvds:
            print(f"Detected multivalued dependencies: {mvds}")
        else:
            print("No anomalies detected for 4NF.")

    print_normalization_stage("Relations in 4NF")
    for count, final_relation in enumerate(final_4NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()
        print_data(final_relation)

    return final_4NF_relations


def normalize_5NF(relation):
    print_normalization_stage("5NF Normalization Started")
    relations = normalize_4NF(relation)
    final_5NF_relations = []

    for rel in relations:
        anomalies = detect_5NF_anomalies(rel)
        stored_fds = rel.functional_dependencies[:]
        stored_data = rel.data[:]

        if anomalies:
            list_of_5NF_relations = decompose_relation(rel, anomalies, "5", stored_fds)
            for decomposed_relation in list_of_5NF_relations:
                decomposed_relation.functional_dependencies = stored_fds[:]
                decomposed_relation.data = stored_data[:]
                final_5NF_relations.append(decomposed_relation)
        else:
            final_5NF_relations.append(rel)

    print_normalization_stage("Relations in 5NF")
    for count, final_relation in enumerate(final_5NF_relations, start=1):
        final_relation.name = str(count)
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

    # Convert each element in primary_key to a set of cleaned, individual components
    primary_key = set()
    for pk in relation.primary_key:
        # Split composite keys and clean whitespace
        if isinstance(pk, list):
            primary_key.update(str(attr).strip() for attr in pk)
        else:
            primary_key.add(str(pk).strip())

    # Collect all key attributes (primary, candidate, and foreign keys)
    all_keys = primary_key.union(
        *[
            set(str(attr).strip() for attr in (key if isinstance(key, list) else [key]))
            for key in relation.candidate_keys + relation.foreign_keys
        ]
    )

    # Identify non-key attributes
    non_keys = [attr for attr in relation.attributes if attr not in all_keys]

    # Check each functional dependency for 2NF anomalies
    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()
        X_set = set(str(attr).strip() for attr in X)  # Convert X to a cleaned set

        # Check if X is a proper subset of the primary key
        if X_set.issubset(primary_key) and X_set != primary_key:
            # Ensure all elements in Y are non-key attributes
            if all(y in non_keys for y in Y):
                anomalies.extend(Y)  # Add the dependent attributes causing anomalies

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
