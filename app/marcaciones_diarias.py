# marcaciones_diarias.py
# Vista de marcaciones del día en tiempo real

import flet as ft
import database
from datetime import datetime

# ---------------------------
# FUNCIÓN SEGURA PARA SQLITE3.ROW
# ---------------------------

def safe_get(row, key, default=None):
    try:
        value = row[key]
        if value is None or value == "" or value == "NULL":
            return default
        return value
    except Exception:
        return default


# =====================================================================
#                         CLASE PRINCIPAL
# =====================================================================

class MarcacionesDiariasView:
    def __init__(self, page):
        self.page = page
        self.build_ui()
    
    def build_ui(self):

        # ---------------------------
        # Botón refrescar
        # ---------------------------
        self.btn_refrescar = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refrescar",
            icon_color="#000000",
            icon_size=30,
            on_click=self.cargar_marcaciones,
        )
        
        # ---------------------------
        # Fecha actual formateada
        # ---------------------------
        hoy = datetime.now()
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        dia_semana = dias[hoy.weekday()]
        mes = meses[hoy.month - 1]
        
        self.fecha_texto = ft.Text(
            f"{dia_semana}, {hoy.day} de {mes} de {hoy.year}",
            size=18,
            color="#000000",
        )
        
        # ---------------------------
        # Tarjetas de estadísticas
        # ---------------------------
        self.stats_container = ft.Row(
            [
                self.crear_stat_card("Total Empleados", "0", ft.Icons.PEOPLE, "#1E88E5"),
                self.crear_stat_card("Han Marcado", "0", ft.Icons.CHECK_CIRCLE, "#43A047"),
                self.crear_stat_card("Llegadas Tarde", "0", ft.Icons.WARNING, "#FB8C00"),
                self.crear_stat_card("Faltan", "0", ft.Icons.SCHEDULE, "#546E7A"),
            ],
            spacing=15,
            wrap=True,
        )

        # ---------------------------
        # Lista de marcaciones
        # ---------------------------
        self.lista_marcaciones = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # ---------------------------
        # LAYOUT GENERAL
        # ---------------------------
        self.container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.TODAY, size=40, color="#000000"),
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    "Marcaciones de Hoy",
                                                    size=28,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#000000",
                                                ),
                                                self.fecha_texto,
                                            ],
                                            spacing=3,
                                        ),
                                    ],
                                    spacing=15,
                                ),
                                self.btn_refrescar,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    
                    self.stats_container,
                    ft.Container(height=20),
                    
                    ft.Text(
                        "Marcaciones Registradas",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#000000",
                    ),

                    ft.Container(
                        content=self.lista_marcaciones,
                        bgcolor="#FFFFFF",
                        padding=20,
                        border_radius=15,
                        shadow=ft.BoxShadow(
                            spread_radius=2,
                            blur_radius=10,
                            color="#00000019",
                        ),
                        height=500,
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
        )
        
        self.cargar_marcaciones()
    

    # =====================================================================
    #                         TARJETAS DE STATS
    # =====================================================================

    def crear_stat_card(self, titulo, valor, icono, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icono, size=40, color=color),
                    ft.Text(valor, size=32, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(titulo, size=14, color="#000000"),  # ← negro
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=15,
            width=200,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color="#00000019",
            ),
        )
    

    # =====================================================================
    #                         CARGA PRINCIPAL
    # =====================================================================

    def cargar_marcaciones(self, e=None):
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        marcaciones = database.consultar_asistencias(f_inicio=hoy, f_fin=hoy)
        empleados = database.obtener_empleados()

        total = len(empleados)
        marcados = len(marcaciones)
        tarde = sum(1 for m in marcaciones if safe_get(m, "llego_tarde") == "SI")
        faltan = total - marcados
        
        # Actualizar estadísticas
        self.stats_container.controls[0].content.controls[1].value = str(total)
        self.stats_container.controls[1].content.controls[1].value = str(marcados)
        self.stats_container.controls[2].content.controls[1].value = str(tarde)
        self.stats_container.controls[3].content.controls[1].value = str(faltan)
        
        self.lista_marcaciones.controls.clear()
        
        if not marcaciones:
            self.lista_marcaciones.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=60, color="#000000"),
                            ft.Text("No hay marcaciones registradas hoy", size=16, color="#000000"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=40,
                )
            )
        else:
            ordenadas = sorted(marcaciones, key=lambda x: safe_get(x, "hora_llegada", ""), reverse=True)
            for m in ordenadas:
                self.lista_marcaciones.controls.append(self.card_marcacion(m))

        self.page.update()


    # =====================================================================
    #                         TARJETA DE MARCACIÓN
    # =====================================================================

    def card_marcacion(self, m):

        nombre = safe_get(m, "nombre", "Sin Nombre")
        numero = safe_get(m, "numero", "Sin teléfono")
        hora_llegada = safe_get(m, "hora_llegada", "--:--:--")
        hora_salida = safe_get(m, "hora_salida")
        horas = safe_get(m, "horas_trabajadas")
        turno = safe_get(m, "turno", "")
        tarde = safe_get(m, "llego_tarde", "NO")

        if tarde == "SI":
            estado_color = "#F57C00"
            estado_texto = "🔴 LLEGÓ TARDE"
        else:
            estado_color = "#2E7D32"
            estado_texto = "🟢 A TIEMPO"

        if "Día" in turno or "DIA" in turno.upper():
            turno_color = "#FFA726"
            turno_icono = "🌞"
        else:
            turno_color = "#5C6BC0"
            turno_icono = "🌙"

        if hora_salida:
            salida_widget = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOGOUT, size=16, color="white"),
                        ft.Text(f"Salida: {hora_salida}", size=12, color="white", weight=ft.FontWeight.BOLD),
                    ],
                    spacing=5,
                ),
                bgcolor="#1E88E5",
                padding=8,
                border_radius=8,
            )
        else:
            salida_widget = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ACCESS_TIME, size=16, color="white"),
                        ft.Text("En turno", size=12, color="white", weight=ft.FontWeight.BOLD),
                    ],
                    spacing=5,
                ),
                bgcolor="#546E7A",
                padding=8,
                border_radius=8,
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.PERSON, size=40, color="#000000"),
                                    ft.Column(
                                        [
                                            ft.Text(nombre, size=18, weight=ft.FontWeight.BOLD, color="#000000"),
                                            ft.Text(f"📱 {numero}", size=14, color="#000000"),
                                        ]
                                    ),
                                ],
                                spacing=15,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    estado_texto,
                                    size=14,
                                    color="white",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=estado_color,
                                padding=10,
                                border_radius=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),

                    ft.Divider(),

                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    f"{turno_icono} {turno}",
                                    size=12,
                                    color="white",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=turno_color,
                                padding=8,
                                border_radius=8,
                            ),

                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.LOGIN, size=16, color="white"),
                                        ft.Text(f"Llegada: {hora_llegada}", size=12, color="white", weight=ft.FontWeight.BOLD),
                                    ]
                                ),
                                bgcolor="#2E7D32",
                                padding=8,
                                border_radius=8,
                            ),

                            salida_widget,

                            ft.Container(
                                content=ft.Text(
                                    f"⏱️ {horas if horas else '--:--:--'}",
                                    size=12,
                                    color="#000000",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                padding=8,
                                border_radius=8,
                            ),
                        ],
                        spacing=10,
                        wrap=True,
                    ),
                ],
                spacing=15,
            ),
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=15,
            border=ft.border.all(3, estado_color),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color="#00000014",
            ),
        )
