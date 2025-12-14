# admin.py
# Vista de administración y configuración del sistema

import flet as ft
import database
from pathlib import Path

# ================================================================
# PALETA GLOBAL DE COLORES
# ================================================================
COLOR_PRIMARY = "#1E88E5"
COLOR_PRIMARY_DARK = "#1565C0"
COLOR_DANGER = "#D32F2F"
COLOR_WARNING = "#FB8C00"
COLOR_SUCCESS = "#2E7D32"
COLOR_TEXT = "black"
CARD_BG = "#FFFFFF"
CARD_SHADOW = ft.BoxShadow(spread_radius=1, blur_radius=12, color="#00000015")


class AdminView:
    def __init__(self, page, on_lock_callback=None):
        self.page = page
        self.on_lock = on_lock_callback
        self.build_ui()

    # ================================================================
    #   UI PRINCIPAL
    # ================================================================
    def build_ui(self):

        # -------------------- EVENTOS --------------------
        def bloquear_vista(e):
            if self.on_lock:
                self.on_lock("admin")

        # BOTÓN BLOQUEAR VISTA
        self.btn_bloquear = ft.ElevatedButton(
            "Bloquear Vista",
            icon=ft.Icons.LOCK,
            bgcolor=COLOR_DANGER,
            color="white",
            on_click=bloquear_vista
        )

        # CAMPOS TURNOS
        self.turno_dia_inicio = ft.TextField(label="Turno Día - Inicio", value="09:00:00", width=150, label_style=ft.TextStyle(color="black"), color="black")
        self.turno_dia_fin = ft.TextField(label="Turno Día - Fin", value="16:00:00", width=150, label_style=ft.TextStyle(color="black"), color="black")
        self.turno_dia_tolerancia = ft.TextField(label="Tolerancia (min)", value="10", width=100, label_style=ft.TextStyle(color="black"), color="black")
        self.turno_noche_inicio = ft.TextField(label="Turno Noche - Inicio", value="16:00:00", width=150, label_style=ft.TextStyle(color="black"), color="black")
        self.turno_noche_fin = ft.TextField(label="Turno Noche - Fin", value="23:00:00", width=150, label_style=ft.TextStyle(color="black"), color="black")
        self.turno_noche_tolerancia = ft.TextField(label="Tolerancia (min)", value="10", width=100, label_style=ft.TextStyle(color="black"), color="black")

        self.btn_guardar_turnos = ft.ElevatedButton(
            "Guardar Cambios de Turnos",
            icon=ft.Icons.SAVE,
            bgcolor=COLOR_SUCCESS,
            color="white",
            on_click=self.guardar_turnos
        )

        # CAMPOS CONTRASEÑA
        self.password_actual = ft.TextField(label="Contraseña Actual", password=True, can_reveal_password=True, width=250, label_style=ft.TextStyle(color="black"), color="black")
        self.password_nueva = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True, width=250, label_style=ft.TextStyle(color="black"), color="black")
        self.password_confirmar = ft.TextField(label="Confirmar Nueva Contraseña", password=True, can_reveal_password=True, width=250, label_style=ft.TextStyle(color="black"), color="black")

        self.btn_cambiar_password = ft.ElevatedButton(
            "Cambiar Contraseña",
            icon=ft.Icons.VPN_KEY,
            bgcolor=COLOR_PRIMARY,
            color="white",
            on_click=self.cambiar_password
        )

        # BOTONES BASE DE DATOS
        self.btn_backup = ft.ElevatedButton(
            "Crear Backup",
            icon=ft.Icons.BACKUP,
            bgcolor=COLOR_PRIMARY,
            color="white",
            on_click=self.crear_backup
        )

        self.btn_limpiar_registros = ft.ElevatedButton(
            "Limpiar Registros",
            icon=ft.Icons.DELETE_SWEEP,
            bgcolor=COLOR_WARNING,
            color="white",
            on_click=self.limpiar_registros_dialog
        )

        self.btn_borrar_todo = ft.ElevatedButton(
            "BORRAR TODA LA BASE DE DATOS",
            icon=ft.Icons.WARNING,
            bgcolor=COLOR_DANGER,
            color="white",
            on_click=self.confirmar_borrar_todo
        )

        # ESTADÍSTICAS
        self.stats_text = ft.Text("Cargando estadísticas...", size=14, color="black")
        self.cargar_estadisticas()

        # ================================================================
        # LAYOUT FINAL
        # ================================================================
        self.container = ft.Container(
            bgcolor="white",
            expand=True,
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.SETTINGS, size=32, color=COLOR_PRIMARY),
                                    ft.Text("Configuración del Sistema", size=26, weight=ft.FontWeight.BOLD, color="black"),
                                ],
                                spacing=10
                            ),
                            self.btn_bloquear
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=15),
                    self.card("📊 Estadísticas del Sistema", ft.Column([self.stats_text])),
                    self.card(
                        "🕐 Configuración de Turnos",
                        ft.Column(
                            [
                                ft.Text("Turno Día", weight=ft.FontWeight.BOLD, color="black"),
                                ft.Row([self.turno_dia_inicio, self.turno_dia_fin, self.turno_dia_tolerancia], spacing=15),
                                ft.Divider(),
                                ft.Text("Turno Noche", weight=ft.FontWeight.BOLD, color="black"),
                                ft.Row([self.turno_noche_inicio, self.turno_noche_fin, self.turno_noche_tolerancia], spacing=15),
                                ft.Container(height=10),
                                self.btn_guardar_turnos
                            ]
                        )
                    ),
                    self.card(
                        "🔐 Cambiar Contraseña",
                        ft.Column([ft.Row([self.password_actual, self.password_nueva, self.password_confirmar], wrap=True, spacing=10), self.btn_cambiar_password])
                    ),
                    self.card(
                        "💾 Gestión de Base de Datos",
                        ft.Column(
                            [
                                ft.Text("⚠️ Precaución: estas acciones pueden eliminar información importante.", color="black"),
                                ft.Row([self.btn_backup, self.btn_limpiar_registros], spacing=15),
                                ft.Container(height=10),
                                self.btn_borrar_todo
                            ]
                        )
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    # ================================================================
    # COMPONENTE TARJETA
    # ================================================================
    def card(self, titulo, contenido):
        return ft.Container(
            bgcolor=CARD_BG,
            padding=20,
            border_radius=12,
            shadow=CARD_SHADOW,
            content=ft.Column([ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="black"), contenido], spacing=15)
        )

    # ================================================================
    # FUNCIONES
    # ================================================================
    def cargar_estadisticas(self):
        try:
            empleados = database.obtener_empleados()
            asistencias = database.consultar_asistencias()
            db_path = Path(__file__).parent / "data.db"
            db_size = db_path.stat().st_size / 1024
            self.stats_text.value = f"• Empleados activos: {len(empleados)}\n• Registros de asistencia: {len(asistencias)}\n• Tamaño de base de datos: {db_size:.2f} KB"
        except Exception as e:
            self.stats_text.value = f"Error: {e}"

    def guardar_turnos(self, e):
        self.mostrar_snackbar("Función en desarrollo", COLOR_WARNING)

    def cambiar_password(self, e):
        if not self.password_actual.value or not self.password_nueva.value:
            self.mostrar_snackbar("Complete los campos", COLOR_DANGER)
            return
        if self.password_nueva.value != self.password_confirmar.value:
            self.mostrar_snackbar("Las contraseñas no coinciden", COLOR_DANGER)
            return
        self.mostrar_snackbar("Función en desarrollo", COLOR_WARNING)

    def crear_backup(self, e):
        try:
            import shutil
            from datetime import datetime
            backup_dir = Path(__file__).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            db_path = Path(__file__).parent / "data.db"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}.db"
            shutil.copy2(db_path, backup_path)
            self.mostrar_snackbar("Backup creado correctamente", COLOR_SUCCESS)
        except Exception as ex:
            self.mostrar_snackbar(f"Error: {ex}", COLOR_DANGER)

    def limpiar_registros_dialog(self, e):
        self.mostrar_snackbar("Función en desarrollo", COLOR_WARNING)

    def confirmar_borrar_todo(self, e):
        def ejecutar_borrado(e):
            try:
                db_path = Path(__file__).parent / "data.db"
                db_path.unlink()
                database.initialize_database()
                dlg.open = False
                self.page.update()
                self.mostrar_snackbar("Base de datos reiniciada", COLOR_SUCCESS)
                self.cargar_estadisticas()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {ex}", COLOR_DANGER)

        dlg = ft.AlertDialog(
            title=ft.Text("⚠️ ADVERTENCIA CRÍTICA", color="black"),
            content=ft.Text("¿Está seguro de que desea eliminar TODOS los datos?\nEsta acción NO se puede deshacer.", color="black"),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog(dlg)),
                     ft.ElevatedButton("ELIMINAR TODO", bgcolor=COLOR_DANGER, color="white", on_click=ejecutar_borrado)]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog(self, dlg):
        dlg.open = False
        self.page.update()

    def mostrar_snackbar(self, mensaje, color):
        self.page.snack_bar.content.value = mensaje
        self.page.snack_bar.bgcolor = color
        self.page.snack_bar.open = True
        self.page.update()
