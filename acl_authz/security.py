from importlib import import_module

from django.conf import settings


# Actions
Allow = 'allow'
Deny = 'deny'

# Principals
Everyone = 'acl_authz.everyone'
Authenticated = 'acl_authz.authenticated'
Staff = 'acl_authz.staff'


def root_principals(request):
    principals = set()
    principals.add(Everyone)
    if hasattr(request, 'user'):
        principals.add(request.user)
        if request.user.is_authenticated:
            principals.add(Authenticated)
        if request.user.is_staff:
            principals.add(Staff)
    return principals


def get_principals_callback():
    path = getattr(settings, 'ACL_AUTHZ_PRINCIPALS_CALLBACK', None)
    if path:
        module, func = path.rsplit('.', 1)
        return getattr(import_module(module), func)
    else:
        return root_principals


def detect_permissions(context, principals):
    if not hasattr(context, '__acl__'):
        raise TypeError("Context %s doesn't have __acl__ attribute" % context)

    permissions = set()
    acl = context.__acl__
    for action, principal, permission in acl:
        if principal in principals:
            if action is Allow:
                permissions.add(permission)
            elif action is Deny:
                permissions.remove(permission)
    return permissions


def has_permission(permission, context, request):
    callback = get_principals_callback()
    principals = callback(request)
    permissions = detect_permissions(context, principals)
    return permission in permissions
