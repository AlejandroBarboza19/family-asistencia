import flet as ft
import os
from marcacion import MarcacionView
from empleados import EmpleadosView
from marcaciones_diarias import MarcacionesDiariasView
from reportes import ReportesView
from admin import AdminView
from diseño_premium import COLORS, PremiumButton, SidebarItem
from login import login_view

# === FORZAR LETRAS NEGRAS EN TODA LA APP ===
COLORS["text_primary"] = "#000000"
COLORS["text_secondary"] = "#000000"

def main(page: ft.Page):
    page.title = "Family | Sistema de Asistencia"
    page.window.width = 1500
    page.window.height = 950
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F6F2EE"

    # Snackbar premium
    page.snack_bar = ft.SnackBar(
        content=ft.Text("", color="#000000"),
        bgcolor=ft.Colors.with_opacity(0.15, "#000000"),
    )

    # === FUNCIONES DE AUTENTICACIÓN ===
    def usuario_logueado():
        """Retorna el usuario actual o None si no está logueado"""
        return page.client_storage.get("usuario")

    def cerrar_sesion():
        """Cierra la sesión y redirige al login"""
        page.client_storage.remove("usuario")
        page.snack_bar.content.value = "🔒 Sesión cerrada"
        page.snack_bar.open = True
        page.update()
        page.go("/login")

    # === FUNCIONES DE CONTROL DE VISTAS ===
    def refresh_callback():
        page.update()

    def mostrar_snackbar(mensaje):
        page.snack_bar.content.value = mensaje
        page.snack_bar.open = True
        page.update()

    # === CONTENEDOR PRINCIPAL (SE DECLARA UNA SOLA VEZ) ===
    contenedor_principal = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLORS["bg_primary"],
    )

    # === FUNCIÓN PARA CREAR SIDEBAR SEGÚN ROL ===
    def crear_sidebar(user):
        rol = user["rol"]
        username = user["username"]

        # === ESTADO DE VISTA ACTIVA ===
        vista_activa = {"nombre": "marcacion"}

        def actualizar_vista(vista_nombre, contenido):
            """Actualiza el contenedor principal con animación"""
            vista_activa["nombre"] = vista_nombre
            contenedor_principal.content = contenido
            actualizar_botones(vista_nombre)
            
            # Animación simple
            contenedor_principal.opacity = 0
            page.update()
            contenedor_principal.opacity = 1
            page.update()

        def actualizar_botones(nombre_activo):
            """Actualiza el estilo de los botones del sidebar"""
            items = {
                "marcacion": nav_marcacion,
                "diarias": nav_diarias,
                "empleados": nav_empleados,
                "reportes": nav_reportes,
                "admin": nav_admin,
            }

            for nombre, item in items.items():
                if item is None:
                    continue
                if nombre == nombre_activo:
                    item.bgcolor = COLORS["glass"]
                    item.border = ft.border.all(1, COLORS["glass_border"])
                else:
                    item.bgcolor = "transparent"
                    item.border = None

            page.update()

        # === CREAR VISTAS SEGÚN ROL ===
        # Vista de Marcación (TODOS)
        marcacion_view = MarcacionView(page, refresh_callback)
        
        # Inicializar variables de navegación
        nav_marcacion = None
        nav_diarias = None
        nav_empleados = None
        nav_reportes = None
        nav_admin = None

        # Lista de items del sidebar
        sidebar_items = []

        # === MARCACIÓN (TODOS) ===
        nav_marcacion = SidebarItem(
            ft.Icons.ACCESS_TIME_ROUNDED, 
            "Marcación", 
            active=True,
            on_click=lambda e: actualizar_vista("marcacion", marcacion_view.container)
        )
        sidebar_items.append(nav_marcacion)

        # === MARCACIONES DIARIAS (admin, jefe) ===
        if rol in ["admin", "jefe"]:
            diarias_view = MarcacionesDiariasView(page)
            nav_diarias = SidebarItem(
                ft.Icons.TODAY_ROUNDED,
                "Hoy",
                on_click=lambda e: actualizar_vista("diarias", diarias_view.container)
            )
            sidebar_items.append(nav_diarias)

        # === REPORTES (admin, jefe) ===
        if rol in ["admin", "jefe"]:
            reportes_view = ReportesView(page, lambda vista: mostrar_snackbar(f"Vista {vista} actualizada"))
            nav_reportes = SidebarItem(
                ft.Icons.ASSESSMENT_ROUNDED,
                "Reportes",
                on_click=lambda e: actualizar_vista("reportes", reportes_view.container)
            )
            sidebar_items.append(nav_reportes)

        # === EMPLEADOS (solo admin) ===
        if rol == "admin":
            empleados_view = EmpleadosView(page, refresh_callback, lambda vista: mostrar_snackbar(f"Vista {vista} actualizada"))
            nav_empleados = SidebarItem(
                ft.Icons.PEOPLE_ROUNDED,
                "Empleados",
                on_click=lambda e: actualizar_vista("empleados", empleados_view.container)
            )
            sidebar_items.append(nav_empleados)

        # === ADMIN (solo admin) ===
        if rol == "admin":
            admin_view_instance = AdminView(page, lambda vista: mostrar_snackbar(f"Vista {vista} actualizada"))
            nav_admin = SidebarItem(
                ft.Icons.SETTINGS_ROUNDED,
                "Admin",
                on_click=lambda e: actualizar_vista("admin", admin_view_instance.container)
            )
            sidebar_items.append(nav_admin)

        # === SIDEBAR COMPLETO ===
        navegacion = ft.Container(
            content=ft.Column(
                [
                    # Logo y título
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, size=40, color="#000000"),
                                width=60,
                                height=60,
                                border_radius=16,
                                alignment=ft.alignment.center,
                            ),
                            ft.Text("Family", size=22, weight=ft.FontWeight.BOLD, color="#000000"),
                            ft.Text("Control de asistencia", size=14, color="#000000"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    
                    # Información del usuario
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.PERSON, size=16, color="#000000"),
                                        ft.Text(username, size=13, weight=ft.FontWeight.BOLD, color="#000000"),
                                    ],
                                    spacing=8,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        rol.upper(), 
                                        size=10, 
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF"
                                    ),
                                    bgcolor="#4CAF50" if rol == "admin" else "#2196F3" if rol == "jefe" else "#FF9800",
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=8,
                                ),
                            ],
                            spacing=5,
                        ),
                        bgcolor=COLORS["glass"],
                        border=ft.border.all(1, COLORS["glass_border"]),
                        border_radius=12,
                        padding=12,
                    ),
                    
                    ft.Divider(height=1, color=COLORS["glass_border"]),
                    
                    # Items de navegación
                    *sidebar_items,
                    
                    # Espaciador
                    ft.Container(expand=True),
                    
                    # Botón de cerrar sesión
                    ft.Divider(height=1, color=COLORS["glass_border"]),
                    ft.Container(
                        content=ft.TextButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.LOGOUT, size=20, color="#000000"),
                                    ft.Text("Cerrar Sesión", size=14, color="#000000"),
                                ],
                                spacing=10,
                            ),
                            on_click=lambda e: cerrar_sesion(),
                        ),
                        border_radius=12,
                        ink=True,
                    ),
                ],
                spacing=15,
            ),
            width=280,
            bgcolor=COLORS["bg_secondary"],
            border=ft.border.only(right=ft.BorderSide(1, COLORS["glass_border"])),
            padding=24,
        )

        return navegacion

    # === MANEJO DE RUTAS ===
    def route_change(route):
        page.views.clear()
        user = usuario_logueado()

        # 🔒 Protección global
        if not user and page.route != "/login":
            page.go("/login")
            return

        # ================= LOGIN =================
        if page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [login_view(page)],
                    padding=0
                )
            )

        # ================= APP PRINCIPAL =================
        else:
            sidebar = crear_sidebar(user)

            # 🎯 Vista inicial: MARCACIÓN por defecto
            contenedor_principal.content = MarcacionView(
                page, refresh_callback
            ).container

            layout = ft.Row(
                [
                    sidebar,
                    contenedor_principal,
                ],
                expand=True,
                spacing=0,
            )

            page.views.append(
                ft.View(
                    "/",
                    [layout],
                    padding=0
                )
            )

        page.update()

    # === CONFIGURAR NAVEGACIÓN ===
    page.on_route_change = route_change
    
    # 🚀 Ruta inicial
    page.go("/" if usuario_logueado() else "/login")


# === INICIAR APLICACIÓN ===
ft.app(
    target=main,
    view=ft.WEB_BROWSER,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000))
)