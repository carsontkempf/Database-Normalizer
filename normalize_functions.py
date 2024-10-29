from classes import *
from helper_functions import *


def print_divider():
    print("\n-------------------------\n")


def print_normalization_stage(stage_name):
    print_divider()
    print(f"Starting {stage_name}")
    print_divider()


# Define the print_data function to display data neatly under attribute headers with dictionary access
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


def fix_partial_functional_dependencies(parent_relation, decomposed_relation):
    adjusted_fds = []

    for fd in parent_relation.functional_dependencies:
        fd_x = set(fd.get_x())
        fd_y = set(fd.get_y())
        primary_key_set = set(parent_relation.primary_key)

        # Check if the X attributes (determinants) are in the decomposed relation
        if fd_x.issubset(decomposed_relation.attributes):
            # Ensure all Y attributes (dependents) are added to the decomposed relation
            for y_attr in fd_y:
                if y_attr not in decomposed_relation.attributes:
                    decomposed_relation.attributes.append(y_attr)

            # Check if the FD is a partial dependency
            if fd_x.issubset(primary_key_set) and fd_x != primary_key_set:
                print(f"Partial dependency detected: {fd_x} -> {fd_y}")

                # Create a new FD with adjusted primary key if partial dependency
                adjusted_fd = FunctionalDependency(list(primary_key_set), list(fd_y))
                adjusted_fds.append(adjusted_fd)
            else:
                # Append the original FD as it is if no adjustment is needed
                adjusted_fds.append(fd)

    return adjusted_fds


def fix_transitive_functional_dependencies(relation):
    primary_key = set(relation.primary_key)
    transitive_dependents = set()
    new_fds = []
    direct_dependencies = (
        set()
    )  # Track intermediaries with direct dependencies on the primary key

    # Step 1: Identify direct dependencies and potential intermediaries
    for fd in relation.functional_dependencies:
        fd_x = set(fd.get_x())  # Determinant
        fd_y = set(fd.get_y())  # Dependents

        # If fd_x exactly matches the primary key, it's a direct dependency
        if fd_x == primary_key:
            new_fds.append(fd)
            # Record each dependent as directly dependent on the primary key
            direct_dependencies.update(fd_y)
        else:
            # If fd_x is a direct dependent of the primary key, add fd_y as intermediaries
            if fd_x.issubset(direct_dependencies):
                print(f"Transitive dependency detected: {fd_x} -> {fd_y}")
                transitive_dependents.update(fd_y)

    # Step 2: Replace transitive dependencies with primary_key -> transitive_dependents
    if transitive_dependents:
        consolidated_fd = FunctionalDependency(
            list(primary_key), list(transitive_dependents)
        )
        new_fds.append(consolidated_fd)

    return new_fds


def exclude_duplicate_relations(decomposed_relation, decomposed_relation_list):
    new_attrs = set(decomposed_relation.attributes)
    to_remove = []

    for existing_relation in decomposed_relation_list:
        existing_attrs = set(existing_relation.attributes)

        if new_attrs == existing_attrs:
            print(
                f"Skipping exact duplicate relation: {decomposed_relation.attributes}"
            )
            return decomposed_relation_list  # Skip adding duplicate
        elif existing_attrs.issubset(new_attrs):
            print(
                f"Removing subset relation: {existing_relation.attributes} in favor of {decomposed_relation.attributes}"
            )
            to_remove.append(existing_relation)  # Mark subset for removal
        elif new_attrs.issubset(existing_attrs):
            print(
                f"Skipping subset relation: {decomposed_relation.attributes} since {existing_relation.attributes} already exists"
            )
            return decomposed_relation_list  # Skip adding subset

    # Remove marked subset relations
    for relation in to_remove:
        decomposed_relation_list.remove(relation)

    # Add the new relation after checking duplicates
    decomposed_relation_list.append(decomposed_relation)
    print(f"Adding new relation: {decomposed_relation.attributes}")

    return decomposed_relation_list


# Input: relation object, a list of anomalies
# anomaly_list = ['abc', 'def|ghi', 'jkl']
# Output: list of relation objects
# Main decomposition function for detected anomalies
def decompose_relation(parent_relation, anomaly_list, normalization_stage, stored_fds):
    if not anomaly_list:
        return []

    decomposed_relation_list = []
    count = 1
    all_parent_attributes = parent_relation.attributes[:]

    print("\nStarting decomposition for anomalies...\n")

    for anomaly in anomaly_list:
        decomposed_relation = Relation(name=str(count), attributes=[])
        decomposed_relation.name = count
        count += 1  # Increment count for unique naming

        # Process anomalies to create new relations
        if "|" not in anomaly:
            if anomaly in all_parent_attributes:
                all_parent_attributes.remove(anomaly)
            decomposed_relation.attributes.append(anomaly)
        else:
            attributes = anomaly.split("|")
            for attr in attributes:
                if attr in all_parent_attributes:
                    all_parent_attributes.remove(attr)
                decomposed_relation.attributes.append(attr)

        # Ensure primary key is included in the decomposed relation
        for pk in parent_relation.primary_key:
            if pk not in decomposed_relation.attributes:
                decomposed_relation.attributes.append(pk)
        decomposed_relation.primary_key = parent_relation.primary_key[
            :
        ]  # Set primary key explicitly

        # Assign stored functional dependencies before filtering
        decomposed_relation.functional_dependencies = [fd for fd in stored_fds]

        # Apply specific normalization stage logic to filter functional dependencies
        if normalization_stage == "1":
            decomposed_relation.functional_dependencies = [
                fd
                for fd in decomposed_relation.functional_dependencies
                if set(fd.get_x()).issubset(decomposed_relation.attributes)
                and set(fd.get_y()).issubset(decomposed_relation.attributes)
            ]
        elif normalization_stage == "2":
            decomposed_relation.functional_dependencies = [
                fd
                for fd in fix_partial_functional_dependencies(
                    parent_relation, decomposed_relation
                )
                if set(fd.get_x()).issubset(decomposed_relation.attributes)
                and set(fd.get_y()).issubset(decomposed_relation.attributes)
            ]
        elif normalization_stage == "3":
            decomposed_relation.functional_dependencies = (
                fix_transitive_functional_dependencies(decomposed_relation)
            )
        elif normalization_stage == "B":
            # BCNF: Remove any dependencies where the determinant is not a superkey
            decomposed_relation.functional_dependencies = [
                fd
                for fd in decomposed_relation.functional_dependencies
                if set(fd.get_x()).issuperset(
                    set(decomposed_relation.primary_key).union(
                        *decomposed_relation.candidate_keys
                    )
                )
            ]
        elif normalization_stage == "4":
            decomposed_relation.functional_dependencies = [
                fd
                for fd in detect_4NF_anomalies(parent_relation, decomposed_relation)
                if set(fd.get_x()).issubset(decomposed_relation.attributes)
                and set(fd.get_y()).issubset(decomposed_relation.attributes)
            ]

        # Add the decomposed relation to the list, ensuring no duplicates
        decomposed_relation_list = exclude_duplicate_relations(
            decomposed_relation, decomposed_relation_list
        )

    # Handle remaining attributes as a final relation if not empty
    if all_parent_attributes:
        remaining_relation = Relation(name=str(count), attributes=all_parent_attributes)
        remaining_relation.name = count

        # Ensure primary key is included in the decomposed relation
        for pk in parent_relation.primary_key:
            if pk not in remaining_relation.attributes:
                remaining_relation.attributes.append(pk)
        remaining_relation.primary_key = parent_relation.primary_key[
            :
        ]  # Set primary key explicitly

        remaining_relation.primary_key = parent_relation.primary_key[:]
        remaining_relation.foreign_keys = parent_relation.foreign_keys[:]
        remaining_relation.candidate_keys = parent_relation.candidate_keys[:]

        # Assign functional dependencies relevant to remaining attributes
        remaining_relation.functional_dependencies = [fd for fd in stored_fds]

        if normalization_stage == "1":
            remaining_relation.functional_dependencies = [
                fd
                for fd in remaining_relation.functional_dependencies
                if set(fd.get_x()).issubset(remaining_relation.attributes)
                and set(fd.get_y()).issubset(remaining_relation.attributes)
            ]
        elif normalization_stage == "2":
            remaining_relation.functional_dependencies = [
                fd
                for fd in fix_partial_functional_dependencies(
                    parent_relation, remaining_relation
                )
                if set(fd.get_x()).issubset(remaining_relation.attributes)
                and set(fd.get_y()).issubset(remaining_relation.attributes)
            ]
        elif normalization_stage == "3":
            remaining_relation.functional_dependencies = (
                fix_transitive_functional_dependencies(remaining_relation)
            )

        elif normalization_stage == "B":
            # BCNF: Remove any dependencies where the determinant is not a superkey
            remaining_relation.functional_dependencies = [
                fd
                for fd in remaining_relation.functional_dependencies
                if set(fd.get_x()).issuperset(
                    set(remaining_relation.primary_key).union(
                        *remaining_relation.candidate_keys
                    )
                )
            ]
        elif normalization_stage == "4":
            decomposed_relation.functional_dependencies = [
                fd
                for fd in detect_4NF_anomalies(parent_relation)
                if set(fd.get_x()).issubset(decomposed_relation.attributes)
                and set(fd.get_y()).issubset(decomposed_relation.attributes)
            ]

        decomposed_relation_list = exclude_duplicate_relations(
            remaining_relation, decomposed_relation_list
        )

    return decomposed_relation_list


def normalize_1NF(relation):
    print_normalization_stage("1NF Normalization")
    anomalies = detect_1NF_anomalies(relation)

    print_normalization_stage("Final 1NF Relations")

    stored_fds = relation.functional_dependencies[:]
    if anomalies:
        list_of_1NF_relations = decompose_relation(relation, anomalies, "1", stored_fds)
        for decomposed_relation in list_of_1NF_relations:
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
        stored_fds = rel.functional_dependencies[:]
        if anomalies:
            list_of_2NF_relations = decompose_relation(rel, anomalies, "2", stored_fds)
            final_2NF_relations.extend(list_of_2NF_relations)
        else:
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
        stored_fds = rel.functional_dependencies[:]

        if anomalies:
            list_of_3NF_relations = decompose_relation(rel, anomalies, "3", stored_fds)

            for decomposed_relation in list_of_3NF_relations:
                decomposed_relation.functional_dependencies = (
                    fix_transitive_functional_dependencies(decomposed_relation)
                )
                decomposed_relation.name = relation_counter
                final_3NF_relations.append(decomposed_relation)
                relation_counter += 1
        else:
            # Ensure transitive dependencies are fixed in the final 3NF relation
            rel.functional_dependencies = fix_transitive_functional_dependencies(rel)
            rel.name = relation_counter
            final_3NF_relations.append(rel)
            relation_counter += 1

    print_normalization_stage("Final 3NF Relations")
    for final_relation in final_3NF_relations:
        final_relation.print_relation()

    return final_3NF_relations


def normalize_BCNF(relation):
    # Start BCNF normalization process
    print_normalization_stage("BCNF Normalization")

    # Step 1: Normalize up to 3NF to start with relations in 3NF
    relations = normalize_3NF(relation)

    # Initialize empty list for final BCNF relations
    final_BCNF_relations = []
    relation_counter = 1

    # Iterate through each relation obtained from 3NF normalization
    for rel in relations:
        # Detect anomalies specific to BCNF
        anomalies = detect_BCNF_anomalies(
            rel
        )  # Find violations where determinants are not superkeys

        # Store current functional dependencies
        stored_fds = rel.functional_dependencies[:]

        # Step 2: If anomalies found (not in BCNF), decompose the relation
        if anomalies:
            # Decompose relation for each detected anomaly
            list_of_BCNF_relations = decompose_relation(rel, anomalies, "B", stored_fds)

            # Assign unique names to each new relation and add to final BCNF list
            for decomposed_relation in list_of_BCNF_relations:
                decomposed_relation.name = relation_counter
                final_BCNF_relations.append(decomposed_relation)
                relation_counter += 1
        else:
            # If no anomalies, keep the relation as it is
            rel.name = relation_counter
            final_BCNF_relations.append(rel)
            relation_counter += 1

    # Display final BCNF relations after decomposition
    print_normalization_stage("Final BCNF Relations")
    for final_relation in final_BCNF_relations:
        final_relation.print_relation()

    return final_BCNF_relations


# Modify normalize_4NF to print data only for 4NF relations
def normalize_4NF(relation):
    print_normalization_stage("4NF Normalization")
    bcnf_relations = normalize_BCNF(relation)
    final_4NF_relations = []

    for bcnf_relation in bcnf_relations:
        mvds = detect_4NF_anomalies(bcnf_relation)

        if mvds:
            decomposed_relations_4NF = decompose_to_4NF(bcnf_relation, mvds)
            final_4NF_relations.extend(decomposed_relations_4NF)
        else:
            final_4NF_relations.append(bcnf_relation)

    print_normalization_stage("Final 4NF Relations")
    for final_relation in final_4NF_relations:
        final_relation.print_relation()
        print_data(final_relation)  # Print data for each 4NF relation

    return final_4NF_relations


# Modify normalize_5NF to print data only for 5NF relations
def normalize_5NF(relation):
    print_normalization_stage("5NF Normalization")
    relations = normalize_4NF(relation)
    final_5NF_relations = []
    relation_counter = 1

    for rel in relations:
        anomalies = detect_5NF_anomalies(rel)
        stored_fds = rel.functional_dependencies[:]
        if anomalies:
            list_of_5NF_relations = decompose_relation(rel, anomalies, "5", stored_fds)
            final_5NF_relations.extend(list_of_5NF_relations)
        else:
            final_5NF_relations.append(rel)

    print_normalization_stage("Final 5NF Relations")
    for final_relation in final_5NF_relations:
        final_relation.print_relation()
        print_data(final_relation)  # Print data for each 5NF relation

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
    primary_key = relation.primary_key[:]
    all_keys = primary_key[:]
    for key in relation.candidate_keys + relation.foreign_keys:
        all_keys.extend(key)

    non_keys = [attr for attr in relation.attributes if attr not in all_keys]
    for fd in relation.functional_dependencies:
        X, Y = fd.get_x(), fd.get_y()
        if set(X).issubset(all_keys) and set(X) != set(primary_key):
            non_key_Y = [y for y in Y if y in non_keys]
            if non_key_Y:
                anomalies.append("|".join(non_key_Y))
    return anomalies


def detect_3NF_anomalies(relation):
    anomalies = []
    primary_key = relation.primary_key[:]
    all_keys = primary_key[:] + relation.candidate_keys + relation.foreign_keys

    # Identify non-key attributes
    non_keys = [attr for attr in relation.attributes if attr not in all_keys]

    for fd in relation.functional_dependencies:
        X = fd.get_x()  # Determinant (left side of FD)
        Y = fd.get_y()  # Dependent attributes (right side of FD)

        # Check if X is not a superkey (does not fully determine the primary key)
        if not set(primary_key).issubset(set(X)):
            for y in Y:
                # Check for transitive dependency if y is a non-key and depends on another non-key attribute
                if y in non_keys:
                    # Create anomaly with primary key and transitive attributes
                    transitive_anomaly = primary_key + X + Y
                    transitive_anomaly_str = "|".join(transitive_anomaly)

                    # Add to anomalies in format "A|B|C"
                    if transitive_anomaly_str not in anomalies:
                        anomalies.append(transitive_anomaly_str)

    return anomalies


def detect_BCNF_anomalies(relation):
    anomalies = []  # Initialize an empty list to store BCNF anomalies

    # Get all attributes involved in the primary key and candidate keys
    primary_key = set(relation.primary_key)
    all_superkeys = primary_key.union(*relation.candidate_keys)

    # Loop through each functional dependency to check if the determinant is a superkey
    for fd in relation.functional_dependencies:
        fd_x = set(fd.get_x())  # Left side of FD (determinant)

        # Check if fd_x is not a superkey (does not fully determine all attributes in the relation)
        if not fd_x.issuperset(all_superkeys):
            # If the FD's determinant isn't a superkey, it's a BCNF violation
            anomalies.append(fd)  # Add violating FD to anomalies list

    return anomalies


# Rename detect_MVDs to detect_4NF_anomalies
def detect_4NF_anomalies(relation):
    mvds = []
    # Loop through each attribute in the relation
    for attribute in relation.attributes:
        # Check if the attribute has independent multi-valued dependencies
        if has_independent_values(
            attribute, relation
        ):  # Custom function to verify independence
            mvds.append(attribute)
    return mvds


def has_independent_values(attribute, relation):
    # Logic to verify if the attribute has independent values from other attributes in the relation
    independent_values = set()
    if attribute not in relation.attributes:
        return False

    try:
        for row in relation.data:
            independent_values.add(row[relation.attributes.index(attribute)])
    except KeyError:
        return False

    # If the attribute has multiple independent values across rows, it's likely part of an MVD
    return len(independent_values) > 1


# Rename detect_MVDs to detect_4NF_anomalies
def detect_4NF_anomalies(relation):
    mvds = []
    # Loop through each attribute in the relation
    for attribute in relation.attributes:
        # Check if the attribute has independent multi-valued dependencies
        if has_independent_values(
            attribute, relation
        ):  # Custom function to verify independence
            mvds.append(attribute)
    return mvds
