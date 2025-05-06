from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (UsuarioViewSet, CategoriaViewSet, ProductoViewSet, ServicioViewSet, 
                    WishlistViewSet, CarritoViewSet, ItemCarritoViewSet, PedidoViewSet, 
                    DetallePedidoViewSet)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'servicios', ServicioViewSet)
router.register(r'wishlist', WishlistViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'items-carrito', ItemCarritoViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'detalles-pedido', DetallePedidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
