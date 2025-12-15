import flet as ft
from database import autenticar_usuario

def login_view(page: ft.Page):
    """Vista de login - retorna SOLO el contenedor, no un ft.View"""
    
    usuario = ft.TextField(
        label="Usuario", 
        width=300,
        autofocus=True
    )
    clave = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True,
        width=300
    )
    mensaje = ft.Text(color=ft.Colors.RED)

    def entrar(e):
        # Validar campos vacíos
        if not usuario.value or not clave.value:
            mensaje.value = "⚠️ Por favor completa todos los campos"
            page.update()
            return

        # Autenticar usuario
        user = autenticar_usuario(usuario.value, clave.value)

        if not user:
            mensaje.value = "❌ Credenciales incorrectas"
            clave.value = ""
            page.update()
            return

        # Guardar sesión
        page.client_storage.set("usuario", {
            "id": user["id"],
            "username": user["username"],
            "rol": user["rol"]
        })
        
        # Redirigir a la app
        page.go("/")

    # Permitir Enter para login
    clave.on_submit = entrar

    # 🎯 RETORNA SOLO EL CONTENEDOR (no ft.View)
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        bgcolor="#F6F2EE",
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Logo
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, 
                        size=70, 
                        color="#FF6B35"
                    ),
                    width=120,
                    height=120,
                    bgcolor=ft.Colors.with_opacity(0.1, "#FF6B35"),
                    border_radius=60,
                    alignment=ft.alignment.center,
                ),
                
                ft.Container(height=20),
                
                # Título
                ft.Text(
                    "Family", 
                    size=42, 
                    weight=ft.FontWeight.BOLD,
                    color="#000000"
                ),
                ft.Text(
                    "Sistema de Asistencia", 
                    size=16, 
                    color="#666666"
                ),
                
                ft.Container(height=40),
                
                # Formulario
                ft.Container(
                    content=ft.Column(
                        [
                            usuario,
                            ft.Container(height=15),
                            clave,
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "Ingresar",
                                icon=ft.Icons.LOGIN_ROUNDED,
                                on_click=entrar,
                                width=300,
                                height=50,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor="#FF6B35",
                                )
                            ),
                            ft.Container(height=15),
                            mensaje,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=20,
                    padding=40,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.1, "#000000"),
                    ),
                ),
            ],
        ),
    )