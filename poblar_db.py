"""
Script para poblar la base de datos de la Biblioteca
Ejecutar con: python manage.py shell < poblar_db.py
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from biblioteca.models import Genero, Autor, Libro, Prestamo

print("🔧 Creando grupos y permisos...")

# Permisos de biblioteca
ct_prestamo = ContentType.objects.get_for_model(Prestamo)
ct_libro = ContentType.objects.get_for_model(Libro)

perm_add_prestamo = Permission.objects.get(content_type=ct_prestamo, codename='add_prestamo')
perm_view_prestamo = Permission.objects.get(content_type=ct_prestamo, codename='view_prestamo')
perm_change_prestamo = Permission.objects.get(content_type=ct_prestamo, codename='change_prestamo')
perm_delete_prestamo = Permission.objects.get(content_type=ct_prestamo, codename='delete_prestamo')
perm_view_libro = Permission.objects.get(content_type=ct_libro, codename='view_libro')

# Grupo socio
grupo_socio, _ = Group.objects.get_or_create(name='socio')
grupo_socio.permissions.set([perm_add_prestamo, perm_view_prestamo])
print("  ✅ Grupo 'socio' creado")

# Grupo bibliotecario
grupo_biblio, _ = Group.objects.get_or_create(name='bibliotecario')
grupo_biblio.permissions.set([
    perm_add_prestamo,
    perm_view_prestamo,
    perm_change_prestamo,
    perm_delete_prestamo,
    perm_view_libro,
])
print("  ✅ Grupo 'bibliotecario' creado")

print("\n📚 Creando géneros...")
generos_data = [
    'Novela', 'Ciencia Ficción', 'Historia', 'Poesía',
    'Terror', 'Filosofía', 'Biografía', 'Fantasía'
]
generos = {}
for nombre in generos_data:
    g, _ = Genero.objects.get_or_create(nombre=nombre)
    generos[nombre] = g
    print(f"  ✅ {nombre}")

print("\n✍️  Creando autores...")
autores_data = [
    ('Gabriel', 'García Márquez', 'Colombiana'),
    ('Isabel', 'Allende', 'Chilena'),
    ('Pablo', 'Neruda', 'Chilena'),
    ('Jorge Luis', 'Borges', 'Argentina'),
    ('Mario', 'Vargas Llosa', 'Peruana'),
    ('Julio', 'Cortázar', 'Argentina'),
    ('Stephen', 'King', 'Estadounidense'),
    ('George', 'Orwell', 'Británica'),
    ('Franz', 'Kafka', 'Checa'),
    ('Fyodor', 'Dostoevsky', 'Rusa'),
]
autores = {}
for nombre, apellido, nacionalidad in autores_data:
    a, _ = Autor.objects.get_or_create(
        nombre=nombre, apellido=apellido,
        defaults={'nacionalidad': nacionalidad}
    )
    autores[apellido] = a
    print(f"  ✅ {nombre} {apellido}")

print("\n📖 Creando libros...")
libros_data = [
    ('Cien años de soledad', 'García Márquez', 'Novela', 1967, 3,
     'La historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo.'),
    ('La casa de los espíritus', 'Allende', 'Novela', 1982, 2,
     'Saga familiar que abarca cuatro generaciones de la familia Trueba en Chile.'),
    ('Veinte poemas de amor', 'Neruda', 'Poesía', 1924, 5,
     'Colección de poemas de amor del poeta chileno Pablo Neruda.'),
    ('Ficciones', 'Borges', 'Novela', 1944, 2,
     'Colección de cuentos que exploran laberintos, bibliotecas infinitas y paradojas del tiempo.'),
    ('La ciudad y los perros', 'Vargas Llosa', 'Novela', 1963, 3,
     'Novela ambientada en el Colegio Militar Leoncio Prado de Lima, Perú.'),
    ('Rayuela', 'Cortázar', 'Novela', 1963, 2,
     'Novela experimental que puede leerse en múltiples órdenes según instrucciones del autor.'),
    ('El resplandor', 'King', 'Terror', 1977, 4,
     'Un escritor acepta cuidar un hotel durante el invierno con su familia, con consecuencias aterradoras.'),
    ('1984', 'Orwell', 'Ciencia Ficción', 1949, 3,
     'Novela distópica sobre un régimen totalitario que controla todos los aspectos de la vida.'),
    ('La metamorfosis', 'Kafka', 'Novela', 1915, 4,
     'Gregor Samsa se despierta convertido en un insecto gigante y debe enfrentarse a su nueva realidad.'),
    ('Crimen y castigo', 'Dostoevsky', 'Novela', 1866, 2,
     'Un estudiante planea y ejecuta un crimen y debe lidiar con las consecuencias psicológicas.'),
    ('El otoño del patriarca', 'García Márquez', 'Novela', 1975, 1,
     'Retrato de un dictador latinoamericano que ha gobernado por más de cien años.'),
    ('Eva Luna', 'Allende', 'Novela', 1987, 3,
     'Historia de una mujer que narra su propia vida con el mismo poder con el que crea sus cuentos.'),
    ('Canto general', 'Neruda', 'Poesía', 1950, 2,
     'Poema épico que abarca la historia y geografía de América Latina.'),
    ('El Aleph', 'Borges', 'Fantasía', 1949, 3,
     'Colección de cuentos donde se incluye la famosa historia del punto que contiene todos los puntos.'),
    ('It', 'King', 'Terror', 1986, 2,
     'Un grupo de niños enfrenta a una entidad maligna que adopta la forma de sus peores miedos.'),
]

for titulo, apellido_autor, genero_nombre, anio, stock, descripcion in libros_data:
    autor = autores[apellido_autor]
    genero = generos[genero_nombre]
    libro, created = Libro.objects.get_or_create(
        titulo=titulo,
        defaults={
            'autor': autor,
            'genero': genero,
            'anio': anio,
            'stock': stock,
            'descripcion': descripcion,
        }
    )
    estado = "✅ creado" if created else "⚠️  ya existe"
    print(f"  {estado}: {titulo}")

print(f"\n{'='*50}")
print(f"✅ Base de datos poblada correctamente")
print(f"   Géneros:  {Genero.objects.count()}")
print(f"   Autores:  {Autor.objects.count()}")
print(f"   Libros:   {Libro.objects.count()}")
print(f"   Grupos:   {Group.objects.count()}")
print(f"{'='*50}")
print("\n👉 Próximo paso: crear usuarios de prueba desde /admin/")
print("   - Un socio (grupo: socio)")
print("   - Un bibliotecario (grupo: bibliotecario, is_staff=True)")
