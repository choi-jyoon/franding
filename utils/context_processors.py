from mypage.models import UserAddInfo

def get_profile_image(request):
    if request.user.is_authenticated:
        try:
            user_info = UserAddInfo.objects.get(user = request.user)
            return {'profile_img': user_info.profile_img}
        except UserAddInfo.DoesNotExist:
            return {'profile_img': None}
    return {'profile_img': None}