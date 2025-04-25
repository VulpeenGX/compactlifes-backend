from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Usuario, Categoria, Producto, Servicio, Wishlist, Carrito, ItemCarrito, Pedido, DetallePedido
from .serializers import (UsuarioSerializer, CategoriaSerializer, ProductoSerializer, ServicioSerializer, 
                          WishlistSerializer, CarritoSerializer, ItemCarritoSerializer, PedidoSerializer, 
                          DetallePedidoSerializer)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_serializer_context(self):
        """Añade el request al contexto del serializer."""
        context = super().get_serializer_context()
        return context
    
    def create(self, request, *args, **kwargs):
        """Crea un nuevo producto con validación mejorada."""
        # Verificar si se ha proporcionado una imagen
        if 'imagen' not in request.FILES:
            return Response(
                {"error": "Se requiere una imagen para el producto"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().create(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        """Actualiza un producto existente."""
        instance = self.get_object()
        
        # Si no se proporciona una nueva imagen, mantener la existente
        if 'imagen' not in request.FILES and instance.imagen:
            request.data._mutable = True
            request.data.pop('imagen', None)
            request.data._mutable = False
            
        return super().update(request, *args, **kwargs)
        
    @action(detail=False, methods=['get'], url_path='ofertas')
    def ofertas(self, request):
        """Obtener productos con descuento mayor a 0"""
        productos_con_descuento = Producto.objects.filter(descuento__gt=0)
        serializer = self.get_serializer(productos_con_descuento, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='sin-ofertas')
    def sin_ofertas(self, request):
        """Obtener productos sin descuento (descuento = 0)"""
        productos_sin_descuento = Producto.objects.filter(descuento=0)
        serializer = self.get_serializer(productos_sin_descuento, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='por-categoria/(?P<categoria_id>[^/.]+)')
    def por_categoria(self, request, categoria_id=None):
        """Obtener productos por categoría"""
        productos = Producto.objects.filter(categoria_id=categoria_id)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

class ItemCarritoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrito.objects.all()
    serializer_class = ItemCarritoSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
