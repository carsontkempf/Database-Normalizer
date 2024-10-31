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


def fix_transitive_functional_dependencies(parent_relation, transitive_dependencies):
    # Check if there are fewer than two functional dependencies; if so, no fixing is needed
    if len(parent_relation.functional_dependencies) < 2:
        return [
            parent_relation
        ]  # Return the original relation as a single-element list

    relations_in_3NF = []
    # Flatten and clean all attributes in parent_relation to remove any nested lists
    all_parent_attributes = []
    for attr in parent_relation.attributes:
        if isinstance(attr, list):
            all_parent_attributes.extend(str(sub_attr).strip() for sub_attr in attr)
        else:
            all_parent_attributes.append(str(attr).strip())

    # Flatten and clean all transitive dependency attributes
    combined_dependencies = set()  # Use a set to handle duplicates

    for dependency in transitive_dependencies:
        # Split each dependency on "|" or "," and clean whitespace
        for attr in dependency.replace("|", ",").split(","):
            cleaned_attr = attr.strip()  # Remove any whitespace around the attribute
            if cleaned_attr:  # Only add non-empty attributes
                combined_dependencies.add(cleaned_attr)

    # Convert combined dependencies to a list for easier manipulation
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

    # Initialize a new relation with primary key and combined dependencies as attributes
    new_relation = Relation(
        name=f"{parent_relation.name}_transitive",
        attributes=combined_dependencies,  # Start with primary key attributes
    )

    # Add only non-primary key combined dependencies to new relation
    new_relation.add_primary_key(parent_relation.primary_key)

    # Add a functional dependency with primary key as X and combined dependencies as Y
    new_relation.add_functional_dependency(
        parent_relation.primary_key, combined_dependencies
    )

    # Append the new relation to the list
    relations_in_3NF.append(new_relation)

    # Remove combined transitive dependency attributes and primary key from all_parent_attributes
    for attr in combined_dependencies + parent_relation.primary_key:
        if attr in all_parent_attributes:
            all_parent_attributes.remove(attr)

    # If there are remaining attributes, add them to a final relation
    if all_parent_attributes:
        remaining_relation = Relation(
            name=f"{parent_relation.name}_remaining",
            attributes=all_parent_attributes,
        )
        remaining_relation.add_primary_key(parent_relation.primary_key)
        relations_in_3NF.append(remaining_relation)

    return relations_in_3NF


def determinants_equal_superkey(relation):
    primary_key = relation.primary_key  # Assuming relation has a primary_key attribute
    for fd in relation.functional_dependencies:
        fd.adjust_to_primary_key(primary_key)  # Adjust determinant to match primary key


def fix_mvds(relation, mvds):
    relations_in_4NF = []
    primary_key = relation.primary_key  # Primary key attributes as list of strings
    pk_values = set()

    # Convert primary key values to strings and ensure unique primary key entries
    for data in relation.data:
        pk_value = tuple(str(data[attr]) for attr in primary_key)
        print(f"Checking primary key value: {pk_value}")

        if pk_value in pk_values:
            print(f"Duplicate primary key value detected: {pk_value}")
            new_pk_value = input(
                "Enter a unique primary key value for the duplicate entry in the secondary relation: "
            )
            data[primary_key[-1]] = (
                new_pk_value.strip()
            )  # Modify the last attribute in primary key for uniqueness
            pk_value = tuple(str(data[attr]) for attr in primary_key)
            print(f"Updated primary key value to: {pk_value}")

        pk_values.add(pk_value)

    # Process each MVD anomaly to create new relations
    for X, Y in mvds:
        non_pk_attributes = [
            attr for attr in relation.attributes if attr not in primary_key
        ]

        # Relation 1 with X + first non-primary key attribute
        table1 = Relation(
            name=f"{relation.name}_{non_pk_attributes[0]}",
            attributes=X + [non_pk_attributes[0]],
        )
        # Relation 2 with X + remaining non-primary key attributes
        table2 = Relation(
            name=f"{relation.name}_{non_pk_attributes[1]}",
            attributes=X + [non_pk_attributes[1]],
        )

        # Populate table1 and table2 with tuples, converting values to strings
        for data in relation.data:
            data_table1 = {attr: str(data[attr]) for attr in table1.attributes}
            data_table2 = {attr: str(data[attr]) for attr in table2.attributes}
            print(f"Adding data to table1: {data_table1}")
            print(f"Adding data to table2: {data_table2}")
            table1.add_tuple(data_table1)
            table2.add_tuple(data_table2)

        # Assign functional dependencies to the new relations
        table1.add_functional_dependency(X, [non_pk_attributes[0]])
        table2.add_functional_dependency(X, [non_pk_attributes[1]])

        # Append the two new relations to the list for 4NF
        relations_in_4NF.append(table1)
        relations_in_4NF.append(table2)

    return relations_in_4NF


def add_functional_dependency_if_pk_equal(relation, primary_key, X, Y):
    # Check if primary_key and X are equal in length and each corresponding position matches
    if len(primary_key) == len(X) and all(pk == x for pk, x in zip(primary_key, X)):
        relation.add_functional_dependency(X, Y)


def ensure_join_dependencies(relation, anomalies):
    new_relations = []
    decomposed_relations = {}

    # Loop through each anomaly to decompose
    for anomaly_index, anomaly in enumerate(anomalies, start=1):
        determinant, dependent = anomaly
        print(
            f"Debug: Processing anomaly {anomaly_index} with determinant {determinant} and dependent {dependent}"
        )

        determinant_key = tuple(determinant)

        # Check if a relation with this determinant already exists
        if determinant_key not in decomposed_relations:
            try:
                new_relation = Relation(
                    name=f"{relation.name}_{'_'.join(determinant)}",
                    attributes=determinant + dependent,
                )
                new_relation.add_primary_key(determinant)
                print(
                    f"Debug: Created new relation {new_relation.name} with attributes {new_relation.attributes}"
                )

                # Attempting to add foreign key - confirming if method allows
                try:
                    new_relation.add_foreign_key(determinant, relation.name)
                    print(
                        f"Debug: Foreign key {determinant} added to {new_relation.name} referencing {relation.name}"
                    )
                except TypeError as e:
                    print("Error adding foreign key:", e)

                # Store and append to relations
                decomposed_relations[determinant_key] = new_relation
                new_relations.append(new_relation)
            except Exception as e:
                print(f"Error creating relation for anomaly {anomaly_index}: {e}")

        # Populating the new relation with tuples
        for data in relation.data:
            try:
                new_tuple = {attr: data[attr] for attr in determinant + dependent}
                decomposed_relations[determinant_key].add_tuple(new_tuple)
                print(
                    f"Debug: Added tuple {new_tuple} to {decomposed_relations[determinant_key].name}"
                )
            except KeyError as e:
                print(
                    f"Error adding data tuple for {determinant_key}: Missing attribute {e}"
                )
            except Exception as e:
                print(
                    f"Unexpected error when adding data tuple for {determinant_key}: {e}"
                )

    # Handle attributes not included in the decomposed relations
    remaining_attributes = [
        attr
        for attr in relation.attributes
        if all(attr not in det[1] for det in anomalies)
    ]
    if remaining_attributes:
        try:
            final_relation = Relation(
                name=f"{relation.name}_remaining", attributes=remaining_attributes
            )
            final_relation.add_primary_key(relation.primary_key)
            final_relation.data = relation.data[:]
            print(
                f"Debug: Created remaining relation {final_relation.name} with attributes {final_relation.attributes}"
            )
            new_relations.append(final_relation)
        except Exception as e:
            print(f"Error creating remaining relation: {e}")

    print("Debug: Completed ensure_join_dependencies")
    return new_relations


# --------------------------------- Normalize Functions ---------------------------------


def normalize_1NF(relation):
    print_normalization_stage("1NF Normalization Started")
    anomalies = detect_1NF_anomalies(relation)

    # Print detected non-atomic attributes if any
    if anomalies:
        print_normalization_stage(
            f"Detected non-atomic attribute(s): {', '.join(anomalies)}"
        )
    else:
        print_normalization_stage("No non-atomic attributes found.")

    print_normalization_stage("Relations in 1NF")

    # Store original functional dependencies and data
    stored_fds = relation.functional_dependencies[:]
    stored_data = relation.data[:]
    final_1NF_relations = []

    # Fix non-atomic attributes by decomposing into new relations
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
        if not final_relation.primary_key:  # Check if no primary key is defined
            primary_key_name = f"{relation.name}_id"
            final_relation.add_primary_key([primary_key_name])  # Add primary key
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
            print_normalization_stage("No partial functional dependencies found.")
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
        stored_data = rel.data[:]

        if anomalies:
            # Call fix_transitive_functional_dependencies to handle anomalies
            new_relations = fix_transitive_functional_dependencies(rel, anomalies)

            # For each new relation, assign the stored data and add it to final_3NF_relations
            for new_relation in new_relations:
                new_relation.data = stored_data[:]
                final_3NF_relations.append(new_relation)
        else:
            final_3NF_relations.append(rel)

    print_normalization_stage("Relations in 3NF")
    for count, final_relation in enumerate(final_3NF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()

    return final_3NF_relations


def normalize_BCNF(relation):
    print_normalization_stage("BCNF Normalization Started")
    list_of_3NF_relations = normalize_3NF(relation)
    final_BCNF_relations = []

    for rel in list_of_3NF_relations:
        anomalies = detect_BCNF_anomalies(rel)
        stored_data = rel.data[:]  # Store original data for each relation

        if anomalies:
            print_normalization_stage(
                f"Detected determinants that are not superkeys: {', '.join(str(anomaly) for anomaly in anomalies)}"
            )

            # Apply the determinants_equal_superkey function to adjust FDs
            determinants_equal_superkey(rel)
            rel.data = stored_data[:]  # Assign stored data back to the relation
            final_BCNF_relations.append(rel)
        else:
            print_normalization_stage("No BCNF violations found.")
            final_BCNF_relations.append(rel)

    # Print the final relations in BCNF
    print_normalization_stage("Relations in BCNF")
    for count, final_relation in enumerate(final_BCNF_relations, start=1):
        final_relation.name = str(count)
        final_relation.print_relation()
        print_data(final_relation)  # Print data values for each BCNF relation

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
        keys = rel.primary_key  # Assuming primary_key holds the keys

        # Check if rel.data is a list of dictionaries
        if isinstance(rel.data, list) and all(isinstance(d, dict) for d in rel.data):
            # Detect 5NF anomalies
            anomalies = detect_5NF_anomalies(rel)

            stored_fds = rel.functional_dependencies[:]  # Store FDs for reference
            stored_data = rel.data[:]  # Store data for reference

            if anomalies:

                list_of_5NF_relations = ensure_join_dependencies(rel, anomalies)
                for decomposed_relation in list_of_5NF_relations:
                    # Instead of adding directly, use the new function
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
                final_5NF_relations.append(rel)

    print_normalization_stage("Relations in 5NF")
    for count, final_relation in enumerate(final_5NF_relations, start=1):
        final_relation.name = count
        final_relation.print_relation()  # Print relation details
        print_data(final_relation)  # Print data in relation

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
        pk_str = (
            pk if isinstance(pk, str) else ",".join(pk)
        )  # Convert pk to a string if not already
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

        # Check if X is a superkey by comparing against primary_key_sets
        if not any(
            set(primary_key.split(",")).issubset(set(X))
            for primary_key in primary_key_sets
        ):
            for y in Y:
                if y in non_keys:
                    # Join primary keys, X, and Y as strings for the anomaly output
                    primary_keys_str = "|".join(
                        ["|".join(pk.split(",")) for pk in primary_key_sets]
                    )
                    X_str = "|".join(X)
                    Y_str = "|".join(Y)
                    anomalies.append(f"{primary_keys_str}|{X_str}|{Y_str}")

    return anomalies


def detect_BCNF_anomalies(relation):
    anomalies = []
    # Generate sets for each composite primary key
    primary_key_sets = [
        set(pk) if isinstance(pk, list) else {pk} for pk in relation.primary_key
    ]

    for fd in relation.functional_dependencies:
        determinant_set = set(fd.get_x())  # Determinant attributes as a set

        # Check if determinant_set is a superset of any primary key subset, indicating it's a superkey
        if not any(determinant_set.issuperset(pk_set) for pk_set in primary_key_sets):
            # If no primary key subset is fully contained in determinant_set, record as anomaly
            anomalies.append(fd)

    return anomalies


def detect_4NF_anomalies(relation):
    mvds = []

    # Convert the primary key to a string and remove extraneous characters for comparison
    primary_key_attribute = str(relation.primary_key[0]).strip("[]'\" ,")

    # Find the position of the primary key attribute by iterating through relation attributes
    attribute_positions = list(
        relation.data[0].keys()
    )  # Assumes data entries are dictionaries
    primary_key_position = None

    for count, attr in enumerate(attribute_positions):
        current_attr = str(attr).strip("[]'\" ,")

        if primary_key_attribute == current_attr:
            primary_key_position = (
                current_attr  # Store attribute name directly for dictionary access
            )

            break

    # Confirm primary key position (attribute name) was found
    if primary_key_position is None:

        return []

    # Detect duplicates in primary key values
    unique_keys = set()

    for i, data in enumerate(relation.data):
        primary_key_value = str(data[primary_key_position]).strip("[]'\" ,")

        # Check for duplicates in primary key values
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

            # Update the primary key value in the data instance at the correct attribute
            data[primary_key_position] = new_value
        else:
            unique_keys.add(primary_key_value)

    for idx, data in enumerate(relation.data, start=1):
        print(f"Tuple {idx}: {data}")

    return mvds


# --------------------------------- Detect 5NF Anomaly Functions ---------------------------------


def detect_5NF_anomalies(relation):
    join_dependencies = []
    attributes = relation.attributes

    for i in range(len(attributes)):
        X = attributes[:i] + attributes[i + 1 :]
        Y = [attributes[i]]

        if check_join_dependency(relation, X, Y):
            join_dependencies.append((X, Y))

    return join_dependencies


def check_join_dependency(relation, X, Y):
    for data in relation.data:
        if all(attr in data for attr in X + Y):
            return True
    return False


def convert_data_to_dict(data, attributes):
    converted_data = []
    for row in data:
        row_dict = {}
        for attribute in attributes:
            row_dict[attribute] = str(row.get(attribute, "")).strip("[]'\" ,")
        converted_data.append(row_dict)
    return converted_data


def decompose_to_5NF(relation, join_dependencies):
    decomposed_relations = []

    for X, Y in join_dependencies:
        new_relation1 = Relation(name=f"{relation.name}_X", attributes=X)
        new_relation2 = Relation(name=f"{relation.name}_Y", attributes=Y)

        new_relation1_data = []
        new_relation2_data = []

        for data in relation.data:
            tuple_X = {attr: str(data[attr]).strip("[]'\" ,") for attr in X}
            tuple_Y = {attr: str(data[attr]).strip("[]'\" ,") for attr in Y}

            if tuple_X not in new_relation1_data:
                new_relation1_data.append(tuple_X)
            if tuple_Y not in new_relation2_data:
                new_relation2_data.append(tuple_Y)

        new_relation1.data = new_relation1_data
        new_relation2.data = new_relation2_data

        decomposed_relations.append(new_relation1)
        decomposed_relations.append(new_relation2)

    remaining_attributes = [
        attr
        for attr in relation.attributes
        if not any(attr in dep for dep in join_dependencies)
    ]

    if remaining_attributes:
        remaining_relation = Relation(
            name=f"{relation.name}_remaining", attributes=remaining_attributes
        )
        remaining_relation.data = convert_data_to_dict(
            relation.data, remaining_attributes
        )
        decomposed_relations.append(remaining_relation)

    return decomposed_relations
