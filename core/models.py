from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
# Create your models here.
User = get_user_model()

class Students(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username
    
class CoruseSchedules(models.Model):
    id = models.IntegerField(primary_key=True)
    days = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_no = models.CharField(max_length=5)

class Courses(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to='courses_images',null=True)
    tag = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=255)
    prerequisites = models.ManyToManyField('self', through='Prerequisties', symmetrical=False)
    instractor = models.CharField(max_length=30,default='')
    capacity = models.IntegerField(default=0)
    schedule_id = models.ForeignKey(CoruseSchedules,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.name

class Prerequisties(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='required_by')
    course_prerequisite = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='requires')

class studentsReg(models.Model):
    id = models.IntegerField(primary_key=True)
    student_id= models.ForeignKey(Students, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)

class Notification(models.Model):
    course_name = models.CharField(max_length=100)
    start_time = models.TimeField()
