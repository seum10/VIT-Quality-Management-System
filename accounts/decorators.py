from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('login')

            user_role = getattr(request.user.profile, 'role', None)

            if user_role not in allowed_roles:
                messages.error(
                    request,
                    'You do not have permission to access this page.'
                )
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator