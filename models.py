from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CategoriaProducto(models.Model):
    nombre_categoria = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categorias_producto'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'

    def __str__(self):
        return self.nombre_categoria


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255, null=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=255, null=False)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, db_column='id_categoria')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, db_column='id_proveedor')

    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['nombre'], name='idx_producto_nombre'),
        ]

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    apellido = models.CharField(max_length=100, null=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Carrito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, db_column='id_cliente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'carritos'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        indexes = [
            models.Index(fields=['id_cliente'], name='idx_carritos_cliente'),
        ]

    def __str__(self):
        return f"Carrito {self.id} - Cliente: {self.cliente}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, db_column='id_carrito')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, db_column='id_producto')
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_al_momento = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta:
        db_table = 'items_carrito'
        verbose_name = 'Ítem de Carrito'
        verbose_name_plural = 'Ítems de Carrito'
        unique_together = ('carrito', 'producto')
        indexes = [
            models.Index(fields=['id_carrito'], name='idx_items_carrito_carrito'),
            models.Index(fields=['id_producto'], name='idx_items_carrito_producto'),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, db_column='id_cliente')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    estatus = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')

    class Meta:
        db_table = 'pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        indexes = [
            models.Index(fields=['id_cliente'], name='idx_pedido_cliente'),
            models.Index(fields=['fecha'], name='idx_pedido_fecha'),
        ]

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente} - {self.estatus}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='id_pedido')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, db_column='id_producto')
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_pedido'
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.id}"


class Venta(models.Model):
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.SET_NULL, null=True, db_column='id_pedido', blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, db_column='id_cliente')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO_CHOICES)

    class Meta:
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['id_cliente'], name='idx_venta_cliente'),
            models.Index(fields=['id_pedido'], name='idx_venta_pedido'),
            models.Index(fields=['fecha_venta'], name='idx_venta_fecha'),
        ]

    def __str__(self):
        return f"Venta {self.id} - {self.cliente} - {self.total_venta}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_venta')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, db_column='id_producto')
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta {self.venta.id}"
