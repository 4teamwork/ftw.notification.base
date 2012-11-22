from AccessControl.Permission import Permission
from AccessControl.interfaces import IRoleManager


class NotificationUtils(object):

    def __init__(self, context):
        self.context = context

    def roles_of_permission(self, permission):
        """Return all roles wich have the given permission
        on the current context."""

        role_manager = IRoleManager(self.context)
        for p in role_manager.ac_inherited_permissions(1):
            name, value = p[:2]
            if name == permission:
                p = Permission(name, value, role_manager)
                roles = p.getRoles()
                return roles

    def has_anonymous_role(self):
        allowed_roles_to_view = self.roles_of_permission('View')
        return bool('Anonymous' in allowed_roles_to_view)

    def has_authenticaded_role(self):
        allowed_roles_to_view = self.roles_of_permission('View')
        return bool('Authenticated' in allowed_roles_to_view)
