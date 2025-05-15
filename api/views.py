from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Categoria, Producto, Servicio, Wishlist, Carrito, ItemCarrito, Pedido, DetallePedido, Estancia
from .serializers import (UsuarioSerializer, CategoriaSerializer, ProductoSerializer, ServicioSerializer, 
                          WishlistSerializer, CarritoSerializer, ItemCarritoSerializer, PedidoSerializer, 
                          DetallePedidoSerializer, RegistroSerializer, LoginSerializer, EstanciaSerializer,
                          ActualizarUsuarioSerializer)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    @action(detail=False, methods=['post'], url_path='registro')
    def registro(self, request):
        """Registrar un nuevo usuario"""
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(usuario)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'usuario': UsuarioSerializer(usuario).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """Login de usuario"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            contraseña = serializer.validated_data['contraseña']
            
            try:
                usuario = Usuario.objects.get(email=email)
                if usuario.check_password(contraseña):
                    #tokens JWT
                    refresh = RefreshToken.for_user(usuario)
                    
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'usuario': UsuarioSerializer(usuario).data
                    })
                else:
                    return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
            except Usuario.DoesNotExist:
                return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['put'], url_path='actualizar')
    def actualizar_usuario(self, request, pk=None):
        """Actualizar datos del usuario"""
        usuario = self.get_object()
        serializer = ActualizarUsuarioSerializer(usuario, data=request.data, partial=True)
        
        if serializer.is_valid():
            usuario_actualizado = serializer.save()
            return Response({
                'usuario': UsuarioSerializer(usuario_actualizado).data,
                'mensaje': 'Datos actualizados correctamente'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    
    def get_queryset(self):
        """Permite filtrar categorías por nombre."""
        queryset = Categoria.objects.all()
        nombre = self.request.query_params.get('nombre', None)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        return queryset
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Obtener todos los productos de una categoría específica."""
        categoria = self.get_object()
        productos = Producto.objects.filter(categoria=categoria)
        serializer = ProductoSerializer(productos, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def con_productos(self, request):
        """Obtener solo categorías que tienen productos asociados."""
        categorias_con_productos = Categoria.objects.filter(productos__isnull=False).distinct()
        serializer = self.get_serializer(categorias_con_productos, many=True)
        return Response(serializer.data)

class EstanciaViewSet(viewsets.ModelViewSet):
    queryset = Estancia.objects.all()
    serializer_class = EstanciaSerializer
    
    def get_queryset(self):
        """Permite filtrar estancias por nombre."""
        queryset = Estancia.objects.all()
        nombre = self.request.query_params.get('nombre', None)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        return queryset
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Obtener todos los productos de una estancia específica."""
        estancia = self.get_object()
        productos = Producto.objects.filter(estancia=estancia)
        serializer = ProductoSerializer(productos, many=True, context={'request': request})
        return Response(serializer.data)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_serializer_context(self):
        """Añade el request al contexto del serializer."""
        context = super().get_serializer_context()
        return context
    
    def get_queryset(self):
        """Permite filtrar productos por nombre y asegura que se incluyan los datos relacionados."""
        queryset = Producto.objects.all().select_related('categoria', 'estancia')
        nombre = self.request.query_params.get('nombre', None)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crea un nuevo producto con validación mejorada."""
        if 'imagen' not in request.data or not request.data.get('imagen'):
            return Response(
                {"error": "Se requiere una URL de imagen para el producto"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().create(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        """Actualiza un producto existente."""
        instance = self.get_object()
        
        # Si no se proporciona una nueva URL de imagen, mantener la existente
        if 'imagen' not in request.data and instance.imagen:
            request.data._mutable = True
            request.data['imagen'] = instance.imagen
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
    
    @action(detail=False, methods=['get'], url_path='por-estancia/(?P<estancia_id>[^/.]+)')
    def por_estancia(self, request, estancia_id=None):
        """Obtener productos por estancia"""
        productos = Producto.objects.filter(estancia_id=estancia_id)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='buscar/(?P<texto>[^/.]+)')
    def buscar(self, request, texto=None):
        """Buscar productos por nombre o descripción"""
        productos = Producto.objects.filter(nombre__icontains=texto) | Producto.objects.filter(descripcion__icontains=texto)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='destacados')
    def destacados(self, request):
        """Obtener productos destacados (los más recientes)"""
        productos_destacados = Producto.objects.all().order_by('-fecha_creacion')[:8]
        serializer = self.get_serializer(productos_destacados, many=True)
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
