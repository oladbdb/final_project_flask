from flask import redirect, url_for, flash
from functools import wraps
from flask_login import current_user

ROLE_PERMISSIONS = {
    "Admin": {
        "create_equipment",
        "edit_equipment",
        "view_equipment",
        "delete_equipment",
        "create_service",
        "view_service" 
    },
    "Technician": {
        "view_equipment",
        "create_service",
        "view_service"
    },
    "Default": {
        "view_equipment"
    }
}

def check_rights(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            role_name = current_user.role.name if current_user.is_authenticated and current_user.role else None

            allowed = permission in ROLE_PERMISSIONS.get(role_name, set())

            if not allowed:
                flash("У вас недостаточно прав для доступа к данной странице.", "warning")
                return redirect(url_for("index"))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator