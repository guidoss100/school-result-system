from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Student, SchoolClass, Score, Subject, Teacher
from .forms import TeacherSignupForm
from .models import Student, Score, ResultSummary
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string


def home(request):
    return render(request, 'home.html')



def promote_students():
    
    students = Student.objects.all()

    promotion_map = {
        "Primary 1": "Primary 2",
        "Primary 2": "Primary 3",
        "Primary 3": "Primary 4",
        "Primary 4": "Primary 5",
        "Primary 5": "Primary 6",
        "Primary 6": "JHS 1",
        "JHS 1": "JHS 2",
        "JHS 2": "JHS 3"
    }

    for student in students:

        current_class = student.school_class.name

        if current_class in promotion_map:

            new_class_name = promotion_map[current_class]

            new_class = SchoolClass.objects.get(name=new_class_name)

            student.school_class = new_class
            student.save()


@login_required
def teacher_dashboard(request):

    teacher = Teacher.objects.get(user=request.user)

    subjects = teacher.subjects.all()

    context = {
        "teacher": teacher,
        "subjects": subjects
    }

    return render(request, "core/teacher_dashboard.html", context)


# TEACHER SIGNUP
def teacher_signup(request):
    if request.method == "POST":
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken.")
                return redirect('teacher_signup')

            # Create user
            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            # Create teacher
            teacher = Teacher.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                level=form.cleaned_data['level']
            )

            teacher.subjects.set(form.cleaned_data['subjects'])
            teacher.save()

            messages.success(request, "Signup successful! Waiting for admin approval.")
            return redirect('teacher-login')
    else:
        form = TeacherSignupForm()

    return render(request, "teacher_signup.html", {"form": form})


# TEACHER LOGIN
def teacher_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            try:
                teacher = Teacher.objects.get(user=user)

                if teacher.approved:
                    login(request, user)
                    return redirect("teacher_dashboard")
                else:
                    messages.error(request, "Your account is not approved yet.")

            except Teacher.DoesNotExist:
                messages.error(request, "You are not registered as a teacher.")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "core/teacher_login.html")


# ENTER MARKS FOR CLASS
def enter_marks(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    students = Student.objects.filter(school_class=school_class)
    subjects = Subject.objects.all()

    if request.method == 'POST':
        for student in students:
            for subject in subjects:
                key = f"{student.id}_{subject.id}"
                mark = request.POST.get(key)

                if mark:
                    Score.objects.update_or_create(
                        student=student,
                        subject=subject,
                        term='1st Term',
                        defaults={'marks': float(mark)}
                    )
        return redirect('teacher_dashboard')

    scores = Score.objects.filter(student__in=students)

    return render(request, 'core/enter_marks.html', {
        'school_class': school_class,
        'students': students,
        'subjects': subjects,
        'scores': scores
    })


# STUDENT PORTAL
def student_portal(request):
    student = None
    scores = []
    average = None

    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        try:
            student = Student.objects.get(admission_number=admission_number)
            scores = Score.objects.filter(student=student, fully_approved=True)
            if scores.exists():
                total = sum(score.marks for score in scores)
                average = total / scores.count()
        except Student.DoesNotExist:
            student = None

    return render(request, 'core/student_portal.html', {
        'student': student,
        'scores': scores,
    })


# RESULT SLIP
def result_slip(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    scores = Score.objects.filter(student=student, fully_approved=True)

    average = None
    if scores.exists():
        total = sum(score.marks for score in scores)
        average = total / scores.count()

    return render(request, 'core/result_slip.html', {
        'student': student,
        'scores': scores,
    })



# HELPER: CREATE SCORES FOR STUDENT
def create_scores_for_student(student, term="Term 1"):
    level = student.school_class.level
    subjects = Subject.objects.filter(level=level)
    for subject in subjects:
        Score.objects.get_or_create(
            student=student,
            subject=subject,
            term=term,
            defaults={'class_score': 0, 'exam_score': 0}
        )


@login_required
def enter_scores(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("teacher-login")

    classes = SchoolClass.objects.filter(level=teacher.level)
    subjects = teacher.subjects.all()

    students = None
    selected_class = None
    selected_subject = None
    selected_term = None
    existing_scores = {}   # ADD THIS LINE

    if request.method == "POST":
        selected_class = request.POST.get("class_id")
        selected_subject = request.POST.get("subject_id")
        selected_term = request.POST.get("term")

        students = Student.objects.filter(school_class_id=selected_class)

        # Save scores
        if "save_scores" in request.POST:
            subject = Subject.objects.filter(id=selected_subject).first()
            if not subject:
                return redirect("enter_scores/?class_id={selected_class}&subject_id={selected_subject}&term={selected_term}")

            for student in students:
                class_score = request.POST.get(f"class_{student.id}")
                exam_score = request.POST.get(f"exam_{student.id}")

                existing = Score.objects.filter(
                    student=student,
                    subject=subject,
                    term=selected_term
                ).first()
        
                # 🚫 BLOCK editing if already approved
                if existing and existing.approved_by_admin1 and existing.approved_by_admin2:
                    continue

                if class_score is not None and exam_score is not None:
                    Score.objects.update_or_create(
                        student=student,
                        subject=subject,
                        term=selected_term,
                        defaults={
                            "class_score": int(class_score),
                            "exam_score": int(exam_score)
                        }
                    )

                


            # calculate positions
            scores = Score.objects.filter(
                subject=subject,
                term=selected_term,
                student__school_class_id=selected_class
            ).order_by("-class_score", "-exam_score")


            # reload the scores so existing_scores has updated objects
            scores = Score.objects.filter(
                subject=subject,
                term=selected_term,
                student__school_class_id=selected_class
            )
            existing_scores = {s.student.id: s for s in scores}

        # ✅ HANDLE GET REQUEST (very important fix)
        if request.method == "GET":
            selected_class = request.GET.get("class_id")
            selected_subject = request.GET.get("subject_id")
            selected_term = request.GET.get("term")

            if selected_class and selected_subject and selected_term:
                students = Student.objects.filter(school_class_id=selected_class)

                scores = Score.objects.filter(
                    subject_id=selected_subject,
                    term=selected_term,
                    student__school_class_id=selected_class
                )

                existing_scores = {s.student.id: s for s in scores}   

    return render(request, "core/enter_scores.html", {
        "classes": classes,
        "subjects": subjects,
        "students": students,
        "selected_class": selected_class,
        "selected_subject": selected_subject,
        "selected_term": selected_term,
        "existing_scores": existing_scores
    })


# STUDENT REPORT
def student_report(request, student_id):
    student = Student.objects.get(id=student_id)
    scores = Score.objects.filter(student=student)

    total_marks = sum(score.total for score in scores)
    subject_count = scores.count()
    
    context = {
        'student': student,
        'scores': scores,
        'total_marks': total_marks,
    }

    return render(request, 'student_report.html', context)

def report_card(request, student_id, term):

    student = get_object_or_404(Student, id=student_id)

    scores = Score.objects.filter(
        student=student,
        term=term,
        approved_by_admin1=True,
        approved_by_admin2=True
    )

    total_marks = sum(score.total for score in scores)
    subject_count = scores.count()

    # Calculate overall class position
    class_students = Student.objects.filter(
    school_class=student.school_class
    )


    rank = 1
    for s in class_students:
        if s.id == student.id:
            overall_position = rank
            break
        rank += 1

    summary = ResultSummary.objects.filter(
        student=student,
        term=term
    ).first()

    context = {
        "student": student,
        "scores": scores,
        "total_marks": total_marks,
        "summary": summary,
        "overall_position": overall_position
}
    if term == "3":
        promote_students()

    return render(request, "core/report_card.html", context)

@login_required
def class_results(request, class_id, term):

    # Get the class
    school_class = get_object_or_404(SchoolClass, id=class_id)

    # Get all students in the class
    students = Student.objects.filter(school_class=school_class)


    # Assign overall positions
    rank = 1
    for student in students:
        student.overall_position = rank
        rank += 1

    return render(request, "core/class_results.html", {
        "school_class": school_class,
        "students": students,
        "term": term
    })


def report_card_pdf(request, student_id, term):
    student = get_object_or_404(Student, id=student_id)

    scores = Score.objects.filter(
        student=student,
        term=term,
        approved_by_admin1=True,
        approved_by_admin2=True
    )

    total_marks = sum(score.total for score in scores)

    summary = ResultSummary.objects.filter(
        student=student,
        term=term
    ).first()

    context = {
        "student": student,
        "scores": scores,
        "total_marks": total_marks,
        "summary": summary,
    }

    html_string = render_to_string("core/report_card.html", context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="report_{student.id}.pdf"'


    return response

@login_required
def approved_results(request):

    teacher = Teacher.objects.get(user=request.user)

    students = None
    selected_term = request.GET.get("term")

    # HANDLE POST
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        term = request.POST.get("term")

        summary, created = ResultSummary.objects.get_or_create(
            student_id=student_id,
            term=term
        )

        # 🚫 DO NOT EDIT if already locked
        if summary.locked:
            return redirect(request.path)

        # ✅ Allow editing ONLY if not locked
        summary.attendance_days = request.POST.get("attendance")
        summary.class_teacher_remark = request.POST.get("remark")
        summary.locked = True
        summary.save()

        return redirect(request.path)

    # HANDLE GET
    if teacher.class_teacher_of and selected_term:
        students = Student.objects.filter(
            school_class=teacher.class_teacher_of
        )

        for student in students:
            scores = Score.objects.filter(
                student=student,
                term=selected_term,
                approved_by_admin1=True,
                approved_by_admin2=True
            )

            student.scores = scores

            summary = ResultSummary.objects.filter(
                student=student,
                term=selected_term
            ).first()

            if not summary:
                summary = ResultSummary.objects.create(
                    student=student,
                    term=selected_term
                )

            student.summary = summary

    # ✅ THIS MUST BE INSIDE FUNCTION
    return render(request, "approved_results.html", {
        "students": students,
        "selected_term": selected_term,
        "teacher": teacher
    })