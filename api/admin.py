from django.contrib import admin
from .models import Usuario, Categoria, Producto, Servicio, Wishlist, Carrito, ItemCarrito, Pedido, DetallePedido, Estancia

admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Servicio)
admin.site.register(Estancia)
admin.site.register(Wishlist)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
