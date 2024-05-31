from rest_framework.views import APIView
from rest_framework.response import Response
from core.serializers import LoginSerializer, StudentRegSerializer, StudentSerializer,CourseSerializer,CourseSchedulesSerializer,NotificationSerializer
from .models import CoruseSchedules, Courses,Students,studentsReg,Notification,Prerequisties
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
import random
import matplotlib.pyplot as plt
import io
import base64
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
                admin = user.is_superuser
                print(user.is_superuser)
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
            prereqieste = course_data['prerequisites']

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
            note= {'title':'Append','message':f'Append the {course_data.get("name")} course.'}
            notification = NotificationSerializer(data=note)
            if notification.is_valid():
                notification.save()
            # Save course with schedule_id
             
            course_data['schedule_id'] = schedule.id
            print(course_data['image'])
            course_serializer = CourseSerializer(data=course_data)
            if course_serializer.is_valid():
                course_serializer.save()
                if prereqieste!='':
                    prereqiestes = Prerequisties.objects.create(
                    course=Courses.objects.get(code=course_serializer.data['code']),
                    course_prerequisite = Courses.objects.get(name=prereqieste),
                    ).save()
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
    def delete(self,request,pk):
        global response_data
        if isinstance(response_data, dict) and response_data.get('admin'):
            note= {'title':'Delete','message':f'Delete the {Courses.objects.get(code = pk).name} course.'}
            notification = NotificationSerializer(data=note)
            if notification.is_valid():
                notification.save()

                Courses.objects.get(code = pk).delete()
                return Response({"message": "Delete The Course."}, status=400)
            return Response({"message": "Error."}, status=404)

    def put(self, request, pk):
        global response_data
        if isinstance(response_data, dict) and response_data.get('admin'):
            data = request.data.get('courseData', {})
            print('Received data:', data)  # تأكد من البيانات المستلمة

            course_data = data.get('course', {})
            schedule_data = data.get('schedule', {})
            
            if not course_data or not schedule_data:
                return Response({"message": "Invalid data."}, status=400)

            try:
                course = Courses.objects.get(code=pk)
            except Courses.DoesNotExist:
                return Response({"message": "Course not found."}, status=404)
            
            if 'name' not in course_data:
                return Response({"message": "Missing 'name' in course data."}, status=400)
            course.name = course_data['name']
            course.description = course_data['description']
            course.instractor = course_data['instractor']
            course.capacity = course_data['capacity']
            course.save()
            try:
                schedule = CoruseSchedules.objects.get(id=course.schedule_id.id)
            except CoruseSchedules.DoesNotExist:
                return Response({"message": "Schedule not found."}, status=404)
            
            schedule.days = schedule_data['days']
            schedule.start_time = schedule_data['start_time']
            schedule.end_time = schedule_data['end_time']
            schedule.room_no = schedule_data['room_no']
            schedule.save()
            note= {'title':'Update','message':f'Update the {Courses.objects.get(code = pk).name} course.'}
            notification = NotificationSerializer(data=note)
            if notification.is_valid():
                notification.save()
            # تحديث الدورة بمعرف جدول الدورة المحدث
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
        for c in studentsReg.objects.filter(student_id=user_student,course_id=my_new_course):
            if my_new_course in c.course_id.prerequisites:
                print(c)
                break
            if c == studentsReg.objects.filter(course_id=my_new_course).last():
                print(c)
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
            courses = Courses.objects.filter(Q(name__icontains=search_query) | Q(code__icontains=search_query) | Q(instractor__icontains=search_query))
            serializer = CourseSerializer(courses,many=True)
            response = []
            for s in range(len(serializer.data)):
                c =CoruseSchedules.objects.get(id=serializer.data[s]['schedule_id'])
                sc = CourseSchedulesSerializer(c,many=False)
                serializer.data[s]['schedule_id'] = sc.data
                response.append(serializer.data[s])
            return Response(response,status=200)
        return Response({"message": "The user is not authenticated."}, status=401)
class NotificationVIEW(APIView):
    def get(self, request):
        global response_data
        if response_data:
            user_object = User.objects.filter(username=response_data['user']['username']).first()
            if not user_object:
                return Response({"message": "User not found."}, status=404)
            user_student = Students.objects.filter(user=user_object).first()
            if not user_student:
                return Response({"message": "No student profile found for this user."}, status=404)
            
            noteification=NotificationSerializer(data=Notification.objects.all(),many=True) 
            noteification.is_valid()
            return Response(noteification.data, status=200)
        return Response({"message": "The user is not authenticated."}, status=401)


class ReportVIEW(APIView):
    def get(self, request):
        global response_data
        if response_data:
            tags = [course.tag for course in Courses.objects.all()]
            filtering_tags = []
            for tag in tags:
                if tag not in filtering_tags:
                    filtering_tags.append(tag)

            images_data = {}  # Dictionary to store images in Base64 format

            for tag in filtering_tags:
                courses = Courses.objects.filter(tag=tag).count()
                students_reg = studentsReg.objects.filter(course_id__tag=tag).count()

                # إعداد الرسم البياني
                fig, ax = plt.subplots(figsize=(12, 8))

                rects1 = ax.bar(['Number of Courses'], [courses], width=0.35, color='skyblue', label='Number of Courses')
                rects2 = ax.bar(['Total Enrollments'], [students_reg], width=0.35, color='orange', label='Total Enrollments')

                # إضافة بعض النصوص
                ax.set_xlabel('Metrics')
                ax.set_ylabel('Count')
                ax.set_title(f'Number of Courses and Total Enrollments for {tag}')
                ax.legend()

                # إضافة التسميات للأعمدة
                def autolabel(rects):
                    for rect in rects:
                        height = rect.get_height()
                        ax.annotate('{}'.format(height),
                                    xy=(rect.get_x() + rect.get_width() / 2, height),
                                    xytext=(0, 3),  # 3 points vertical offset
                                    textcoords="offset points",
                                    ha='center', va='bottom')

                autolabel(rects1)
                autolabel(rects2)

                fig.tight_layout()

                # حفظ الرسم في الذاكرة كصورة Base64
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                buf.close()
                plt.close(fig)

                images_data[tag] = image_base64

            return Response({"images": images_data}, status=200)

        return Response({"message": "The user is not authenticated."}, status=401)