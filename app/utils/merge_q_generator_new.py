# SQL join-based merge
import hashlib

def merge_q_generator_new(data:dict={
        "selected_project": "project1",
        "tables": [
            {
                "table_name": "table1",
                "selected_cols": ["colA", "colB", "colC"],
                "m1":"colA",
                "m2": None,
                "m3": "colC",
                "action": None
            },
            {
                "table_name": "table2",
                "selected_cols": ["colD", "colE", "colF"],
                "m1":"colD",
                "m2": None,
                "m3": None,
                "action": "BASE"
            },
            {
                "table_name": "table3",
                "selected_cols": ["colG", "colH", "colI"],
                "m1":"colG",
                "m2": None,
                "m3": "colI",
                "action": "left join"
            }
        ]
    }) -> tuple[str, str]:
    """
    # ##example data format:
    # {
    #     "selected_project": "project1",
    #     "tables": [
    #         {
    #             "table_name": "table1",
    #             "selected_cols": ["colA", "colB", "colC"],
    #             "m1":"colA",
    #             "m2": None,
    #             "m3": "colC",
    #             "action": None
    #         },
    #         {
    #             "table_name": "table2",
    #             "selected_cols": ["colD", "colE", "colF"],
    #             "m1":"colD",
    #             "m2": None,
    #             "m3": None,
    #             "action": "left join"
    #         },
    #         {
    #             "table_name": "table3",
    #             "selected_cols": ["colG", "colH", "colI"],
    #             "m1":"colG",
    #             "m2": None,
    #             "m3": "colI",
    #             "action": "left join"
    #         }
    #     ]
    # }
    ## sample sql query => select a.colA, a.colB, a.colC, b.colE, b.colF, c.colH
    ## from table1 as a
    ## left join table2 as b on a.colA = b.colD
    ## left join table3 as c on a.colA = c.colG and a.colC = c.colI
    """
    proj = data.get("selected_project")
    tables = data.get("tables", []) #list of tables selected with columns to merge 
    key_columns = data.get("key_columns", [])  #list of table_name and its key columns to merge on
    # first_table = tables[0]
    base_table_idx = [i for i, t in enumerate(tables) if t.get("action").upper()=='BASE'][0]
    # print(base_table_idx)  #find the table with action BASE
    first_table = tables[base_table_idx]
    last_table_name = first_table['table_name']
    order_col1 = f't0."{first_table["m1"]}"'
    order_col2 = f't0."{first_table["m2"]}"' if first_table['m2'] else None
    order_col3 = f't0."{first_table["m3"]}"' if first_table['m3'] else None
    last_m1 = f't0."{first_table["m1"]}"'
    last_m2 = f't0."{first_table["m2"]}"' if first_table['m2'] else None
    last_m3 = f't0."{first_table["m3"]}"' if first_table['m3'] else None
    selected_cols = [last_m1, last_m2, last_m3] + [f't0."{c}"' for c in first_table["selected_cols"] if c not in [first_table["m1"], first_table["m2"], first_table["m3"]]]
    selected_cols = [col for col in selected_cols if col is not None]  #remove None values

    join_q = f' FROM {proj}.{last_table_name} AS t0 '
    
    for idx, table in enumerate(tables, start=0):
        if idx == base_table_idx:
            continue  #skip the base table as it's already added
        print(table)
        table_name = f'{proj}.{table["table_name"]}'
        m1 = table["m1"]
        m2 = table["m2"]
        m3 = table["m3"]
        table_alias = f't{idx+1}'
        selected_cols += [f'{table_alias}."{c}"' for c in table["selected_cols"] if c not in [m1, m2, m3]]
        action = table["action"]
        if m2 and last_m2 and m3 and last_m3:
            join_q += f"""\n{action.upper()} {table_name} AS t{idx} 
            ON {last_m1} = {table_alias}."{m1}" 
            AND CAST({last_m2} AS DATE) = CAST({table_alias}."{m2}" AS DATE)
            AND {last_m3} = {table_alias}."{m3}" """
        elif m2 and last_m2:
            join_q += f"""\n{action.upper()} {table_name} AS {table_alias} 
            ON {last_m1} = {table_alias}."{m1}" 
            AND CAST({last_m2} AS DATE) = CAST({table_alias}."{m2}" AS DATE) """
        elif m3 and last_m3:
            join_q += f"""\n{action.upper()} {table_name} AS {table_alias} 
            ON {last_m1} = {table_alias}."{m1}" 
            AND {last_m3} = {table_alias}."{m3}" """
        else:
            join_q += f"""\n{action.upper()} {table_name} AS {table_alias} 
            ON {last_m1} = {table_alias}."{m1}" """
        last_table_name = table["table_name"]
        last_m1 = f'{table_alias}."{m1}"'
        last_m2 = f'{table_alias}."{m2}"' if m2 else last_m2
        last_m3 = f'{table_alias}."{m3}"' if m3 else last_m3

    print(join_q)
    print(selected_cols)

    select_q = "SELECT " + ", ".join(selected_cols)
    final_sql_query = select_q + join_q + " ORDER BY " + order_col1 + (f", {order_col2}" if order_col2 else "") + (f", {order_col3}" if order_col3 else "") + " ;"

    return hashlib.md5(final_sql_query.encode()).hexdigest(), final_sql_query