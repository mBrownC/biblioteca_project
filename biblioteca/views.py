from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Genero, Libro, Prestamo, Revista


def lista_libros(request):
    libros = Libro.objects.select_related('autor', 'genero').all()
    revistas = Revista.objects.select_related('editorial_fk').all()
    generos = Genero.objects.all()

    genero_id = request.GET.get('genero')
    if genero_id:
        libros = libros.filter(genero__id=genero_id)

    busqueda = request.GET.get('q')
    if busqueda:
        libros = libros.filter(
            Q(titulo__icontains=busqueda)
            | Q(autor__nombre__icontains=busqueda)
            | Q(autor__apellido__icontains=busqueda)
        )
        revistas = revistas.filter(
            Q(titulo__icontains=busqueda)
            | Q(editorial__icontains=busqueda)
            | Q(editorial_fk__nombre__icontains=busqueda)
        )

    autor_busq = request.GET.get('autor')
    if autor_busq:
        libros = libros.filter(
            Q(autor__nombre__icontains=autor_busq)
            | Q(autor__apellido__icontains=autor_busq)
        )

    return render(request, 'biblioteca/lista_libros.html', {
        'libros': libros,
        'revistas': revistas,
        'generos': generos,
        'busqueda': busqueda or '',
        'genero_id': genero_id or '',
        'autor_busq': autor_busq or '',
    })


def detalle_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    return render(request, 'biblioteca/detalle_libro.html', {'libro': libro})


def detalle_revista(request, pk):
    revista = get_object_or_404(Revista, pk=pk)
    return render(request, 'biblioteca/detalle_revista.html', {'revista': revista})


@login_required
def solicitar_prestamo(request, pk):
    libro = get_object_or_404(Libro, pk=pk)

    if not libro.disponible():
        messages.error(request, 'Este libro no tiene stock disponible.')
        return redirect('detalle_libro', pk=pk)

    prestamo_activo = Prestamo.objects.filter(
        socio=request.user,
        libro=libro,
        devuelto=False,
    ).exists()

    if prestamo_activo:
        messages.warning(request, 'Ya tienes este libro en préstamo.')
        return redirect('detalle_libro', pk=pk)

    if request.method == 'POST':
        Prestamo.objects.create(socio=request.user, libro=libro)
        libro.stock -= 1
        libro.save()
        messages.success(request, f'Préstamo de "{libro.titulo}" registrado correctamente.')
        return redirect('mis_prestamos')

    return render(request, 'biblioteca/confirmar_prestamo.html', {
        'item': libro,
        'tipo': 'libro',
        'cancel_url': 'detalle_libro',
    })


@login_required
def solicitar_prestamo_revista(request, pk):
    revista = get_object_or_404(Revista, pk=pk)

    if not revista.disponible:
        messages.error(request, 'Esta revista no está disponible para préstamo.')
        return redirect('detalle_revista', pk=pk)

    prestamo_activo = Prestamo.objects.filter(
        socio=request.user,
        revista=revista,
        devuelto=False,
    ).exists()

    if prestamo_activo:
        messages.warning(request, 'Ya tienes esta revista en préstamo.')
        return redirect('detalle_revista', pk=pk)

    if request.method == 'POST':
        Prestamo.objects.create(socio=request.user, revista=revista)
        revista.disponible = False
        revista.save()
        messages.success(request, f'Préstamo de "{revista.titulo}" registrado correctamente.')
        return redirect('mis_prestamos')

    return render(request, 'biblioteca/confirmar_prestamo.html', {
        'item': revista,
        'tipo': 'revista',
        'cancel_url': 'detalle_revista',
    })


@login_required
def mis_prestamos(request):
    prestamos = Prestamo.objects.filter(
        socio=request.user,
    ).select_related('libro', 'libro__autor', 'revista', 'revista__editorial_fk').order_by('-fecha_prestamo')
    return render(request, 'biblioteca/mis_prestamos.html', {'prestamos': prestamos})


@login_required
def devolver_libro(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk, socio=request.user)

    if prestamo.devuelto:
        messages.info(request, 'Este préstamo ya fue devuelto.')
        return redirect('mis_prestamos')

    if request.method == 'POST':
        from django.utils import timezone

        prestamo.devuelto = True
        prestamo.fecha_devolucion = timezone.now().date()
        prestamo.save()

        if prestamo.libro:
            prestamo.libro.stock += 1
            prestamo.libro.save()
            messages.success(request, f'"{prestamo.libro.titulo}" devuelto correctamente.')
        elif prestamo.revista:
            prestamo.revista.disponible = True
            prestamo.revista.save()
            messages.success(request, f'"{prestamo.revista.titulo}" devuelta correctamente.')

        return redirect('mis_prestamos')

    return render(request, 'biblioteca/confirmar_devolucion.html', {'prestamo': prestamo})


@login_required
@permission_required('biblioteca.view_prestamo', raise_exception=True)
def panel_bibliotecario(request):
    prestamos_activos = Prestamo.objects.filter(
        devuelto=False,
    ).select_related('socio', 'libro', 'libro__autor', 'revista', 'revista__editorial_fk').order_by('-fecha_prestamo')

    total_libros = Libro.objects.count()
    total_prestamos = Prestamo.objects.count()
    prestamos_pendientes = prestamos_activos.count()

    return render(request, 'biblioteca/panel_bibliotecario.html', {
        'prestamos_activos': prestamos_activos,
        'total_libros': total_libros,
        'total_prestamos': total_prestamos,
        'prestamos_pendientes': prestamos_pendientes,
    })
