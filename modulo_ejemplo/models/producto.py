from odoo import models, fields, api

class Producto(models.Model):
    # --------------------------------------
    # 1. Private attributes
    # --------------------------------------
    _name = "mi.producto"  # Nombre técnico del modelo
    _description = "Modelo de ejemplo completo siguiendo guidelines"  # Descripción legible
    _inherit = []  # Herencia de otros modelos (vacío en este ejemplo)
    _order = "nombre asc"  # Orden por defecto al listar registros
    _sql_constraints = [
        ('nombre_uniq', 'unique(nombre)', 'El nombre del producto debe ser único')  # Restricción SQL
    ]

    # --------------------------------------
    # 2. Default methods / default_get
    # --------------------------------------
    @api.model
    def _default_precio_unitario(self):
        """Método que devuelve el precio unitario por defecto"""
        return 10.0

    @api.model
    def default_get(self, fields_list):
        """
        Sobrescribe default_get para establecer valores por defecto adicionales
        cuando se crea un nuevo registro desde la interfaz.
        """
        defaults = super().default_get(fields_list)
        defaults['cantidad'] = 1
        return defaults

    # --------------------------------------
    # 3. Field declarations
    # --------------------------------------
    nombre = fields.Char(string="Nombre", required=True)  # Campo obligatorio de texto
    descripcion = fields.Text(string="Descripción")  # Campo de texto largo
    precio_unitario = fields.Float(
        string="Precio unitario",
        default=_default_precio_unitario  # Valor por defecto mediante método
    )
    cantidad = fields.Integer(string="Cantidad", default=1)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")  # Campo computado
    iva = fields.Float(string="IVA (%)", default=21)  # Valor por defecto
    total = fields.Float(string="Total", compute="_compute_total")  # Campo computado
    activo = fields.Boolean(string="Activo", default=True)
    categoria_id = fields.Many2one("mi.categoria", string="Categoría")  # Relación Many2one
    tipo = fields.Selection(
        [('fisico', 'Físico'), ('digital', 'Digital')],
        string="Tipo",
        default='fisico'
    )

    # --------------------------------------
    # 4. Compute, inverse, search methods (in order of field declaration)
    # --------------------------------------
    @api.depends("precio_unitario", "cantidad")
    def _compute_subtotal(self):
        """Calcula subtotal = precio_unitario * cantidad"""
        for record in self:
            record.subtotal = record.precio_unitario * record.cantidad

    @api.depends("subtotal", "iva")
    def _compute_total(self):
        """Calcula total = subtotal + IVA"""
        for record in self:
            record.total = record.subtotal * (1 + record.iva / 100)

    # --------------------------------------
    # 5. Selection methods
    # --------------------------------------
    @api.model
    def _get_tipos(self):
        """Devuelve las opciones de selección del campo 'tipo'"""
        return [('fisico', 'Físico'), ('digital', 'Digital')]

    # --------------------------------------
    # 6. Constrains and onchange methods
    # --------------------------------------
    @api.constrains("precio_unitario", "cantidad")
    def _check_valores(self):
        """
        Validación al guardar registros:
        - Precio unitario no puede ser negativo
        - Cantidad no puede ser negativa
        """
        for record in self:
            if record.precio_unitario < 0:
                raise ValueError("El precio unitario no puede ser negativo")
            if record.cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa")

    @api.onchange("precio_unitario", "cantidad")
    def _onchange_subtotal(self):
        """
        Recalcula el subtotal al cambiar precio o cantidad en el formulario.
        No se guarda en la base de datos hasta que se confirma.
        """
        if self.precio_unitario and self.cantidad:
            self.subtotal = self.precio_unitario * self.cantidad

    # --------------------------------------
    # 7. CRUD methods (ORM overrides)
    # --------------------------------------
    @api.model
    def create(self, vals):
        """
        Se sobrescribe create para añadir lógica al crear un registro.
        Se recomienda siempre llamar a super().
        """
        record = super().create(vals)
        # Aquí se podría añadir lógica adicional (notificaciones, logs, etc.)
        return record

    def write(self, vals):
        """
        Se sobrescribe write para añadir lógica al actualizar un registro.
        """
        res = super().write(vals)
        # Lógica adicional después de actualizar
        return res

    def unlink(self):
        """
        Se sobrescribe unlink para añadir lógica al eliminar un registro.
        """
        # Lógica antes de borrar, si es necesario
        return super().unlink()

    # --------------------------------------
    # 8. Action methods
    # --------------------------------------
    def action_marcar_inactivo(self):
        """Ejemplo de método que cambia el estado 'activo' a False"""
        for record in self:
            record.activo = False
        return True

    def action_abrir_wizard(self):
        """
        Ejemplo de método que devuelve una acción para abrir un wizard.
        """
        return {
            "type": "ir.actions.act_window",
            "res_model": "mi.modulo.wizard",
            "view_mode": "form",
            "target": "new",
        }

    # --------------------------------------
    # 9. Other business methods
    # --------------------------------------
    def duplicar_producto(self):
        """Método propio que duplica el registro"""
        for record in self:
            self.create({
                "nombre": record.nombre + " (Copia)",
                "descripcion": record.descripcion,
                "precio_unitario": record.precio_unitario,
                "cantidad": record.cantidad,
                "iva": record.iva,
                "activo": record.activo,
                "categoria_id": record.categoria_id.id,
                "tipo": record.tipo,
            })

    @api.model
    def productos_activos(self):
        """Devuelve todos los productos activos"""
        return self.search([("activo", "=", True)])
