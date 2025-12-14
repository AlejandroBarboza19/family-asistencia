import flet as ft
from marcacion import MarcacionView
from empleados import EmpleadosView
from marcaciones_diarias import MarcacionesDiariasView
from reportes import ReportesView
from admin import AdminView
from diseño_premium import COLORS, PremiumTextField, PremiumButton, SidebarItem

# === FORZAR LETRAS NEGRAS EN TODA LA APP ===
COLORS["text_primary"] = "#000000"
COLORS["text_secondary"] = "#000000"

# Contraseña de administrador
ADMIN_PASSWORD = "admin123"

def main(page: ft.Page):
    page.title = "Family | Sistema de Asistencia"
    page.window.width = 1500
    page.window.height = 950
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # Fondo crema/beige sin difuminar la UI
    page.bgcolor = "#F6F2EE"

    # Snackbar premium
    page.snack_bar = ft.SnackBar(
        content=ft.Text("", color="#000000"),
        bgcolor=ft.Colors.with_opacity(0.15, "#000000"),
    )

    # Estado de autenticación
    autenticado_empleados = False
    autenticado_reportes = False
    autenticado_admin = False
    vista_pendiente = None

    # === FUNCIONES DE CONTROL ===
    def refresh_callback():
        page.update()

    def lock_callback(vista_nombre):
        nonlocal autenticado_empleados, autenticado_reportes, autenticado_admin
        if vista_nombre == "empleados":
            autenticado_empleados = False
        elif vista_nombre == "reportes":
            autenticado_reportes = False
        elif vista_nombre == "admin":
            autenticado_admin = False

        mostrar_vista("marcacion")
        page.snack_bar.content.value = f"🔒 {vista_nombre.capitalize()} bloqueado"
        page.snack_bar.open = True
        page.update()

    def mostrar_vista(vista_nombre):
        if vista_nombre == "marcacion":
            contenedor.content = MarcacionView(page, refresh_callback).container
        elif vista_nombre == "empleados":
            contenedor.content = EmpleadosView(page, refresh_callback, lock_callback).container
        elif vista_nombre == "diarias":
            contenedor.content = MarcacionesDiariasView(page).container
        elif vista_nombre == "reportes":
            contenedor.content = ReportesView(page, lock_callback).container
        elif vista_nombre == "admin":
            contenedor.content = AdminView(page, lock_callback).container

        actualizar_botones(vista_nombre)

        # Animación simple
        contenedor.opacity = 0
        page.update()
        contenedor.opacity = 1
        page.update()

    def cerrar_overlay(e=None):
        overlay_password.visible = False
        password_input.value = ""
        password_input.error_text = ""
        page.update()

    def verificar_password(e=None):
        nonlocal autenticado_empleados, autenticado_reportes, autenticado_admin, vista_pendiente

        if password_input.value == ADMIN_PASSWORD:
            if vista_pendiente == "empleados":
                autenticado_empleados = True
            elif vista_pendiente == "reportes":
                autenticado_reportes = True
            elif vista_pendiente == "admin":
                autenticado_admin = True

            cerrar_overlay()
            mostrar_vista(vista_pendiente)
        else:
            password_input.error_text = "❌ Contraseña incorrecta"
            password_input.value = ""
            page.update()

    def solicitar_password(vista_nombre):
        nonlocal vista_pendiente
        vista_pendiente = vista_nombre
        overlay_password.visible = True
        password_input.value = ""
        password_input.error_text = ""
        page.update()
        password_input.focus()

    def cambiar_vista(vista):
        nonlocal autenticado_empleados, autenticado_reportes, autenticado_admin
        if vista == "empleados" and not autenticado_empleados:
            solicitar_password(vista)
        elif vista == "reportes" and not autenticado_reportes:
            solicitar_password(vista)
        elif vista == "admin" and not autenticado_admin:
            solicitar_password(vista)
        else:
            mostrar_vista(vista)

    def actualizar_botones(vista_activa):
        nonlocal autenticado_empleados, autenticado_reportes, autenticado_admin
        items = {
            "marcacion": nav_marcacion,
            "diarias": nav_diarias,
            "empleados": nav_empleados,
            "reportes": nav_reportes,
            "admin": nav_admin,
        }

        for nombre, item in items.items():
            if nombre == vista_activa:
                item.bgcolor = COLORS["glass"]
                item.border = ft.border.all(1, COLORS["glass_border"])
            else:
                item.bgcolor = "transparent"
                item.border = None

        lock_empleados.visible = not autenticado_empleados
        lock_reportes.visible = not autenticado_reportes
        lock_admin.visible = not autenticado_admin

        page.update()

    # === OVERLAY DE PASSWORD ===
    password_input = PremiumTextField(
        label="Contraseña de Administrador",
        password=True,
        can_reveal_password=True,
        width=400,
        on_submit=verificar_password,
    )

    overlay_password = ft.Container(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.LOCK_ROUNDED, size=56, color="#000000"),
                        width=100,
                        height=100,
                        border_radius=50,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text("Acceso Restringido", size=28, weight=ft.FontWeight.BOLD, color="#000000"),
                    ft.Text(
                        "Esta sección requiere permisos de administrador",
                        size=14,
                        color="#000000",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    password_input,
                    ft.Row(
                        [
                            PremiumButton("Cancelar", on_click=cerrar_overlay, gradient=False, width=150),
                            PremiumButton("Ingresar", icon=ft.Icons.LOGIN_ROUNDED, on_click=verificar_password, width=150),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLORS["bg_card"],
            padding=40,
            border_radius=24,
            width=550,
        ),
        alignment=ft.alignment.center,
        bgcolor="#00000099",
        visible=False,
        expand=True,
    )

    # === ICONOS DE LOCK ===
    lock_empleados = ft.Icon(ft.Icons.LOCK, color="#000000", size=16)
    lock_reportes = ft.Icon(ft.Icons.LOCK, color="#000000", size=16)
    lock_admin = ft.Icon(ft.Icons.LOCK, color="#000000", size=16)

    # === SIDEBAR ===
    nav_marcacion = SidebarItem(ft.Icons.ACCESS_TIME_ROUNDED, "Marcación", active=True, on_click=lambda e: cambiar_vista("marcacion"))
    nav_diarias = SidebarItem(ft.Icons.TODAY_ROUNDED, "Hoy", on_click=lambda e: cambiar_vista("diarias"))
    nav_empleados = SidebarItem(ft.Icons.PEOPLE_ROUNDED, "Empleados", on_click=lambda e: cambiar_vista("empleados"))
    nav_empleados.content.controls.append(lock_empleados)
    nav_reportes = SidebarItem(ft.Icons.ASSESSMENT_ROUNDED, "Reportes", on_click=lambda e: cambiar_vista("reportes"))
    nav_reportes.content.controls.append(lock_reportes)
    nav_admin = SidebarItem(ft.Icons.SETTINGS_ROUNDED, "Admin", on_click=lambda e: cambiar_vista("admin"))
    nav_admin.content.controls.append(lock_admin)

    # === HEADER DEL SIDEBAR ===
    navegacion = ft.Container(
        content=ft.Column(
            [
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
                ft.Divider(height=1, color=COLORS["glass_border"]),
                nav_marcacion,
                nav_diarias,
                nav_empleados,
                nav_reportes,
                nav_admin,
            ],
            spacing=15,
        ),
        width=280,
        bgcolor=COLORS["bg_secondary"],
        border=ft.border.only(right=ft.BorderSide(1, COLORS["glass_border"])),
        padding=24,
    )

    # === CONTENEDOR PRINCIPAL ===
    contenedor = ft.Container(
        content=MarcacionView(page, refresh_callback).container,
        expand=True,
        padding=30,
        bgcolor=COLORS["bg_primary"],
    )

    # === LAYOUT PRINCIPAL ===
    layout = ft.Row(
        [navegacion, contenedor],
        expand=True,
        spacing=0,
    )

    page.add(layout)
    page.overlay.append(overlay_password)

ft.app(target=main)
