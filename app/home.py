import flet as ft

def home_view(page: ft.Page):

    user = page.client_storage.get("usuario")

    def salir(e):
        page.client_storage.clear()
        page.go("/login")

    return ft.View(
        "/",
        controls=[
            ft.AppBar(
                title=ft.Text("Family | Sistema de Asistencia"),
                actions=[
                    ft.Text(user["username"]),
                    ft.IconButton(ft.icons.LOGOUT, on_click=salir)
                ]
            ),
            ft.Text(f"Rol: {user['rol']}"),
            ft.Text("Aquí va tu sistema completo 👇")
        ]
    )
