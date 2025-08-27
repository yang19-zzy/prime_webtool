# utils/schema_manager.py
from app.models import User, UserRole, SchemaAccess

def get_schemas_for_user(user_id):
    '''
    Get schemas for a specific user
    '''
    # Logic to retrieve schemas for a specific user
    user = UserRole.query.filter_by(user_id=user_id).first()
    if not user:
        return []
    is_in_lab = user.role == 'in-lab-user' or user.role == 'admin' or user.role == 'dev'

    schemas = object
    if is_in_lab:
        # If the user is a lab user, return all schemas
        schemas = SchemaAccess.query.all()
    else:
        schemas = SchemaAccess.query.filter_by(limit_access=True).all()

    return [i.schema_name for i in schemas]

def get_profile_for_user(user_id):
    '''
    Get a user profile
    '''
    user = User.query.filter_by(user_id=user_id).first()
    user_role = UserRole.query.filter_by(user_id=user_id).first()
    if user and user_role:
        user.role = user_role.role
    else:
        user.role = None
    return {
        "user_id": user.user_id,
        "email": user.email,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "role": user.role
    }

def get_all_users():
    '''
    Get all users' roles for admin to manage
    '''
    users = UserRole.query.join(User, User.user_id == UserRole.user_id, full=True).add_columns(
        UserRole.user_id, User.first_name, User.last_name, UserRole.role, UserRole.in_lab_user
    ).order_by(UserRole.id).all()
    # Convert to objects with attributes for compatibility with the return statement
    class UserObj:
        def __init__(self, user_id, first_name, last_name, role, in_lab_user):
            self.user_id = user_id
            self.first_name = first_name
            self.last_name = last_name
            self.role = role
            self.in_lab_user = in_lab_user

    users = [UserObj(user_id, first_name, last_name, role, in_lab_user) for _, user_id, first_name, last_name, role, in_lab_user in users]
    return [{
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "in_lab_user": user.in_lab_user
    } for user in users]