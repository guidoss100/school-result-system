from django.urls import path
from . import views
from .views import student_report

urlpatterns = [
    path('teacher/signup/', views.teacher_signup, name='teacher-signup'),
    path("teacher/login/", views.teacher_login, name="teacher_login"),
    path("teacher/login/", views.teacher_login, name="teacher-login"),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("report/pdf/<int:student_id>/<int:term>/", views.report_card_pdf, name="report_pdf"),
    path('report/<int:student_id>/', student_report, name='student_report'),
    path('create-admin/', views.create_admin),
    path('teacher/enter-scores/', views.enter_scores, name='enter_scores'),
    path("approved-results/", views.approved_results, name="approved_results"),
    path('enter-scores/', views.enter_scores, name='enter_scores'),
    path(
    "report/<int:student_id>/<str:term>/",
    views.report_card,
    name="report_card"
),
    path('class-results/<int:class_id>/<str:term>/', views.class_results, name='class_results'),

    path("teacher-dashboard/", views.teacher_dashboard, name="teacher_dashboard_alt"),

    path("enter-marks/<int:class_id>/", views.enter_marks, name="enter_marks"),
    
    path("student-portal/", views.student_portal, name="student_portal"),
    path("result-slip/<int:student_id>/", views.result_slip, name="result_slip"),
]
    
    