# your_app/management/commands/update_degree.py

from django.core.management.base import BaseCommand
from neomodel import db

class Command(BaseCommand):
    help = 'Hitung ulang in-degree untuk properti degree pada semua node Course berdasarkan relasi HAS_ACCESSED dari User'

    def handle(self, *args, **kwargs):
        query = """
        MATCH (c:Course)
        OPTIONAL MATCH (c)<-[r:HAS_ACCESSED]-()
        WITH c, COUNT(r) as degree
        SET c.degree = degree
        RETURN c, degree
        ORDER BY degree DESC
        """
        db.cypher_query(query)
        self.stdout.write(self.style.SUCCESS('Berhasil menghitung ulang in-degree untuk semua node Course'))
