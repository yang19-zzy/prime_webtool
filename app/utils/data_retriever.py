# utils/schema_manager.py
from collections import defaultdict
from app.models import *

# functions for profile management
def get_schemas_for_user(user_id):
    '''
    Get schemas for a specific user
    '''
    # Logic to retrieve schemas for a specific user
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return []
    is_in_lab = user.in_lab_user or user.role == 'admin' or user.role == 'dev'

    schemas = object
    if is_in_lab:
        # If the user is a lab user, return all schemas
        schemas = UserSchemaAccess.query.all()
    else:
        schemas = UserSchemaAccess.query.filter_by(limited_access=True).all()

    return [i.schema_name for i in schemas]

def get_schema_access_info(user_id):

    schemas = UserGroups.query.add_columns(
        UserGroups.group_id, UserGroups.user_id
    ).join(
        GroupProjectAccess, UserGroups.group_id == GroupProjectAccess.group_id, full=True
    ).add_columns(
        GroupProjectAccess.project_name, GroupProjectAccess.has_access
    ).filter(UserGroups.user_id == user_id, GroupProjectAccess.has_access == True).all()

    return [i.project_name for i in schemas]

def get_profile_for_user(user_id):
    '''
    Get a user profile
    '''
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return {
            "user_id": user.user_id,
            "email": user.email,
            "firstname": user.first_name,
            "lastname": user.last_name,
            "role": user.role
        }
    return None

def get_all_users():
    '''
    Get all users' roles for admin to manage
    '''
    users = User.query.add_columns(
        User.row_id, User.user_id, 
        User.first_name, User.last_name, User.email, 
        User.role, User.in_lab_user
    ).join(
            UserGroups, User.user_id == UserGroups.user_id, full=True
    ).add_columns(
        UserGroups.group_id
    ).order_by(User.last_name, User.first_name).all()
    # Convert to objects with attributes for compatibility with the return statement
    class UserObj:
        def __init__(self, user_id, first_name, last_name, email, role, in_lab_user, group_id):
            self.user_id = user_id
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.role = role
            self.in_lab_user = in_lab_user
            self.group_id = group_id

    users = [UserObj(user.user_id, user.first_name, user.last_name, user.email, user.role, user.in_lab_user, user.group_id) for user in users]
    return [{
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role if user.role else 'app_user',
        "in_lab_user": user.in_lab_user if user.in_lab_user is not None else False,
        "group_id": user.group_id
    } for user in users]


# functions for static data retrieval
def get_table_options(user_id):
    '''
    Get table options for data-viewer
    '''
    user_schemas = get_schemas_for_user(user_id)
    # Logic to retrieve table options
    options = ViewerOptions.query.filter(ViewerOptions.data_schema.in_(user_schemas)).order_by(
        ViewerOptions.row_id, ViewerOptions.data_source, ViewerOptions.table_name
    ).all()
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for opt in options:
        grouped[opt.data_schema][opt.data_source][opt.table_name].append(opt.column_name)
    return grouped


def get_column_options(user_id):
    '''
    Get column options for data-viewer
    '''
    user_schemas = get_schema_access_info(user_id)
    # Logic to retrieve column options
    options = ColumnOptions.query.filter(ColumnOptions.project.in_(user_schemas)).order_by(
        ColumnOptions.row_id, ColumnOptions.project, ColumnOptions.table_name, ColumnOptions.column_name
    ).all()
    grouped = defaultdict(lambda: defaultdict(list))
    for opt in options:
        grouped[opt.project][opt.table_name].append(opt.column_name)
    return grouped


def get_tracker_options(user_id):
    options = FormOptions.query.filter_by(active=True).order_by(
        FormOptions.field_name, FormOptions.item_num
    ).all()
    grouped = defaultdict(lambda: defaultdict(list))
    for opt in options:
        grouped[opt.field_name][opt.value].append(opt.item_num)
    return grouped


def get_unvalidated_forms(user_id):
    forms = TrackerForm.query.filter_by(validated=False).order_by(TrackerForm.id).all()
    data = [
        {
            "form_id": f.id,
            "data": {
                "form_owner": f.form_owner,
                "subject_id": f.subject_id,
                "form_data": f.form_data,
                "form_validator": f.form_validator,
                "validated": f.validated,
            },
        }
        for f in forms
    ]
    return data


def get_tables_description(proj):
    table_desc = TableDescription.query.filter_by(project=proj).order_by(TableDescription.table_name).all()
    data = [
        {
            "table_name": t.table_name,
            "table_type": t.table_type,
            "key_columns": t.unique_keys,
            "description": t.table_desc_short,
        }
        for t in table_desc
    ]
    return data


def get_group_project_access():
    rows = GroupProjectAccess.query.all()
    groups = {}
    for row in rows:
        if row.group_id not in groups:
            groups[row.group_id] = {
                "group_abbr": row.group_abbr,
                "group_desc": row.group_desc,
                "projects": {row.project_name: row.has_access}
            }
        groups[row.group_id]["projects"][row.project_name] = row.has_access
    projects = ProjectSchemaList.query.all()
    projects = [p.project_name for p in projects]
    return groups, projects


def get_user_groups(user_id):
    rows = UserGroups.query.all()
    groups = [row.group_id for row in rows]
    return groups