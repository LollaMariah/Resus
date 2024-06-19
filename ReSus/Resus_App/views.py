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

# @login_required
def profile(request):
    if 'userId' not in request.session:
        return redirect('login')
    return render(request, 'profile/profile.html')

def index(request):
    return render(request, 'kursus/index.html')

def home(request):
    return render(request, 'home.html')

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

# @login_required
def logout(request):
    try:
        del request.session['userId']
        del request.session['name']
    except KeyError:
        pass
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

logger = logging.getLogger(__name__)

# @login_required
def course_list(request):
    selected_topics = request.GET.getlist('topics')
    courses = []

    logger.info(f"Selected topics: {selected_topics}")

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
            ORDER BY degree DESC, p.weight DESC
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
            ORDER BY degree DESC, p.weight DESC
            """
            results, meta = db.cypher_query(query, {})

        logger.info(f"Query results: {results}")

        for record in results:
            course = Course.inflate(record[0])
            platform = record[1]["name"] if record[1] else None
            platform_weight = record[1]["weight"] if record[1] else 0
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
                "platform": platform,
                "platform_weight": platform_weight
            })

        # Determine the top 3 courses by degree centrality and platform weight
        top_courses = sorted(courses, key=lambda x: (x['degree'], x['platform_weight']), reverse=True)[:3]

        return render(request, 'kursus/course_list.html', {'courses': courses, 'selected_topics': selected_topics, 'top_courses': top_courses})

    except Exception as e:
        logger.error(f"Error: {e}")
        raise Http404("Error retrieving courses")

# @login_required
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

# @login_required
def pilih_role(request):
    roles = Role.nodes.all()
    return render(request, 'kursus/pilih_role.html', {'roles': roles})

# @login_required
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
        pass
    
logger = logging.getLogger(__name__)

# @login_required
def log_course_access(request, course_title):
    user_name = request.session.user_name

    try:
        user = User.nodes.get(name=user_name)
        course = Course.nodes.get(title=course_title)
        user.has_accessed.connect(course, {'datetime': timezone.now()})
    except User.DoesNotExist:
        messages.error(request, 'Pengguna tidak ada.')
        return redirect('login')
    except Course.DoesNotExist:
        messages.error(request, 'Kursus tidak ada.')
        return redirect('course_list')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('course_list')

    # Mengambil rekomendasi kursus berdasarkan similarity
    recommendations = get_course_recommendations(user)

    # Mengambil kursus yang telah diakses
    accessed_courses = get_accessed_courses(user)

    # Redirect ke halaman profil dengan daftar kursus yang telah diakses dan rekomendasi
    return render(request, 'profile/profile.html', {
        'course_title': course_title,
        'recommended_courses': recommendations,
        'accessed_courses': accessed_courses
    })


def get_course_recommendations(request, user):
    username = request.user.name

    query = """
    CALL gds.nodeSimilarity.stream('gds-sim')
    YIELD node1, node2, similarity
    WITH gds.util.asNode(node1) AS c1, gds.util.asNode(node2) AS c2, similarity

    MATCH (u:User {name: $username})-[:HAS_ACCESSED]->(c1)
    WITH DISTINCT c1, c2, similarity
    WHERE NOT c1.title = c2.title AND similarity >= 0.5
    OPTIONAL MATCH (c1)-[:IS_ABOUT]->(t:Topic)<-[:IS_ABOUT]-(c2)
    WITH DISTINCT c1, c2, similarity
    RETURN similarity, c2.title AS title, c2.url AS url, c2.image AS image, c2.price AS price, c2.platform AS platform
    ORDER BY similarity DESCENDING, c2.title
    """

    params = {'user_name': user.name}
    results, meta = db.cypher_query(query, params)
    
    recommendations = [
        {
            "similarity": record[0],
            "title": record[1],
            "url": record[2],
            "image": record[3] if record[3] else "https://blog.ecampuz.com/wp-content/uploads/2020/05/tips-kursus-online-ecampuz.jpg",
            "price": record[4] if record[4] else "Rp. 0",
            "platform": record[5] if record[5] else "Unknown"
        }
        for record in results
    ]

    return recommendations

def get_accessed_courses(user):
    query = """
    MATCH (u:User {name: $user_name})-[:HAS_ACCESSED]->(c:Course)
    RETURN c.title AS title, c.url AS url
    ORDER BY c.title
    """

    params = {'user_name': user.name}
    results, meta = db.cypher_query(query, params)
    
    accessed_courses = [
        {
            "title": record[0],
            "url": record[1]
        }
        for record in results
    ]

    return accessed_courses

@login_required
def access_course(request, course_id):
    try:
        user = User.nodes.get(userId=str(request.session.user_id))
        
        # Ambil kursus yang akan diakses
        course = Course.nodes.get(courseId=course_id)
        
        # Hubungkan pengguna dengan kursus
        user.has_accessed.connect(course, {'date_accessed': timezone.now()})
        
        # Ambil URL kursus dan lemparkan pengguna ke URL tersebut
        return redirect(course.url)
    except User.DoesNotExist:
        messages.error(request, 'Pengguna tidak ada.')
        return redirect('login')
    except Course.DoesNotExist:
        messages.error(request, 'Kursus tidak ada.')
        return redirect('course_list')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('course_list')