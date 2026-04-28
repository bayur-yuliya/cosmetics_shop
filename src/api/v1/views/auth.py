from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from api.utils.custom_authentication import CsrfExemptSessionAuthentication
from api.v1.serializers.auth import RegisterSerializer


class LoginView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )

        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return Response({"status": "User login successfully"})


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return Response(
            {"user_id": user.id, "status": "User created successfully"},
            status=status.HTTP_201_CREATED,
        )
