# SQL join-based merge
from flask import jsonify
import hashlib

def merge_q_generator(data):
    """
    Generate SQL join query based on selected schemas, tables and columns.
    Input:
        data: dict, selected schemas, tables and columns. Example: {"row-1": {"data_schema": "metrics", "data_source": "source1", "table": "table_data_1", "col_lst": ["col1", "col2"]}, "row-2": {...}, ...}
    Output:
        SQL join query string
    """
    # Check if the data is empty
    if not data:
        return jsonify({"error": "No data to merge"}), 400
    
    #use first table as base table to merge others onto
    selected_schema = data["schema"]
    selected_tables = data["tables"]
    table_items = list(selected_tables.items())
    base_row, base_table_info = table_items[0]
    base_cols = base_table_info["cols"]
    base_table = f"{selected_schema}.{base_table_info['metrics'].replace('-metrics','')}_{base_table_info['table']}"
    base_alias = base_row.replace("row-", "t")
    select_clauses = [
        (
            f"""CAST({base_alias}."{col}" AS TEXT) AS "{base_table}__{col}" """
            if col == "visit_date"
            else f"""{base_alias}."{col}" AS "{base_table}__{col}" """
        )
        for col in base_cols
    ]
    join_clauses = ""
    # aliases = {base_key: base_alias}
    alias_counter = int(base_row.replace("row-", "")) + 1
    key_raw = {"schema": selected_schema, "tables": [{"metrics": base_table_info["metrics"], "table": base_table_info["table"], "cols": base_cols}]}

    for row_id, table_info in table_items[1:]:
        metrics = table_info["metrics"]
        table = table_info["table"]
        cols = table_info["cols"]
        key_raw["tables"].append({"metrics": metrics, "table": table, "cols": cols})

        table_name = f"{selected_schema}.{metrics.replace('-metrics','')}_{table}"
        alias = f"t{alias_counter}"
        alias_counter += 1

        cols = [
            col
            for col in table_info["cols"]
            if col not in ["participant_ID", "visit_date", "visit_type"]
        ]
        select_clauses += [
            (
                f"""CAST({alias}."{col}" AS TEXT) AS "{table_name}__{col}" """
                if col == "visit_date" or col == "visit_datetime"
                else f"""{alias}."{col}" AS "{table_name}__{col}" """
            )
            for col in cols
        ]

        join_clause = (
            f"""
        LEFT JOIN {table_name} {alias}
        ON {alias}."participant_ID" = {base_alias}."participant_ID"
            AND {alias}."visit_date" = {base_alias}."visit_date"
            AND COALESCE({alias}."visit_type", '') = COALESCE({base_alias}."visit_type", '')
        """
            if "visit_type" in cols
            else f"""
        LEFT JOIN {table_name} {alias}
        ON {alias}."participant_ID" = {base_alias}."participant_ID"
            AND {alias}."visit_date" = {base_alias}."visit_date"
        """
        )
        join_clauses += join_clause

    final_query = f"""SELECT {', '.join(select_clauses)} FROM {base_table} {base_alias}{join_clauses};"""
    final_key = hashlib.md5(str(key_raw).encode()).hexdigest()
    return final_key, final_query
