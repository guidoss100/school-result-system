from django.db import models
from django.contrib.auth.models import User

class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    LEVEL_CHOICES = (
        ('Primary', 'Primary'),
        ('JHS', 'JHS'),
    )
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)

    def __str__(self):
        return self.name

class Student(models.Model):
    LEVEL_CHOICES = (
        ("Primary", "Primary"),
        ("JHS", "JHS"),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    admission_number = models.CharField(max_length=100, unique=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"
    
    @property
    def total(self):
        return self.class_score + self.exam_score

    @property
    def overall_position(self):

        students = Student.objects.filter(
            school_class=self.school_class
        )

        ranked = sorted(
            students,
            key=lambda s: s.term_average,
            reverse=True
        )

        position = 1
        for s in ranked:
            if s == self:
                return position
            position += 1

class Subject(models.Model):
    LEVEL_CHOICES = [
        ('Primary', 'Primary'),
        ('JHS', 'JHS'),
    ]
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.level})"

class Teacher(models.Model):
    LEVEL_CHOICES = [
        ('Primary', 'Primary'),
        ('JHS', 'JHS'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    subjects = models.ManyToManyField(Subject)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
    class_teacher_of = models.ForeignKey(
    SchoolClass,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    TERM_CHOICES = [
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
    ]
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    class_score = models.IntegerField()
    exam_score = models.IntegerField()
    approved_by_admin1 = models.BooleanField(default=False)
    approved_by_admin2 = models.BooleanField(default=False)

    locked = models.BooleanField(default=False)

    

    @property
    def grade(self):
        total = self.total
        if self.student.level == "JHS":
            if total >= 90: return 1
            elif total >= 80: return 2
            elif total >= 70: return 3
            elif total >= 65: return 4
            elif total >= 60: return 5
            elif total >= 55: return 6
            elif total >= 50: return 7
            elif total >= 40: return 8
            else: return 9
        else:
            if total >= 80: return "A"
            elif total >= 70: return "B"
            elif total >= 60: return "C"
            elif total >= 50: return "D"
            elif total >= 40: return "E"
            else: return "F"

    

    @property
    def remark(self):
        level = self.student.school_class.level
        g = self.grade
        if level == "Primary":
            if g == "A": return "Excellent"
            elif g == "B": return "Very Good"
            elif g == "C": return "Good"
            elif g == "D": return "Fair"
            else: return "Poor"
        else:  # JHS
            if g in [1, 2,]: return "Excellent"
            elif g in [3, 4, 5]: return "Good"
            elif g in [6, 7]: return "Fair"
            else: return "Poor"

    @property
    def fully_approved(self):
        return self.approved_by_admin1 and self.approved_by_admin2

    def __str__(self):
        return f"{self.student} - {self.subject}"

# NEW MODEL FOR REPORT SUMMARY
class ResultSummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=Score.TERM_CHOICES)
    attendance_days = models.PositiveIntegerField(default=0)
    vacation_date = models.DateField(null=True, blank=True)
    reopening_date = models.DateField(null=True, blank=True)
    class_teacher_remark = models.TextField(blank=True)
    headmaster_remark = models.TextField(blank=True)
    next_term_bill = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_marks = models.IntegerField(default=0)
    

    def __str__(self):
        return f"{self.student} - Term {self.term}"

    
    locked = models.BooleanField(default=False)   # ✅ ADD THIS

    class Meta:
        unique_together = ('student', 'term')