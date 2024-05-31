from django.urls import path
from . import views
urlpatterns = [
    path('register',views.Register.as_view(),name='register'),
    path('login',views.Login.as_view(),name='login'),
    path('logout',views.Logout.as_view(),name='logout'),
    path('courses',views.CourseVIEW.as_view(),name='course'),
    path('courses-schedule',views.CourseScheduleVIEW.as_view(),name='courses-schedule'),
    path('courses/<int:pk>',views.CourseVIEW.as_view(),name='course'),
    path('select-course',views.CoursesSelect.as_view(),name='course'),
    path('search',views.Search.as_view(),name='search'),
    path('notifications',views.NotificationVIEW.as_view(),name='notifications'),
    path('Update-course/<int:pk>',views.UpdateVIEW.as_view(),name='update'),
    path('report/',views.ReportVIEW.as_view(),name='report')
    # path('test',views.test.as_view(),name='test'),
]