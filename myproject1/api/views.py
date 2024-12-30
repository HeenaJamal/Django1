from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView                   # type: ignore
from rest_framework.views import APIView                                                          # type: ignore
from rest_framework.response import Response                                                       # type: ignore
from rest_framework import status                                                                      # type: ignore
from .models import User, FileUpload
from .serializers import UserSerializer, FileUploadSerializer
import csv
import os
from django.db import connection  
                                

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
"""

from django.contrib.auth.hashers import check_password

class LoginView(APIView):
    def post(self, request):
        mobile = request.data.get('mobile')
        password = request.data.get('password')

        user = User.objects.filter(mobile=mobile).first()
        if user and check_password(password, user.password):
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



"""class LoginView(APIView):
    def post(self, request):
        mobile = request.data.get('mobile')
        user = User.objects.filter(mobile=mobile).first()
        if user:
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
"""

# View user by ID
class UserDetailView(APIView):
    def post(self, request):
        user_id = request.data.get('id')
        if not user_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# List all users
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Update user
class UserUpdateView(APIView):
    def put(self, request):
        user_id = request.data.get('id')
        if not user_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            file_path = serializer.instance.file.path
            table_name = serializer.instance.table_name
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                with connection.cursor() as cursor:
                    # Create the table with `table_<10-digit random number>`
                    create_table_query = f"CREATE TABLE `{table_name}` ({', '.join([f'`{col}` TEXT' for col in header])})"
                    cursor.execute(create_table_query)
                    # Insert rows from CSV into the table
                    for row in reader:
                        cursor.execute(f"INSERT INTO `{table_name}` VALUES ({', '.join(['%s' for _ in row])})", row)
            return Response({"table_name": table_name}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
