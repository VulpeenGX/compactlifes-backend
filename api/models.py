from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
import json  # Añadir esta importación

class Usuario(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    apellido = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    contraseña = models.CharField(max_length=100, null=False, blank=False)
    direccion = models.TextField(null=False, blank=False)
    telefono = models.CharField(max_length=9, null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def save(self, *args, **kwargs):
        # Hash de la contraseña solo si no está hasheada
        if self.contraseña and not self.contraseña.startswith('pbkdf2_sha256$'):
            self.contraseña = make_password(self.contraseña)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        """Verifica si la contraseña sin procesar coincide con la contraseña hasheada."""
        return check_password(raw_password, self.contraseña)

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.nombre

class Estancia(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)  
    descuento = models.PositiveIntegerField(default=0)  
    stock = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    estancia = models.ForeignKey(Estancia, on_delete=models.CASCADE, related_name='productos', null=True)
    imagen = models.URLField(max_length=500)
    colores = models.JSONField(default=list)
    materiales = models.JSONField(default=list)
    peso = models.FloatField(null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    @property
    def precio_con_descuento(self):
        """Calcula el precio final aplicando el descuento."""
        return self.precio * (Decimal('1') - Decimal(self.descuento) / Decimal('100'))
    
    @property
    def colores_formateados(self):
        try:
            data = self.colores
            if isinstance(data, list):
                return ", ".join(
                    item["color"] if isinstance(item, dict) and "color" in item else str(item)
                    for item in data
                )
            elif isinstance(data, dict):
                return ", ".join(str(v) for v in data.values())
            else:
                return str(data)
        except Exception:
            return str(self.colores)
        
    @property
    def materiales_formateados(self):
        try:
            data = self.materiales
            if isinstance(data, list):
                return ", ".join(
                    item["material"] if isinstance(item, dict) and "material" in item else str(item)
                    for item in data
                )
            elif isinstance(data, dict):
                return ", ".join(str(v) for v in data.values())
            else:
                return str(data)
        except Exception:
            return str(self.materiales)

class Servicio(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.nombre

class Wishlist(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='wishlist')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_añadido = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"Wishlist de {self.usuario.nombre} - {self.producto.nombre}"

class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carritos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1, null=False, blank=False)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en carrito {self.carrito.id}"

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    direccion_envio = models.TextField(null=False, blank=False)
    metodo_pago = models.CharField(max_length=50, null=False, blank=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f'Pedido {self.id} - {self.usuario.nombre} - {self.estado}'

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(null=False, blank=False)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en pedido {self.pedido.id}"
