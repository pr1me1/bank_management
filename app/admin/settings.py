from sqladmin import Admin

from app.admin import AdminUserView, AuditLogView
from app.admin.authenticate import authentication_backend
from app.db import engine


def setup_admin(app):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Admin Panel",
    )

    admin.add_view(AdminUserView)
    admin.add_view(AuditLogView)

    return admin


__all__ = ["setup_admin"]
