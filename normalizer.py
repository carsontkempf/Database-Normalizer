import os


class TableManager:
    def __init__(self):
        self.table_count = 0
        self.table_registry = {}

    def get_table_name(self, attributes):
        attributes_key = tuple(
            sorted(attributes)
        )  # Sort and use as a unique identifier
        if attributes_key in self.table_registry:
            return self.table_registry[attributes_key]
        else:
            self.table_count += 1
            new_table_name = f"Relation {self.table_count}"
            self.table_registry[attributes_key] = new_table_name
            return new_table_name


def normalize_database():
    table_manager = TableManager()

    # Step 1: Delete old Normalize.md file if it exists
    if os.path.exists("Normalization.md"):
        os.remove("Normalization.md")

    # Step 2: Get the table name
    table_name = input("Enter the initial table name: ")

    # Step 3: Ask if the user wants to add <table_name>id as the primary key
    add_table_id = input(
        f"Do you want to add '{table_name}id' as the primary key? (yes/[Enter to skip]): "
    ).lower()

    # Step 4: Initialize attributes, primary keys, foreign keys, and candidate keys
    attributes = []
    primary_keys = []

    if add_table_id == "yes":
        table_id = f"{table_name}id"
        attributes.append(table_id)
        primary_keys.append(table_id)

    # Step 5: Get other attributes
    other_attributes = input("Enter other attributes (comma separated): ").split(",")
    attributes.extend([attr.strip() for attr in other_attributes])

    # Step 6: Get foreign keys and candidate keys
    foreign_keys = input("Enter foreign keys (comma separated): ").split(",")
    candidate_keys = input("Enter candidate keys (comma separated): ").split(",")

    # Step 7: Process non-atomic attributes (list-type)
    nonatomic_attributes = []
    new_tables = []
    for attr in attributes[:]:
        nonatomic = input(
            f"Is the attribute '{attr.strip()}' nonatomic or of type list? (yes/[Enter to skip]): "
        ).lower()
        if nonatomic == "yes":
            nonatomic_attributes.append(attr.strip())
            # Create a new table for the list-type attribute (1NF)
            new_table_name = table_manager.get_table_name(
                [f"{table_name}id", attr.strip()]
            )
            new_table_primary_key = (
                primary_keys[0] if primary_keys else f"{table_name}id"
            )
            new_tables.append((new_table_name, new_table_primary_key, attr.strip()))

    # Step 8: Write the Initial Table to 'Normalization.md'
    with open("Normalization.md", "a") as file:
        file.write(f"# Initial Table\n\n")

        # Write the original table with all attributes
        initial_table_name = table_manager.get_table_name(attributes)
        file.write(f"## {initial_table_name}\n\n")
        file.write("### Table Structure\n\n")
        file.write(f"| " + " | ".join(attributes) + " |\n")
        file.write(
            f"| " + " | ".join(["----------------" for _ in attributes]) + " |\n"
        )

        # Nested list format for constraints
        file.write(f"\n- **Primary Keys**\n")
        for pk in primary_keys:
            file.write(f"    - {pk}\n")
        file.write(f"- **Foreign Keys**\n")
        for fk in foreign_keys:
            file.write(f"    - {fk}\n" if fk else "    - None\n")
        file.write(f"- **Candidate Keys**\n")
        for ck in candidate_keys:
            file.write(f"    - {ck}\n" if ck else "    - None\n")
        file.write(f"- **Non-atomic attributes**\n")
        for na in nonatomic_attributes:
            file.write(f"    - {na}\n" if na else "    - None\n")

        file.write("\n---\n\n")

        # Step 9: Add 1NF section and include both the original and decomposed tables
        file.write(f"# 1NF\n\n")
        file.write("Tables in 1NF:\n\n")

        # Original Table after 1NF
        attributes_1nf = [
            attr for attr in attributes if attr not in nonatomic_attributes
        ]  # Remove list-type attributes
        table_name_1nf = table_manager.get_table_name(attributes_1nf)
        file.write(f"## {table_name_1nf}\n\n")
        file.write(f"| " + " | ".join(attributes_1nf) + " |\n")
        file.write(
            f"| " + " | ".join(["----------------" for _ in attributes_1nf]) + " |\n"
        )

        # Constraints for 1NF table
        file.write(f"\n- **Primary Keys**\n")
        for pk in primary_keys:
            file.write(f"    - {pk}\n")
        file.write(f"- **Foreign Keys**\n")
        for fk in foreign_keys:
            file.write(f"    - {fk}\n" if fk else "    - None\n")
        file.write(f"- **Candidate Keys**\n")
        for ck in candidate_keys:
            file.write(f"    - {ck}\n" if ck else "    - None\n")

        file.write("\n---\n\n")

        # Step 10: Add new tables for list-type attributes in 1NF
        for new_table in new_tables:
            file.write(f"## {new_table[0]}\n\n")
            file.write(f"| Primary Key          | List Attribute       |\n")
            file.write(f"|----------------------|----------------------|\n")
            file.write(f"| {new_table[1]}       | {new_table[2]}       |\n")

            # Nested list format for new table constraints
            file.write(f"\n- **Primary Keys**\n")
            file.write(f"    - {new_table[1]}\n")
            file.write(f"- **Foreign Keys**\n")
            file.write(f"    - None\n")
            file.write(f"- **Candidate Keys**\n")
            file.write(f"    - None\n")

            file.write("\n---\n\n")

        # Step 11: Sections for 2NF, 3NF, BCNF, 4NF, and 5NF
        for nf in ["2NF", "3NF", "BCNF", "4NF", "5NF"]:
            file.write(f"# {nf}\n\n")
            file.write(f"Tables in {nf}:\n\n")
            # In this placeholder, you would handle the tables as you process them for each normal form.
            table_name_nf = table_manager.get_table_name(attributes_1nf)
            file.write(f"## {table_name_nf}\n\n")
            file.write(f"| " + " | ".join(attributes_1nf) + " |\n")
            file.write(
                f"| "
                + " | ".join(["----------------" for _ in attributes_1nf])
                + " |\n"
            )

            # Constraints for nf table
            file.write(f"\n- **Primary Keys**\n")
            for pk in primary_keys:
                file.write(f"    - {pk}\n")
            file.write(f"- **Foreign Keys**\n")
            for fk in foreign_keys:
                file.write(f"    - {fk}\n" if fk else "    - None\n")
            file.write(f"- **Candidate Keys**\n")
            for ck in candidate_keys:
                file.write(f"    - {ck}\n" if ck else "    - None\n")

            file.write("\n---\n\n")

    print(f"Results for {table_name} written to Normalization.md")


if __name__ == "__main__":
    normalize_database()
