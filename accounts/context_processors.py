from accounts.models import UserProfile

def profile_context(request):
    context = {}
    if request.user.is_authenticated:
        profile_id = request.session.get('active_profile_id')
        if profile_id:
            try:
                context['active_profile'] = UserProfile.objects.get(id=profile_id, user=request.user)
            except UserProfile.DoesNotExist:
                pass
    return context
