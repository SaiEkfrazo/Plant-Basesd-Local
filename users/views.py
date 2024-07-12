from rest_framework import viewsets
from .models import User
from .serializers import *
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
import secrets
from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

User = get_user_model()

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class UserAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @swagger_auto_schema(
        operation_summary="List all Users",
        manual_parameters=[
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Api to get list of all users or Search by first name, last name, email, or phone number'
            )
        ],
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('key', None)
        if search_query:
            queryset = self.queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        else:
            queryset = self.queryset.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results':serializer.data})
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_summary="Create a User",
        responses={201: openapi.Response(description="User created successfully")}
    )
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Ensure email is provided and not empty
        email = serializer.validated_data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Set username to email
        username = email

        try:
            user = serializer.save(username=username)
            # Generate a random password
            password_length = 12
            password = secrets.token_urlsafe(password_length)
            user.set_password(password)
            user.save()

            # Send an email
            subject = 'User Account Created'
            message = f"Hello {user.first_name}, your account has been created. Your password is: {password}"
            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, [user.email])

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'message': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_INTEGER, format=openapi.FORMAT_INT64),
                # 'designation': openapi.Schema(type=openapi.TYPE_INTEGER, format=openapi.FORMAT_INT64),
                # 'organization': openapi.Schema(type=openapi.TYPE_INTEGER, format=openapi.FORMAT_INT64),
            },
            required=['first_name', 'last_name', 'email']
        ),
        operation_summary="Update User Details",
        responses={
            200: openapi.Response(
                description="User details updated successfully",
                examples={
                    "application/json": {
                        "message": "User details updated successfully"
                    }
                }
            )
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update the user instance
        validated_data = serializer.validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # If password is provided, update it separately
        if 'password' in request.data:
            instance.set_password(request.data['password'])
        instance.save()

        return Response({'message':'User Details Updated Successfully'})
    
@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Login with email or phone number and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Logged In Successfully",
                        "refresh_token": "your_refresh_token",
                        "access_token": "your_access_token"
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid Credentials",
                examples={
                    "application/json": {
                        "error": "Invalid Credentials"
                    }
                }
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email_or_phone = serializer.validated_data.get('email_or_phone')
        # print('emal or phone',email_or_phone)
        password = serializer.validated_data['password']
        
        try:
            # Identify if the input is an email or phone number
            if '@' in email_or_phone:
                user = User.objects.get(email=email_or_phone)
            else:
                user = User.objects.get(phone_number=email_or_phone)
            
            if not user.check_password(password):
                return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Logged In Successfully',
                'user_id':user.id,
                'first_name':user.first_name,
                'last_name':user.last_name,
                # 'user_designation': user.designation.designation_name if user.designation else None,
                'user_name': user.username if user.username else user.first_name + user.last_name,
                'is_superuser': user.is_superuser,
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),

            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout by blacklisting the refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist')
            },
        ),
        responses={
            205: openapi.Response(
                description="Successfully logged out",
                examples={
                    "application/json": {
                        "message": "Successfully logged out"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Error message"
                    }
                }
            ),
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# {
#   "name": "Leakages above 5 mm",
#   "color_code": "#c44a41",
#   "plant": 4
# }