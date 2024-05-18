from django.shortcuts import render
from .neo4j_connection import Neo4jConnection

def show_persons(request):
    conn = Neo4jConnection("bolt://cb7896fd.databases.neo4j.io:7687", "neo4j", "Sl-sbZMNY1p-6Gm08k6Eg5ZMrseubfURvhzdVsYDg4k")
    result = conn.query("MATCH (p:Person) RETURN p.name AS name, p.age AS age")
    persons = [{"name": record["name"], "age": record["age"]} for record in result]
    conn.close()
    return render(request, 'kursus/show_person.html', {'persons': persons})

def kursus_card(request):
    return render(request, 'kursus/kursus.html')

def pilih_role(request):
    context = {
        'range': range(1, 21)  # Adjust the range as needed
    }
    return render(request, 'kursus/pilih_role.html', context)

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'kursus/index.html')

def login(request):
    return render(request, 'kursus/login.html')

def registrasi(request):
    return render(request, 'kursus/registrasi.html')

def detail_kursus(request):
    return render(request, 'kursus/detail_kursus.html')

