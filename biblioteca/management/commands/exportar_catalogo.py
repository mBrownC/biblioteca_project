from pathlib import Path

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand

from biblioteca.models import Autor, Editorial, Genero, Libro, Revista, Tag


class Command(BaseCommand):
    help = (
        'Exporta un respaldo del catalogo para alumnos '
        '(generos, autores, tags, editoriales, libros y revistas), '
        'sin usuarios ni prestamos.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='fixtures/catalogo_alumnos.json',
            help='Ruta relativa o absoluta del archivo JSON a generar.',
        )

    def handle(self, *args, **options):
        output = Path(options['output'])
        if not output.is_absolute():
            output = Path(settings.BASE_DIR) / output

        output.parent.mkdir(parents=True, exist_ok=True)

        objetos = [
            *Genero.objects.order_by('id'),
            *Autor.objects.order_by('id'),
            *Tag.objects.order_by('id'),
            *Editorial.objects.order_by('id'),
            *Libro.objects.order_by('id'),
            *Revista.objects.order_by('id'),
        ]

        data = serializers.serialize('json', objetos, indent=2)
        output.write_text(data, encoding='utf-8')

        self.stdout.write(
            self.style.SUCCESS(
                f'Respaldo exportado en: {output}'
            )
        )
        self.stdout.write(
            'Modelos incluidos: Genero, Autor, Tag, Editorial, Libro y Revista.'
        )
        self.stdout.write(
            'Modelos excluidos: CustomUser y Prestamo.'
        )
