# SQL join-based merge
from flask import jsonify
import pandas as pd

def merge_q_generator(data, db):
    # Check if the data is empty
    if not data:
        return jsonify({"error": "No data to merge"}), 400

    # Generate SQL join query
    # Assuming data is a dictionary with keys as table names and values as lists of columns
    # Example: {'table_data_1': ['col1', 'col2'], 'table_data_2': ['col3', 'col4']}
    # Identify base table (first in selection)
    table_items = list(data.items())
    base_key, base_cols = table_items[0]
    base_table = base_key.replace("table_data_", "").replace('-metrics-','_').lower()
    base_alias = "t0"
    select_clauses = [f"""{base_alias}."{col}" AS {base_table}__{col}""" for col in base_cols]
    join_clauses = ""
    aliases = {base_key: base_alias}
    alias_counter = 1

    for key, cols in table_items[1:]:
        table = key.replace("table_data_", "").replace('-metrics-','_').lower()
        alias = f"t{alias_counter}"
        aliases[key] = alias
        alias_counter += 1

        select_clauses += [f"""{alias}."{col}" AS {table}__{col}""" for col in cols if col not in ['participant_ID', 'visit_date', 'visit_type']]

        join_clause = f"""
        LEFT JOIN metrics.{table} {alias}
        ON {alias}."participant_ID" = {base_alias}."participant_ID"
            AND {alias}."visit_date" = {base_alias}."visit_date"
            AND COALESCE({alias}."visit_type", '') = COALESCE({base_alias}."visit_type", '')
        """ if "visit_type" in cols else f"""
        LEFT JOIN metrics.{table} {alias}
        ON {alias}."participant_ID" = {base_alias}."participant_ID"
            AND {alias}."visit_date" = {base_alias}."visit_date"
        """
        join_clauses += join_clause

    final_query = f"""
    SELECT {', '.join(select_clauses)}
    FROM metrics.{base_table} {base_alias}
    {join_clauses}
    """
    return final_query
    