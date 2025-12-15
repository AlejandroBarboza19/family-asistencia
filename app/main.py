import flet as ft
from marcacion import MarcacionView
from empleados import EmpleadosView
from marcaciones_diarias import MarcacionesDiariasView
from reportes import ReportesView
from admin import AdminView
from diseño_premium import COLORS, PremiumTextField, PremiumButton, SidebarItem

import os

# === CONFIGURACIÓN GLOBAL DE COLORES ===
COLORS["text_primary"] = "#000000"
COLORS["text_secondary"] = "#000000"

# Contraseña de administrador
ADMIN_PASSWORD = "admin123"

def main(page: ft.Page):
    page.title = "Family | Sistema de Asistencia"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F6F2EE"
    page.scroll = "auto"
    
    # Configuración responsive
    page.window_min_width = 320
    page.window_min_height = 480

    # --- Funciones para detectar tamaño ---
    def es_movil(): 
        return page.width < 768
    
    def es_tablet(): 
        return 768 <= page.width < 1024
    
    def es_movil_pequeño():
        return page.width < 400

    # --- Snackbar global ---
    page.snack_bar = ft.SnackBar(
        content=ft.Text("", color="white", size=14), 
        bgcolor="#2E7D32",
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=10
    )

    # --- Estados ---
    autenticado_empleados = False
    autenticado_reportes = False
    autenticado_admin = False
    vista_pendiente = None
    menu_abierto = False
    vista_activa = "marcacion"

    # === FUNCIONES ===
    def refresh_callback(): 
        page.update()

    def toggle_menu(e=None):
        nonlocal menu_abierto
        menu_abierto = not menu_abierto
        menu_lateral.visible = menu_abierto
        overlay_menu.visible = menu_abierto
        page.update()

    def cerrar_menu(e=None):
        nonlocal menu_abierto
        menu_abierto = False
        menu_lateral.visible = False
        overlay_menu.visible = False
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
        nonlocal vista_activa
        
        contenedor.content = {
            "marcacion": MarcacionView(page, refresh_callback).container,
            "empleados": EmpleadosView(page, refresh_callback, lock_callback).container,
            "diarias": MarcacionesDiariasView(page).container,
            "reportes": ReportesView(page, lock_callback).container,
            "admin": AdminView(page, lock_callback).container
        }.get(vista_nombre, MarcacionView(page, refresh_callback).container)
        
        vista_activa = vista_nombre
        actualizar_botones(vista_activa)

        # Cerrar menú después de seleccionar
        cerrar_menu()

        # Animación suave
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
        nonlocal autenticado_empleados, autenticado_reportes, autenticado_admin
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
        if vista == "empleados" and not autenticado_empleados: 
            solicitar_password(vista)
        elif vista == "reportes" and not autenticado_reportes: 
            solicitar_password(vista)
        elif vista == "admin" and not autenticado_admin: 
            solicitar_password(vista)
        else: 
            mostrar_vista(vista)

    def actualizar_botones(vista_activa):
        items = {
            "marcacion": nav_marcacion,
            "diarias": nav_diarias,
            "empleados": nav_empleados,
            "reportes": nav_reportes,
            "admin": nav_admin,
        }
        
        for nombre, item in items.items():
            item.bgcolor = COLORS["glass"] if nombre == vista_activa else "transparent"
            item.border = ft.border.all(1, COLORS["glass_border"]) if nombre == vista_activa else None

        lock_empleados.visible = not autenticado_empleados
        lock_reportes.visible = not autenticado_reportes
        lock_admin.visible = not autenticado_admin
        
        page.update()

    def ajustar_layout(e=None):
        is_mobile = es_movil()
        is_small = es_movil_pequeño()
        is_tablet = es_tablet()
        
        # Ajustar ancho del menú según el dispositivo
        if is_small:
            menu_lateral.width = page.width * 0.85
            menu_lateral.padding = 20
            logo_icon.size = 36
            logo_container.width = 60
            logo_container.height = 60
            logo_texto.size = 20
            logo_subtitulo.size = 12
            contenedor.padding = 12
            btn_menu.icon_size = 24
        elif is_mobile:
            menu_lateral.width = min(320, page.width * 0.85)
            menu_lateral.padding = 24
            logo_icon.size = 40
            logo_container.width = 65
            logo_container.height = 65
            logo_texto.size = 22
            logo_subtitulo.size = 13
            contenedor.padding = 16
            btn_menu.icon_size = 26
        elif is_tablet:
            menu_lateral.width = 280
            menu_lateral.padding = 26
            logo_icon.size = 42
            logo_container.width = 68
            logo_container.height = 68
            logo_texto.size = 23
            logo_subtitulo.size = 13
            contenedor.padding = 24
            btn_menu.icon_size = 28
        else:
            menu_lateral.width = 320
            menu_lateral.padding = 28
            logo_icon.size = 44
            logo_container.width = 70
            logo_container.height = 70
            logo_texto.size = 24
            logo_subtitulo.size = 14
            contenedor.padding = 30
            btn_menu.icon_size = 28
        
        # Overlay de contraseña
        if is_mobile:
            overlay_password.content.width = page.width * 0.9
            overlay_password.content.padding = 20 if is_small else 28
            password_overlay_icon.size = 48 if is_small else 56
            password_titulo.size = 20 if is_small else 24
            password_subtitulo.size = 12 if is_small else 14
        else:
            overlay_password.content.width = 450
            overlay_password.content.padding = 35
            password_overlay_icon.size = 56
            password_titulo.size = 24
            password_subtitulo.size = 14
        
        overlay_menu.width = page.width
        overlay_menu.height = page.height
        
        page.update()

    # === 1. BOTÓN HAMBURGUESA FIJO ===
    btn_menu = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.MENU_ROUNDED, 
            icon_color="#000000", 
            icon_size=28,
            tooltip="Menú",
            on_click=toggle_menu,
            style=ft.ButtonStyle(
                overlay_color="#00000010",
            )
        ),
        bgcolor=COLORS["bg_card"],
        border_radius=12,
        padding=4,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color="#00000020",
            offset=ft.Offset(0, 4),
        ),
        top=16,
        left=16
    )

    # === 2. OVERLAY PASSWORD ===
    password_input = PremiumTextField(
        label="Contraseña de Administrador", 
        password=True, 
        can_reveal_password=True, 
        on_submit=verificar_password
    )
    
    password_overlay_icon = ft.Icon(
        ft.Icons.LOCK_ROUNDED, 
        size=56, 
        color="#000000"
    )
    
    password_logo_container = ft.Container(
        content=password_overlay_icon,
        width=100, 
        height=100, 
        border_radius=50, 
        alignment=ft.alignment.center,
        bgcolor=COLORS["glass"]
    )
    
    password_titulo = ft.Text(
        "Acceso Restringido", 
        size=24, 
        weight=ft.FontWeight.BOLD, 
        color="#000000",
        text_align=ft.TextAlign.CENTER
    )
    
    password_subtitulo = ft.Text(
        "Esta sección requiere permisos de administrador", 
        size=14, 
        color="#000000",
        text_align=ft.TextAlign.CENTER
    )
    
    overlay_password = ft.Container(
        content=ft.Container(
            content=ft.Column([
                password_logo_container,
                password_titulo,
                password_subtitulo,
                password_input,
                ft.Row(
                    [
                        PremiumButton("Cancelar", on_click=cerrar_overlay),
                        PremiumButton("Ingresar", icon=ft.Icons.LOGIN_ROUNDED, on_click=verificar_password)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    wrap=True
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            spacing=20),
            bgcolor=COLORS["bg_card"], 
            padding=35, 
            border_radius=24,
            width=450
        ),
        alignment=ft.alignment.center, 
        bgcolor="#000000CC", 
        visible=False, 
        expand=True
    )

    # === 3. LOCKS ===
    lock_empleados = ft.Icon(ft.Icons.LOCK, color="#000000", size=16)
    lock_reportes = ft.Icon(ft.Icons.LOCK, color="#000000", size=16)
    lock_admin = ft.Icon(ft.Icons.LOCK, color="#000000", size=16)

    # === 4. ITEMS DE NAVEGACIÓN ===
    nav_marcacion = SidebarItem(
        ft.Icons.ACCESS_TIME_ROUNDED, 
        "Marcación", 
        active=True, 
        on_click=lambda e: cambiar_vista("marcacion")
    )
    nav_diarias = SidebarItem(
        ft.Icons.TODAY_ROUNDED, 
        "Hoy", 
        on_click=lambda e: cambiar_vista("diarias")
    )
    nav_empleados = SidebarItem(
        ft.Icons.PEOPLE_ROUNDED, 
        "Empleados", 
        on_click=lambda e: cambiar_vista("empleados")
    )
    nav_empleados.content.controls.append(lock_empleados)
    
    nav_reportes = SidebarItem(
        ft.Icons.ASSESSMENT_ROUNDED, 
        "Reportes", 
        on_click=lambda e: cambiar_vista("reportes")
    )
    nav_reportes.content.controls.append(lock_reportes)
    
    nav_admin = SidebarItem(
        ft.Icons.SETTINGS_ROUNDED, 
        "Admin", 
        on_click=lambda e: cambiar_vista("admin")
    )
    nav_admin.content.controls.append(lock_admin)

    # === 5. MENÚ LATERAL DESPLEGABLE ===
    logo_icon = ft.Icon(
        ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, 
        size=44, 
        color="#000000"
    )
    
    logo_container = ft.Container(
        content=logo_icon,
        width=70, 
        height=70, 
        border_radius=20, 
        alignment=ft.alignment.center,
        bgcolor=COLORS["glass"]
    )
    
    logo_texto = ft.Text(
        "Family", 
        size=24, 
        weight=ft.FontWeight.BOLD, 
        color="#000000"
    )
    
    logo_subtitulo = ft.Text(
        "Control de asistencia", 
        size=14, 
        color="#000000",
        text_align=ft.TextAlign.CENTER
    )
    
    menu_lateral = ft.Container(
        content=ft.Column([
            # Header del menú con botón cerrar
            ft.Row(
                [
                    ft.Text("Menú", size=20, weight=ft.FontWeight.BOLD, color="#000000"),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        icon_color="#000000",
                        icon_size=24,
                        tooltip="Cerrar menú",
                        on_click=cerrar_menu
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            
            ft.Divider(height=1, color=COLORS["glass_border"]),
            
            # Logo
            ft.Column([
                logo_container,
                logo_texto,
                logo_subtitulo
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            spacing=8),
            
            ft.Divider(height=1, color=COLORS["glass_border"]),
            
            # Items de navegación
            ft.Column(
                [
                    nav_marcacion, 
                    nav_diarias, 
                    nav_empleados, 
                    nav_reportes, 
                    nav_admin
                ], 
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        ], spacing=20, expand=True),
        width=320,
        bgcolor=COLORS["bg_secondary"],
        padding=28,
        visible=False,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color="#00000030",
            offset=ft.Offset(0, 0)
        ),
        border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
        animate=ft.Animation(300, "easeOut")
    )

    # === 6. OVERLAY OSCURO ===
    overlay_menu = ft.Container(
        bgcolor="#00000060",
        visible=False,
        on_click=cerrar_menu,
        expand=True,
        animate_opacity=200
    )

    # === 7. CONTENEDOR PRINCIPAL ===
    contenedor = ft.Container(
        content=MarcacionView(page, refresh_callback).container, 
        expand=True, 
        padding=30, 
        bgcolor=COLORS["bg_primary"],
        animate_opacity=200
    )

    # === 8. LAYOUT FINAL CON STACK ===
    layout = ft.Stack(
        [
            # Contenido principal (ocupa todo el espacio)
            contenedor,
            
            # Overlay oscuro (cuando el menú está abierto)
            overlay_menu,
            
            # Menú lateral desplegable
            ft.Row(
                [menu_lateral],
                alignment=ft.MainAxisAlignment.START
            ),
            
            # Botón hamburguesa siempre visible
            btn_menu
        ],
        expand=True
    )

    page.add(layout)
    page.overlay.append(overlay_password)
    page.on_resize = ajustar_layout
    
    # Llamar ajustar_layout al inicio
    ajustar_layout()

ft.app(
    target=main, 
    view=ft.WEB_BROWSER, 
    host="0.0.0.0", 
    port=int(os.environ.get("PORT", 8000))
)