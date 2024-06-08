from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

def group_required(*group_names):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if any(request.user.groups.filter(name=group_name).exists() for group_name in group_names):
                    return view_func(request, *args, **kwargs)
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('login')
        return _wrapped_view
    return decorator
