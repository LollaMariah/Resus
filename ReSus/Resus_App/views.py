from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from .models import User, Role, Course, Topic
from neomodel.exceptions import DoesNotExist
from django.http import Http404,HttpResponseNotFound
from neomodel import db
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import logging

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = make_password(form.cleaned_data['password'])
            try:
                user = User(email=email, name=name, password=password).save()
                messages.success(request, 'Registration successful.')
                return redirect('login')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.nodes.get(email=email)
                if check_password(password, user.password):
                    request.session['user_id'] = str(user.userId)
                    request.session['user_name'] = user.name
                    messages.success(request, 'Login successful.')
                    return redirect('pilih_role')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(request, 'User does not exist.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout(request):
    try:
        del request.session['user_id']
        del request.session['username']
    except KeyError:
        pass
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

@login_required
def course_list(request):
    selected_topics = request.GET.getlist('topics')
    courses = []

    try:
        if selected_topics:
            query = """
            MATCH (c:Course)-[:IS_ABOUT]->(t:Topic)
            WHERE t.name IN $topics
            OPTIONAL MATCH (c)<-[r:HAS_ACCESSED]-()
            OPTIONAL MATCH (c)-[:BELONGS_TO]->(p:Platform)
            WITH c, p, COUNT(r) as degree
            SET c.degree = degree
            RETURN c, p
            ORDER BY degree DESC
            """
            results, meta = db.cypher_query(query, {'topics': selected_topics})
        else:
            query = """
            MATCH (c:Course)
            OPTIONAL MATCH (c)<-[r:HAS_ACCESSED]-()
            OPTIONAL MATCH (c)-[:BELONGS_TO]->(p:Platform)
            WITH c, p, COUNT(r) as degree
            SET c.degree = degree
            RETURN c, p
            ORDER BY degree DESC
            """
            results, meta = db.cypher_query(query, {})

        for record in results:
            course = Course.inflate(record[0])
            platform = record[1]["name"] if record[1] else None
            courses.append({
                "courseId": course.courseId,
                "title": course.title,
                "description": course.description,
                "duration": course.duration,
                "image": course.image,
                "level": course.level,
                "price": course.price,
                "url": course.url,
                "degree": course.degree,
                "platform": platform
            })

        # Determine the top 3 courses by degree centrality
        top_courses = sorted(courses, key=lambda x: x['degree'], reverse=True)[:3]

        return render(request, 'kursus/course_list.html', {'courses': courses, 'selected_topics': selected_topics, 'top_courses': top_courses})

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Error retrieving courses")

@login_required
def course_detail(request, course_id):
    try:
        course = Course.nodes.get(courseId=course_id)
        platform_query = """
        MATCH (c:Course)-[:BELONGS_TO]->(p:Platform)
        WHERE c.courseId = $course_id
        RETURN p
        """
        platform_result, meta = db.cypher_query(platform_query, {'course_id': course_id})
        platform = platform_result[0][0] if platform_result else None
    except DoesNotExist:
        raise Http404("Course does not exist")
    
    return render(request, 'kursus/course_detail.html', {'course': course, 'platform': platform})


@login_required
def pilih_role(request):
    roles = Role.nodes.all()
    return render(request, 'kursus/pilih_role.html', {'roles': roles})

@login_required
def topics(request):
    role_name = request.GET.get('role')
    topics = []
    if role_name:
        try:
            role = Role.nodes.get(name=role_name)
            topics = role.topics.all()
        except Role.DoesNotExist:
            messages.error(request, 'Role does not exist.')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'kursus/topics.html', {'topics': topics, 'role_name': role_name})

@login_required
def profile(request):
    return render(request, 'profile/profile.html')

def index(request):
    return render(request, 'kursus/index.html')

def home(request):
    return render(request, 'home.html')

@login_required
def access_course(request, course_id):
    try:
        # Ambil pengguna yang terautentikasi dari sesi Django
        django_user = request.user
        user = User.nodes.get(userId=str(django_user.id))
        
        # Ambil kursus yang akan diakses
        course = Course.nodes.get(courseId=course_id)
        
        # Hubungkan pengguna dengan kursus
        user.has_accessed.connect(course, {'date_accessed': timezone.now()})
        
        # Ambil URL kursus dan lemparkan pengguna ke URL tersebut
        return redirect(course.url)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('login')
    except Course.DoesNotExist:
        messages.error(request, 'Course does not exist.')
        return redirect('course_list')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('course_list')
    
def all_topics(request):
    topics = Topic.nodes.all()
    return render(request, 'kursus/all_topics.html', {'topics': topics})

def all_role(request):
    roles = Role.nodes.all()
    return render(request, 'kursus/all_role.html', {'roles': roles})

def get_recommended_courses():
    # Ambil semua relasi RECOMMENDS antara Role dan Course
    recommends = Role.objects.filter(recommends__isnull=False).values_list('name', 'recommends__title')
    return recommends

def recommended_courses(request):
    # Dapatkan role yang dipilih dari parameter URL
    selected_role = request.GET.get('role')

    # Dapatkan node Role yang sesuai
    role = Role.nodes.get_or_none(name=selected_role)

    recommended_courses = []
    if role:
        # Ambil semua Course yang terkait dengan role yang dipilih
        for topic in role.topics.all():
            recommended_courses.extend(topic.is_about.all())

        # Urutkan recommended_courses berdasarkan degree centrality (descending)
        recommended_courses = sorted(recommended_courses, key=lambda course: course.degree, reverse=True)

    return render(request, 'kursus/recommended_courses.html', {'recommended_courses': recommended_courses, 'selected_role': selected_role})

def accessed_users(request):
    try:
        user_id = request.session.get('user_id')
        user = User.nodes.get(userId=user_id)
        accessed_courses = user.has_accessed.all()
        return render(request, 'profile/profile.html', {'accessed_courses': accessed_courses})
    except User.DoesNotExist:
        # Handle the case when user does not exist
        pass
    
logger = logging.getLogger(__name__)

@login_required
@require_POST
def access_course(request):
    user = request.user
    course_id = request.POST.get('course_id')

    logger.info(f"User: {user.username}, Course ID: {course_id}")

    try:
        query = """
        MATCH (u:User {name: $name}), (c:Course {courseId: $course_id})
        MERGE (u)-[:HAS_ACCESSED {date_accessed: datetime()}]->(c)
        RETURN u, c
        """
        params = {'name': user.username, 'course_id': course_id}
        logger.info(f"Running query: {query} with params: {params}")
        results, meta = db.cypher_query(query, params)
        logger.info(f"Query Results: {results}")
        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        logger.error(f"Error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)