from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Teacher
    path("teacher/signup/", views.teacher_signup, name="teacher-signup"),
    path("teacher/login/", views.teacher_login, name="teacher-login"),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher-dashboard/", views.teacher_dashboard, name="teacher_dashboard_alt"),

    # Enter Scores
    path("teacher/enter-scores/", views.enter_scores, name="enter_scores"),
    path("enter-scores/", views.enter_scores, name="enter_scores"),

    # Approved Results
    path("approved-results/", views.approved_results, name="approved_results"),

    # Report Card
    path("report/<int:student_id>/<str:term>/", views.report_card, name="report_card"),
    path("report/pdf/<int:student_id>/<int:term>/", views.report_card_pdf, name="report_pdf"),

    # Class Results
    path(
        "class-results/<int:class_id>/<str:term>/",
        views.class_results,
        name="class_results",
    ),

    # Result Slip
    path("result-slip/<int:student_id>/", views.result_slip, name="result_slip"),

    path(
        "promote-students/",
        views.promote_students,
        name="promote_students",
    ),

]