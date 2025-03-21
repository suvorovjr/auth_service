"""Create base permissions and roles

Revision ID: 036d93d8f77d
Revises: cb03c46c83a0
Create Date: 2025-03-14 18:11:48.094529

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "036d93d8f77d"
down_revision: Union[str, None] = "cb03c46c83a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()

    permissions = [
        ("can_create_role", "Может создавать роли"),
        ("can_update_role", "Может изменять роли"),
        ("can_delete_role", "Может удалять роли"),
        ("can_view_role", "Может просматривать роли"),
        ("can_create_user", "Может создавать пользователей"),
        ("can_update_user", "Может изменять пользователей"),
        ("can_delete_user", "Может удалять пользователей"),
        ("can_view_user", "Может просматривать пользователей"),
        ("can_create_perm", "Может создавать права"),
        ("can_update_perm", "Может изменять права"),
        ("can_delete_perm", "Может удалять права"),
        ("can_view_perm", "Может просматривать права"),
    ]

    for slug, desc in permissions:
        conn.execute(
            sa.text("INSERT INTO permissions (slug, description) VALUES (:slug, :desc) ON CONFLICT (slug) DO NOTHING"),
            {"slug": slug, "desc": desc},
        )

    roles = [
        ("admin", "Администратор", "Полный доступ ко всем возможностям системы"),
        ("moderator", "Модератор", "Может управлять пользователями"),
        ("user", "Пользователь", "Обычный пользователь"),
    ]

    for slug, title, desc in roles:
        conn.execute(
            sa.text(
                "INSERT INTO roles (slug, title, description) VALUES (:slug, :title, :desc) ON CONFLICT (slug) DO NOTHING"
            ),
            {"slug": slug, "title": title, "desc": desc},
        )

    role_permissions = {
        "admin": [
            "can_create_role",
            "can_update_role",
            "can_delete_role",
            "can_view_role",
            "can_create_user",
            "can_update_user",
            "can_delete_user",
            "can_view_user",
            "can_create_perm",
            "can_update_perm",
            "can_delete_perm",
            "can_view_perm",
        ],
        "moderator": ["can_create_user", "can_update_user", "can_delete_user", "can_view_user", "can_view_role"],
        "user": [],
    }

    for role, perms in role_permissions.items():
        for perm in perms:
            conn.execute(
                sa.text(
                    "INSERT INTO role_permissions (role_slug, permission_slug) VALUES (:role, :perm) ON CONFLICT DO NOTHING"
                ),
                {"role": role, "perm": perm},
            )


def downgrade():
    conn = op.get_bind()

    conn.execute(sa.text("DELETE FROM role_permissions WHERE role_slug IN ('admin', 'moderator', 'viewer', 'user')"))

    conn.execute(sa.text("DELETE FROM roles WHERE slug IN ('admin', 'moderator', 'viewer', 'user')"))

    conn.execute(sa.text("DELETE FROM permissions WHERE slug LIKE 'can_%'"))
