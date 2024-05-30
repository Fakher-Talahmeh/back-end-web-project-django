from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsSuperUser
from core.serializers import LoginSerializer, StudentRegSerializer, StudentSerializer,CourseSerializer,CourseSchedulesSerializer,NotificationSerializer
from .models import CoruseSchedules, Courses,Students,studentsReg
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
import random, time
from datetime import datetime, timedelta, date
# from django.core.mail import send_mail
response_data=''
class Register(APIView):
    def post(self, request):
        """Create a new Student"""
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password']
            )
            user.save()
            refresh = RefreshToken.for_user(user)
            global access_token
            access_token = str(refresh.access_token)
            new_profile = Students.objects.create(user = user)
            new_profile.save()
            response_data = {
                'access_token': access_token,
                'user': serializer.data,
                'admin': False
            }
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)
class Login(APIView):
    def post(self,request):
        """sign in a student"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(username=username, password=password)
            if user != None:
                refresh = RefreshToken.for_user(user)
                global response_data
                access_token = str(refresh.access_token)
                admin = True
                if request.user.is_superuser is None :
                    admin = False
                response_data = {
                        'access_token': access_token,
                        'user': serializer.data,
                        'admin': admin
                }
                return Response(response_data, status=200)
            else:
                return Response({'detail': 'Invalid credentials'}, status=401)
        else:
            return Response(serializer.errors, status=400)
class Logout(APIView):
    def post(self, request):
        """Sign out a student"""
        global response_data
        token = response_data
        if token:
            response_data = {}
            return Response({'detail': 'Successfully logged out.'}, status=205)
        else:
            return Response({'detail': 'Refresh token is required.'}, status=400)
class CourseVIEW(APIView):
    def post(self, request):
        global response_data
        if isinstance(response_data, dict) and response_data.get('admin'):
            data = request.data.get('courseData', {})
            image= request.FILES.get('image')
            course_data = data.get('course', {})
            course_data['image'] = image
            schedule_data = data.get('schedule', {})
            
            print("Received Data:", request.data)
            print("Course Data:", course_data)
            print("Schedule Data:", schedule_data)
            
            # Save schedule first
            schedule_serializer = CourseSchedulesSerializer(data=schedule_data)
            if schedule_serializer.is_valid():
                schedule = schedule_serializer.save()
            else:
                print("Schedule Serializer Errors:", schedule_serializer.errors)  # Debug print
                return Response(schedule_serializer.errors, status=400)
            
            # Save course with schedule_id

            course_data['schedule_id'] = schedule.id
            print(course_data['image'])
            course_serializer = CourseSerializer(data=course_data)
            if course_serializer.is_valid():
                course_serializer.save()
                return Response(course_serializer.data, status=201)
            else:
                print("Course Serializer Errors:", course_serializer.errors)  # Debug print
                return Response(course_serializer.errors, status=400)
        
        return Response({"message": "The user is not authorized."}, status=403)

    def get(self, request):
        """Returns All Courses"""
        global response_data
        if response_data:
            courses = Courses.objects.all()
            serializer = CourseSerializer(courses, many=True)
            ser=random.sample(serializer.data,20 if len(serializer.data) > 20 else len(serializer.data))
            response = []
            for s in range(len(ser)):
                c =CoruseSchedules.objects.get(id=ser[s]['schedule_id'])
                sc = CourseSchedulesSerializer(c,many=False)
                ser[s]['schedule_id'] = sc.data
                response.append(ser[s])
            return Response(response,status=200)
        else:
            return Response({"message": "The user is not authenticated."})
    def put(self, request, pk):
        """return one Course"""
        global response_data
        if response_data:
            course = Courses.objects.filter(code=pk).first()
            serializer = CourseSerializer(course)
            courses_connect_tag = random.sample(CourseSerializer(Courses.objects.filter(tag=course.tag),many=True).data,3 if len(Courses.objects.filter(tag=course.tag)) >3 else len(Courses.objects.filter(tag=course.tag)))
            for c in range(len(courses_connect_tag)):
                if courses_connect_tag[c]['code'] == serializer.data['code']:
                    courses_connect_tag.remove(courses_connect_tag[c])
                    break
            c =CoruseSchedules.objects.get(id=serializer.data['schedule_id'])
            sc = CourseSchedulesSerializer(c,many=False)
            response = serializer.data
            response['schedule_id'] = sc.data
            for pre in range(len(response['prerequisites'])):
                response['prerequisites'][pre] = CourseSerializer(Courses.objects.get(code=response['prerequisites'][pre]),many=False).data
            r = True if studentsReg.objects.filter(course_id=course.code,student_id=Students.objects.filter(user=User.objects.filter(username=response_data['user']['username']).first()).first()).first() != None else False
            length = len(studentsReg.objects.filter(course_id=pk))
            res = {'course':response,'registered':r,'courses_connect_tag':courses_connect_tag,'student_length':length}
            return Response(res)
        else:
            return Response({"message": "The user is not authenticated."})

class UpdateVIEW(APIView):
    def get(self,request,pk):
        global response_data
        if response_data:
            course = Courses.objects.filter(code=pk).first()
            serializer = CourseSerializer(course)
            courses_connect_tag = random.sample(CourseSerializer(Courses.objects.filter(tag=course.tag),many=True).data,3 if len(Courses.objects.filter(tag=course.tag)) >3 else len(Courses.objects.filter(tag=course.tag)))
            for c in range(len(courses_connect_tag)):
                if courses_connect_tag[c]['code'] == serializer.data['code']:
                    courses_connect_tag.remove(courses_connect_tag[c])
                    break
            c =CoruseSchedules.objects.get(id=serializer.data['schedule_id'])
            sc = CourseSchedulesSerializer(c,many=False)
            response = serializer.data
            response['schedule_id'] = sc.data
            for pre in range(len(response['prerequisites'])):
                response['prerequisites'][pre] = CourseSerializer(Courses.objects.get(code=response['prerequisites'][pre]),many=False).data
            r = True if studentsReg.objects.filter(course_id=course.code,student_id=Students.objects.filter(user=User.objects.filter(username=response_data['user']['username']).first()).first()).first() != None else False
            length = len(studentsReg.objects.filter(course_id=pk))
            res = {'course':response,'registered':r,'courses_connect_tag':courses_connect_tag,'student_length':length}
            return Response(res)
        else:
            return Response({"message": "The user is not authenticated."})
    def put(self, request, pk):
        global response_data
        if isinstance(response_data, dict) and response_data.get('admin'):
            data = request.data.get('courseData', {})
            image = request.FILES.get('image')
            course_data = data.get('course', {})
            course_data['image'] = image
            schedule_data = data.get('schedule', {})

            # Retrieve the course object
            course = Courses.objects.filter(code=pk).first()
            if not course:
                return Response({"message": "Course not found."}, status=404)

            # Update the schedule first
            schedule = CoruseSchedules.objects.filter(id=course.schedule_id).first()
            if schedule:
                schedule_serializer = CourseSchedulesSerializer(schedule, data=schedule_data)
                if schedule_serializer.is_valid():
                    schedule_serializer.save()
                else:
                    return Response(schedule_serializer.errors, status=400)
            else:
                return Response({"message": "Schedule not found."}, status=404)

            # Update the course with the new schedule ID
            course_data['schedule_id'] = schedule.id
            course_serializer = CourseSerializer(course, data=course_data)
            if course_serializer.is_valid():
                course_serializer.save()
                return Response(course_serializer.data, status=200)
            else:
                return Response(course_serializer.errors, status=400)

        return Response({"message": "The user is not authorized."}, status=403)

class CourseScheduleVIEW(APIView):
    def post(self, request):
        global response_data
        if isinstance(response_data, dict) and response_data.get('admin'):
            serializer_newschdule = CourseSchedulesSerializer(data=request.data)      
            if serializer_newschdule.is_valid():
                if serializer_newschdule.is_valid():
                    serializer_newschdule.save()
                    return Response(serializer_newschdule.data, status=201)
                return Response(serializer_newschdule.errors, status=400)
            return Response(serializer_newschdule.errors, status=400)
        return Response({"message": "The user is not authorized."}, status=403)

class CoursesSelect(APIView):
    def post(self, request):
        global response_data
        if not response_data:
            return Response({"message": "The user is not authenticated."}, status=401)
        user_object = User.objects.filter(username=response_data['user']['username']).first()
        if not user_object:
            return Response({"message": "User not found."}, status=404)
        user_student = Students.objects.filter(user=user_object).first()
        if not user_student:
            return Response({"message": "Student profile not found for user."}, status=404)
        mutable_data = request.data.copy()
        mutable_data['student_id'] = user_student.id
        my_new_course = Courses.objects.get(code=request.data.get('course_id'))
        for c in studentsReg.objects.filter(course_id=my_new_course):
            if my_new_course in c.course_id.prerequisites:
                break
            if c == studentsReg.objects.filter(course_id=my_new_course).last():
                return Response({'message':'You can\'t join in this course.'})
        for c in Courses.objects.all():
            if studentsReg.objects.filter(course_id = c.code,student_id = user_student.id):
                if my_new_course.schedule_id.start_time == c.schedule_id.start_time: 
                    return Response({'message':'It conflicts with another lecture.'})
        for sr in studentsReg.objects.filter(student_id=str(user_student.id)):
            if request.data.get('course_id') == sr.course_id.code:
                return Response({"message": "The student is already registered in this course."}, status=400)
        length = len(studentsReg.objects.filter(course_id=request.data.get('course_id')))
        course = Courses.objects.filter(code=request.data.get('course_id')).first()
        if not course:
            return Response({"message": "Course not found."}, status=404)
        if length >= course.capacity:
            return Response({"message": "The course capacity is full."}, status=400)
        serializer = StudentRegSerializer(data=mutable_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
    def get(self, request):
        global response_data
        if response_data:
            user_object = User.objects.filter(username=response_data['user']['username']).first()
            if not user_object:
                return Response({"message": "User not found."}, status=404)
            user_student = Students.objects.filter(user=user_object).first()
            if not user_student:
                return Response({"message": "No student profile found for this user."}, status=404)
            my_courses = studentsReg.objects.filter(student_id=user_student.id)
            serializer = StudentRegSerializer(my_courses, many=True)
            response=[]
            for s in range(len(serializer.data)):
                c =Courses.objects.get(code=serializer.data[s]['course_id'])
                ser = CourseSerializer(c,many=False)
                response.append(ser.data)
            return Response(response,status=200)
        return Response({"message": "The user is not authenticated."}, status=401)
class Search(APIView):
    def post(self,request):
        global response_data
        if response_data:
            search_query = request.data.get('query')
            courses = Courses.objects.filter(Q(name__icontains=search_query))
            serializer = CourseSerializer(courses,many=True)
            response = []
            for s in range(len(serializer.data)):
                c =CoruseSchedules.objects.get(id=serializer.data[s]['schedule_id'])
                sc = CourseSchedulesSerializer(c,many=False)
                serializer.data[s]['schedule_id'] = sc.data
                response.append(serializer.data[s])
            return Response(response,status=200)
        return Response({"message": "The user is not authenticated."}, status=401)
class Notification(APIView):
    def get(self, request):
        global response_data
        if response_data:
            user_object = User.objects.filter(username=response_data['user']['username']).first()
            if not user_object:
                return Response({"message": "User not found."}, status=404)
            user_student = Students.objects.filter(user=user_object).first()
            if not user_student:
                return Response({"message": "No student profile found for this user."}, status=404)
            my_courses = studentsReg.objects.filter(student_id=user_student.id)
            serializer = StudentRegSerializer(my_courses, many=True)
            response = []
            now = datetime.now()
            for s in range(len(serializer.data)):
                c = Courses.objects.get(code=serializer.data[s]['course_id'])
                course_start_datetime = datetime.combine(date.today(), c.schedule_id.start_time)
                difference = course_start_datetime - now - timedelta(minutes=10)
                if difference.total_seconds() < 60:
                    ser = NotificationSerializer({'course_name': c.name, 'start_time': c.schedule_id.start_time}, many=False)
                    response.append(ser.data)
            return Response(response, status=200)
        return Response({"message": "The user is not authenticated."}, status=401)
