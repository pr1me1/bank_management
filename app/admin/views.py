import logging

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional

from app.admin import AdminUser
from app.models import AuditLog

logger = logging.getLogger(__name__)


class AdminUserView(ModelView, model=AdminUser):
    column_list = [
        AdminUser.email,
        AdminUser.telegram_id,
        AdminUser.is_active,
        AdminUser.created_at
    ]

    can_export = True
    export_types = ['csv', 'xlsx']

    form_edit_rules = ["email", "telegram_id", "is_active"]

    form_create_rules = ["email", "telegram_id", "is_active", "password"]

    form_overrides = {
        "is_active": BooleanField,
    }

    form_args = {
        "email": {
            "label": "Email",
            "validators": [DataRequired(), Email()],
        },
        "telegram_id": {
            "label": "Telegram ID",
            "validators": [Optional()],
        },
        "is_active": {
            "label": "Faolmi?",
            "render_kw": {"class": "form-check-input"}
        }
    }

    form_excluded_columns = ["password_hash", "created_at", "updated_at"]

    name = "Admin User"
    icon = "fa-solid fa-user"
    name_plural = "Admin Users"

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules=rules)

        if rules and "password" in rules:
            form_class.password = PasswordField(
                "Password",
                validators=[DataRequired()],
                render_kw={
                    "placeholder": "Parol kiriting",
                    "class": "form-control"
                }
            )
        return form_class

    async def on_model_change(self, data, model, is_created, request):
        from app.utils import hash_password
        if is_created:
            if "password" in data:
                data["password_hash"] = hash_password(data.pop("password"))
                logger.info(f"✅ Yangi admin yaratildi: {data.get('email')}")
        else:
            data.pop("password", None)
            data.pop("password_hash", None)

    async def is_accessible(self, request: Request) -> bool:
        is_superuser = request.session.get("is_superuser")

        if is_superuser is True:
            return True
        return False

    async def is_visible(self, request: Request) -> bool:
        return request.session.get("is_superuser") is True


class AuditLogView(ModelView, model=AuditLog):
    column_list = [
        AuditLog.user_id,
        AuditLog.category,
        AuditLog.action,
        AuditLog.payload,
        AuditLog.user,
        AuditLog.created_at
    ]

    can_export = True
    export_types = ['csv', 'xlsx', 'json']

    page_size = 50
    page_size_options = [50, 100, 200]

    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    name = "Audit Log"
    name_plural = "Audit Logs"
    icon = "fa-solid fa-clipboard-list"


__all__ = [
    'AdminUserView',
    'AuditLogView'
]
