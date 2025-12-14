# empleados.py
# Gestión de empleados con overlays funcionales (adaptado a paleta blanca y Premium UI)

import flet as ft
import database
from diseño_premium import COLORS, PremiumButton, PremiumTextField

class EmpleadosView:
    def __init__(self, page, on_refresh_callback, on_lock_callback=None):
        self.page = page
        self.on_refresh = on_refresh_callback
        self.on_lock = on_lock_callback
        self.table = None
        self.empleado_editar_id = None
        self.empleado_eliminar_id = None
        self.build_ui()

    def build_ui(self):
        # Botón de bloquear vista
        def bloquear_vista(e):
            if self.on_lock:
                self.on_lock("empleados")

        self.btn_bloquear = PremiumButton(
            "🔒 Bloquear Vista",
            on_click=bloquear_vista,
            gradient=False,
            width=160,
        )

        # Inputs con estilo Premium
        self.nombre_input = PremiumTextField(
            label="Nombre completo",
            width=360,
        )
        self.cedula_input = PremiumTextField(
            label="Cédula",
            width=220,
        )
        self.numero_input = PremiumTextField(
            label="Teléfono",
            width=220,
        )

        self.btn_agregar = PremiumButton(
            "Agregar Empleado",
            icon=ft.Icons.PERSON_ADD,
            on_click=self.agregar_empleado,
            width=180,
        )

        # Tabla de empleados (DataTable)
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])),
                ft.DataColumn(ft.Text("Cédula", weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])),
            ],
            rows=[],
            border=ft.border.all(1, COLORS["glass_border"]),
            border_radius=10,
        )

        # OVERLAY DE EDICIÓN
        self.edit_nombre = PremiumTextField(label="Nombre", width=360)
        self.edit_cedula = PremiumTextField(label="Cédula", width=220)
        self.edit_numero = PremiumTextField(label="Teléfono", width=220)

        self.overlay_editar = ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Editar Empleado", size=22, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                        ft.Container(height=14),
                        self.edit_nombre,
                        self.edit_cedula,
                        self.edit_numero,
                        ft.Container(height=18),
                        ft.Row(
                            [
                                ft.TextButton("Cancelar", on_click=self.cerrar_overlay_editar),
                                PremiumButton(
                                    "Guardar Cambios",
                                    icon=ft.Icons.SAVE,
                                    on_click=self.guardar_edicion_overlay,
                                    width=160,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=12,
                ),
                bgcolor=COLORS["bg_card"],
                padding=24,
                border_radius=14,
                width=540,
                shadow=ft.BoxShadow(spread_radius=6, blur_radius=24, color="#00000022"),
            ),
            alignment=ft.Alignment(0, 0),
            bgcolor="#00000066",
            visible=False,
            expand=True,
        )

        # OVERLAY DE ELIMINACIÓN
        self.overlay_eliminar = ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.WARNING, size=56, color=COLORS["warning"]),
                        ft.Text("⚠️ Confirmar Eliminación", size=20, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                        ft.Container(height=8),
                        ft.Text(
                            "Se eliminarán también todos los registros de asistencia de este empleado.",
                            size=14,
                            color=COLORS["text_secondary"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=12),
                        ft.Row(
                            [
                                ft.TextButton("Cancelar", on_click=self.cerrar_overlay_eliminar),
                                PremiumButton(
                                    "SÍ, ELIMINAR",
                                    icon=ft.Icons.DELETE_FOREVER,
                                    on_click=self.eliminar_overlay,
                                    width=160,
                                    gradient=False,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                bgcolor=COLORS["bg_card"],
                padding=20,
                border_radius=14,
                width=480,
                shadow=ft.BoxShadow(spread_radius=6, blur_radius=24, color="#00000022"),
            ),
            alignment=ft.Alignment(0, 0),
            bgcolor="#00000066",
            visible=False,
            expand=True,
        )

        # Layout con tarjeta y SCROLL
        self.main_column = ft.Column(
            [
                # Encabezado con botón de bloqueo
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.PEOPLE, size=36, color=COLORS["accent_blue"]),
                                    ft.Text(
                                        "Gestión de Empleados",
                                        size=26,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLORS["text_primary"],
                                    ),
                                ],
                                spacing=12,
                            ),
                            self.btn_bloquear,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(bottom=18),
                ),

                # Formulario de registro
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Nuevo Empleado", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                            ft.Row(
                                [
                                    self.nombre_input,
                                    self.cedula_input,
                                    self.numero_input,
                                    self.btn_agregar,
                                ],
                                wrap=True,
                                spacing=12,
                            ),
                        ],
                        spacing=12,
                    ),
                    bgcolor=COLORS["bg_card"],
                    padding=18,
                    border_radius=12,
                    shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color="#00000010"),
                ),

                ft.Container(height=14),

                # Tabla de empleados
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Lista de Empleados", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                            ft.Container(content=self.table, padding=8),
                        ],
                        spacing=12,
                    ),
                    bgcolor=COLORS["bg_card"],
                    padding=18,
                    border_radius=12,
                    shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color="#00000010"),
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        )

        # Stack con overlays
        self.container = ft.Stack([self.main_column, self.overlay_editar, self.overlay_eliminar], expand=True)

        # Carga inicial
        self.cargar_tabla()

    def cargar_tabla(self, e=None):
        rows = []
        empleados = database.obtener_empleados()

        for emp in empleados:
            emp_id = emp["id"]

            # Crear botones con data
            btn_editar = ft.IconButton(
                icon=ft.Icons.EDIT,
                icon_color=COLORS["accent_blue"],
                tooltip="Editar",
                data=emp_id,
                on_click=self.click_editar,
            )

            btn_eliminar = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=COLORS["danger"],
                tooltip="Eliminar",
                data=emp_id,
                on_click=self.click_eliminar,
            )

            acciones = ft.Row([btn_editar, btn_eliminar], spacing=6)

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(emp_id), color=COLORS["text_primary"])),
                        ft.DataCell(ft.Text(emp["nombre"] or "", color=COLORS["text_primary"])),
                        ft.DataCell(ft.Text(emp["cedula"] or "", color=COLORS["text_primary"])),
                        ft.DataCell(ft.Text(emp["numero"] or "-", color=COLORS["text_secondary"])),
                        ft.DataCell(acciones),
                    ]
                )
            )

        self.table.rows = rows
        self.page.update()

    def click_editar(self, e):
        """Handler del click en botón editar."""
        emp_id = e.control.data

        emp = database.obtener_empleado_por_id(emp_id)
        if not emp:
            return

        # Guardar ID y llenar campos
        self.empleado_editar_id = emp_id
        self.edit_nombre.value = emp["nombre"]
        self.edit_cedula.value = emp["cedula"]
        self.edit_numero.value = emp["numero"]

        # Mostrar overlay
        self.overlay_editar.visible = True
        self.page.update()

    def cerrar_overlay_editar(self, e=None):
        self.overlay_editar.visible = False
        self.page.update()

    def guardar_edicion_overlay(self, e):
        """Guarda los cambios del overlay de edición."""
        database.actualizar_empleado(
            self.empleado_editar_id,
            self.edit_nombre.value,
            self.edit_cedula.value,
            self.edit_numero.value
        )

        self.overlay_editar.visible = False
        self.cargar_tabla()
        self.on_refresh()
        # mostrar snackbar
        self.page.snack_bar.content.value = "✓ Empleado actualizado"
        self.page.snack_bar.bgcolor = COLORS["success"]
        self.page.snack_bar.open = True
        self.page.update()

    def click_eliminar(self, e):
        """Handler del click en botón eliminar."""
        emp_id = e.control.data
        self.empleado_eliminar_id = emp_id
        self.overlay_eliminar.visible = True
        self.page.update()

    def cerrar_overlay_eliminar(self, e=None):
        self.overlay_eliminar.visible = False
        self.page.update()

    def eliminar_overlay(self, e):
        """Elimina el empleado desde el overlay."""
        database.eliminar_empleado(self.empleado_eliminar_id)
        self.overlay_eliminar.visible = False
        self.cargar_tabla()
        self.on_refresh()
        self.page.snack_bar.content.value = "✓ Empleado eliminado"
        self.page.snack_bar.bgcolor = COLORS["warning"]
        self.page.snack_bar.open = True
        self.page.update()

    def agregar_empleado(self, e):
        nombre = (self.nombre_input.value or "").strip()
        cedula = (self.cedula_input.value or "").strip()
        numero = (self.numero_input.value or "").strip()

        if not nombre or not cedula:
            self.page.snack_bar.content.value = "El nombre y la cédula son obligatorios"
            self.page.snack_bar.bgcolor = COLORS["danger"]
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            database.crear_empleado(nombre, cedula, numero)
            self.nombre_input.value = ""
            self.cedula_input.value = ""
            self.numero_input.value = ""
            self.cargar_tabla()
            self.on_refresh()
            self.page.snack_bar.content.value = "✓ Empleado agregado exitosamente"
            self.page.snack_bar.bgcolor = COLORS["success"]
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar.content.value = f"Error: {str(ex)}"
            self.page.snack_bar.bgcolor = COLORS["danger"]
            self.page.snack_bar.open = True
            self.page.update()

    # helper
    def cerrar_dialogo(self, dlg):
        dlg.open = False
        self.page.update()
