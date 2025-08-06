# proyecto-ferreteria-django
ferreteria
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

# --- Categoría de Productos ---
class CategoriaProducto(models.Model):
    nombre_categoria = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de Categoría"
    )

    class Meta:
        db_table = 'categorias_producto'
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"

    def __str__(self):
        return self.nombre_categoria


# --- Proveedor ---
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Proveedor")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="Email")

    class Meta:
        db_table = 'proveedor'
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


# --- Producto ---
class Producto(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio de Venta"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del Producto")
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )

    class Meta:
        db_table = 'producto'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['nombre'], name='idx_producto_nombre'),
            models.Index(fields=['categoria']),
            models.Index(fields=['proveedor']),
        ]

    def __str__(self):
        return self.nombre


# --- Cliente ---
class Cliente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="Email")

    class Meta:
        db_table = 'cliente'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# --- Carrito de Compras ---
class Carrito(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente Asociado"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = 'carritos'
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"
        indexes = [
            models.Index(fields=['cliente'], name='idx_carritos_cliente'),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"Carrito #{self.id} - {self.cliente or 'Invitado'}"


# --- Ítem del Carrito ---
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, verbose_name="Carrito")
    producto = models.ForeignKey(
        Producto,
        on_delete=models.RESTRICT,
        verbose_name="Producto"
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    precio_al_momento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio al Momento"
    )

    class Meta:
        db_table = 'items_carrito'
        verbose_name = "Ítem del Carrito"
        verbose_name_plural = "Ítems del Carrito"
        unique_together = ('carrito', 'producto')
        indexes = [
            models.Index(fields=['carrito'], name='idx_items_carrito_carrito'),
            models.Index(fields=['producto'], name='idx_items_carrito_producto'),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_al_momento

    def save(self, *args, **kwargs):
        # Guardar el precio actual del producto al momento de agregar
        if not self.precio_al_momento:
            self.precio_al_momento = self.producto.precio
        super().save(*args, **kwargs)


# --- Pedido ---
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, verbose_name="Cliente")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Pedido")
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total del Pedido"
    )
    estatus = models.CharField(
        max_length=50,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estatus del Pedido"
    )

    class Meta:
        db_table = 'pedido'
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        indexes = [
            models.Index(fields=['cliente'], name='idx_pedido_cliente'),
            models.Index(fields=['fecha'], name='idx_pedido_fecha'),
            models.Index(fields=['estatus']),
        ]

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} ({self.estatus})"


# --- Detalle de Pedido ---
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, verbose_name="Pedido")
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Subtotal"
    )

    class Meta:
        db_table = 'detalle_pedido'
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"
        unique_together = ('pedido', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Pedido #{self.pedido.id})"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


# --- Venta ---
class Venta(models.Model):
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    ]

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pedido Relacionado"
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, verbose_name="Cliente")
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Venta")
    total_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total de Venta"
    )
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO_CHOICES, verbose_name="Tipo de Pago")

    class Meta:
        db_table = 'venta'
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        indexes = [
            models.Index(fields=['cliente'], name='idx_venta_cliente'),
            models.Index(fields=['pedido'], name='idx_venta_pedido'),
            models.Index(fields=['fecha_venta'], name='idx_venta_fecha'),
        ]

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente} - ${self.total_venta}"


# --- Detalle de Venta ---
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, verbose_name="Venta")
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Subtotal"
    )

    class Meta:
        db_table = 'detalle_venta'
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        unique_together = ('venta', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Venta #{self.venta.id})"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
