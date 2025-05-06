from rest_framework import serializers
from .models import Usuario, Categoria, Producto, Servicio, Wishlist, Carrito, ItemCarrito, Pedido, DetallePedido
from decimal import Decimal
from django.contrib.auth.hashers import make_password

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {'contraseña': {'write_only': True}}

class RegistroSerializer(serializers.ModelSerializer):
    confirmar_contraseña = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'contraseña', 'confirmar_contraseña', 'direccion', 'telefono']
        extra_kwargs = {
            'contraseña': {'write_only': True},
        }
    
    def validate(self, data):
        # Verificar que las contraseñas coincidan
        if data.get('contraseña') != data.pop('confirmar_contraseña'):
            raise serializers.ValidationError({"error": "Las contraseñas no coinciden"})
        return data
    
    def create(self, validated_data):
        # Crear el usuario con la contraseña hasheada
        usuario = Usuario.objects.create(**validated_data)
        return usuario

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    contraseña = serializers.CharField(required=True, write_only=True)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    precio_con_descuento = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()  # Campo adicional para compatibilidad
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'descuento', 
                  'precio_con_descuento', 'stock', 'categoria', 'categoria_nombre', 'imagen', 
                  'imagen_url', 'colores', 'materiales', 'peso', 'fecha_creacion']
        extra_kwargs = {
            'imagen': {'required': True},
        }

    def get_precio_con_descuento(self, obj):
        """Calcula el precio con descuento directamente en el serializer."""
        return obj.precio * (Decimal('1') - Decimal(obj.descuento) / Decimal('100'))
        
    def get_imagen_url(self, obj):
        """Devuelve la URL completa de la imagen."""
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
        
    def validate_colores(self, value):
        """Valida que los colores sean una lista."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Los colores deben ser una lista")
        return value
        
    def validate_materiales(self, value):
        """Valida que los materiales sean una lista."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Los materiales deben ser una lista")
        return value

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = '__all__'

class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'