from rest_framework import serializers
from .models import Usuario, Categoria, Producto, Servicio, Wishlist, Carrito, ItemCarrito, Pedido, DetallePedido, Estancia
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

class ActualizarUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'direccion', 'telefono']
        
    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.direccion = validated_data.get('direccion', instance.direccion)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    contraseña = serializers.CharField(required=True, write_only=True)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class EstanciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estancia
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    precio_con_descuento = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    estancia_nombre = serializers.ReadOnlyField(source='estancia.nombre')
    categoria_data = CategoriaSerializer(source='categoria', read_only=True)
    estancia_data = EstanciaSerializer(source='estancia', read_only=True)
    colores_formateados = serializers.SerializerMethodField()
    materiales_formateados = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 
            'precio_con_descuento', 'stock', 'categoria', 'categoria_nombre', 
            'estancia', 'estancia_nombre', 'imagen', 'imagen_url', 
            'colores', 'materiales', 'peso', 'fecha_creacion',
            'categoria_data', 'estancia_data',
            'colores_formateados', 'materiales_formateados'
        ]
        extra_kwargs = {
            'imagen': {'required': True},
        }

    def get_precio_con_descuento(self, obj):
        return obj.precio * (Decimal('1') - Decimal(obj.descuento) / Decimal('100'))

    def get_imagen_url(self, obj):
        if obj.imagen:
            return obj.imagen
        return None

    def get_colores_formateados(self, obj):
        try:
            data = obj.colores
            if isinstance(data, str):
                import json
                data = json.loads(data)
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
            return str(obj.colores)

    def get_materiales_formateados(self, obj):
        try:
            data = obj.materiales
            if isinstance(data, str):
                import json
                data = json.loads(data)
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
            return str(obj.materiales)
        
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