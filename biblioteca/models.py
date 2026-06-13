from django.db import models
from django.conf import settings


class Genero(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'Géneros'


class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Tag(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self): return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='libros')
    anio = models.IntegerField(verbose_name='Año de publicación')
    stock = models.IntegerField(default=1)
    descripcion = models.TextField(blank=True)
    publication_date = models.DateField(null=False)
    paginas = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    def disponible(self):
        return self.stock > 0


class Editorial(models.Model):
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    anio_fundacion = models.IntegerField()
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural = 'Editoriales'

class Revista(models.Model):
    titulo = models.CharField(max_length=200)
    editorial = models.CharField(max_length=100)
    numero_edicion = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_publicacion = models.DateField()
    disponible = models.BooleanField(default=True)
    notas = models.TextField(blank=True)
    editorial_fk = models.ForeignKey(Editorial, on_delete=models.SET_NULL, null=True, blank=True)
    paginas = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='revistas')
    def __str__(self):
        return self.titulo

class Prestamo(models.Model):
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, null=True, blank=True)
    revista = models.ForeignKey(Revista, on_delete=models.CASCADE, null=True, blank=True)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        item = self.libro or self.revista
        return f"{self.socio.username} - {item.titulo if item else 'Sin item'}"

    class Meta:
        ordering = ['-fecha_prestamo']
