from django.contrib import admin
from .models import Teacher, Student, Score, SchoolClass, Subject, ResultSummary
from django.utils.html import format_html


admin.site.site_header = "New Generation Prep. Administration"
admin.site.site_title = "New Generation Prep. Admin"
admin.site.index_title = "Welcome to New Generation Prep. Administration"


class ReadOnlyAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

class StudentAdmin(ReadOnlyAdmin):

    list_display = ("first_name", "last_name", "school_class", "report_link")

    def report_link(self, obj):
        return format_html(
            '<a href="/report/{}/1/" target="_blank">Open Report</a>',
            obj.id
        )

    report_link.short_description = "Report Card"

admin.site.register(SchoolClass)
admin.site.register(Subject)
admin.site.register(Student, StudentAdmin)



class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'level', 'class_teacher_of', 'approved')
    readonly_fields = ("subjects", "level", "full_name", "user")
    list_filter = ('level', 'approved')
    search_fields = ('full_name', 'user__username')
    actions = ['approve_teachers']

    def approve_teachers(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected teachers have been approved.")

    approve_teachers.short_description = "Approve selected teachers"


admin.site.register(Teacher, TeacherAdmin)


class ScoreAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'subject',
        'term',
        'class_score',
        'exam_score',
        'total',
        'grade',
        'position',
        'approved_by_admin1',
        'approved_by_admin2'
    )

    readonly_fields = (
        "student",
        "subject",
        "term",
        "class_score",
        "exam_score",
        "total",
        "grade",
        "position",
    )

    list_filter = ("term", "subject")

    search_fields = (
        "student__first_name",
        "student__last_name",
    )

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):

        if request.user.is_superuser:
            return self.readonly_fields

        return self.readonly_fields + (
            "approved_by_admin1",
            "approved_by_admin2",
        )   

admin.site.register(Score, ScoreAdmin)


@admin.register(ResultSummary)
class ResultSummaryAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "term",
        "attendance_days",
        "vacation_date",
        "reopening_date",
        "next_term_bill",
    )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ["attendance_days", "class_teacher_remark"]
        return ["attendance_days", "class_teacher_remark", "next_term_bill"]