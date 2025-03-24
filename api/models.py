from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=9)
    fecha_creacion = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    imagenes = models.JSONField(default=list)  # Guarda una lista de URLs de imágenes
    colores = models.JSONField(default=list)   # Lista de colores
    materiales = models.JSONField(default=list)  # Lista de materiales
    peso = models.FloatField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    productos = models.JSONField(default=list)  # Lista de productos con cantidad y precio
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Pedido {self.id} - {self.usuario.nombre} - {self.estado}'
