from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'cabinet/profile/profile_settings.html')


# class CoachDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id):
#         trainer = get_object_or_404(User, id=user_id)
#         return render(request, 'cabinet/coaches/coach_detail.html', {'coach': trainer})