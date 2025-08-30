from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer, SocialAccountSerializer
from .models import SocialAccount

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class SocialAccountListView(generics.ListAPIView):
    serializer_class = SocialAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_social_account(request):
    """Connect a social media account to user profile"""
    provider = request.data.get('provider')
    access_token = request.data.get('access_token')
    
    if not provider or not access_token:
        return Response(
            {'error': 'Provider and access_token are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Here you would implement the logic to verify the token with the provider
    # and create/update the social account
    
    return Response({'message': 'Social account connected successfully'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def disconnect_social_account(request, provider):
    """Disconnect a social media account from user profile"""
    try:
        social_account = SocialAccount.objects.get(
            user=request.user, 
            provider=provider
        )
        social_account.delete()
        return Response({'message': 'Social account disconnected successfully'})
    except SocialAccount.DoesNotExist:
        return Response(
            {'error': 'Social account not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
