from rest_framework import serializers
from .models import Courses,studentsReg,CoruseSchedules,Notification
from django.contrib.auth.models import User


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

class CourseSchedulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoruseSchedules
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
    
class StudentRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = studentsReg
        fields = ['student_id', 'course_id']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class CourseAndCourseSchduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = [
            'code',
            'name',
            'image',
            'tag',
            'description',
            'prerequisites',
            'instractor',
            'capacity',
            'days',
            'start_time',
            'end_time',
            'room_no'
            ]
        