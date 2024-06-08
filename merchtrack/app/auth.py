from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if any(request.user.groups.filter(name=group_name).exists() for group_name in group_names):
                    return view_func(request, *args, **kwargs)
            messages.error(request, 'You are not authorized to access this page.')
            # Store the current path in the session
            next_url = request.get_full_path()
            return redirect(f'{reverse("login")}?next={next_url}')
        return _wrapped_view
    return decorator
