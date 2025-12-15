# reportes.py
import flet as ft
import database
from exportar import exportar_excel, exportar_pdf
from datetime import datetime, timedelta
from pathlib import Path
import base64

class ReportesView:
    def __init__(self, page, on_lock_callback=None):
        self.page = page
        self.on_lock = on_lock_callback

        self.build_ui()

    def build_ui(self):
        # Botón bloquear vista
        def bloquear_vista(e):
            if self.on_lock:
                self.on_lock("reportes")

        self.btn_bloquear = ft.ElevatedButton(
            "🔒 Bloquear Vista",
            icon=ft.Icons.LOCK,
            bgcolor="#C62828",
            color="#FFFFFF",
            on_click=bloquear_vista,
        )

        # Campos de filtro
        self.f_inicio = ft.TextField(label="Fecha inicio (YYYY-MM-DD)", width=200, border_radius=10, label_style=ft.TextStyle(color="black"), color="black")
        self.f_fin = ft.TextField(label="Fecha fin (YYYY-MM-DD)", width=200, border_radius=10, label_style=ft.TextStyle(color="black"), color="black")
        self.f_texto = ft.TextField(label="Buscar por nombre o cédula", width=300, border_radius=10, prefix_icon=ft.Icons.SEARCH, label_style=ft.TextStyle(color="black"), color="black")
        self.f_tarde = ft.Checkbox(label="Solo llegadas tarde", value=False, label_style=ft.TextStyle(color="black"))

        # Botones
        self.btn_filtrar = ft.ElevatedButton("Aplicar Filtros", icon=ft.Icons.FILTER_ALT, bgcolor="#1976D2", color="white", height=45, on_click=self.cargar_tabla)
        self.btn_limpiar = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, bgcolor="#78909C", color="white", height=45, on_click=self.limpiar_filtros)
        self.btn_export_excel = ft.ElevatedButton("Exportar Excel", icon=ft.Icons.TABLE_CHART, bgcolor="#2E7D32", color="white", height=45, on_click=lambda e: self.exportar_archivo_web("excel"))
        self.btn_export_pdf = ft.ElevatedButton("Exportar PDF", icon=ft.Icons.PICTURE_AS_PDF, bgcolor="#C62828", color="white", height=45, on_click=lambda e: self.exportar_archivo_web("pdf"))

        # Filtros rápidos
        self.btn_hoy = ft.TextButton("Hoy", icon=ft.Icons.TODAY, on_click=self.filtrar_hoy, style=ft.ButtonStyle(color="black"))
        self.btn_semana = ft.TextButton("Última Semana", icon=ft.Icons.DATE_RANGE, on_click=self.filtrar_semana, style=ft.ButtonStyle(color="black"))
        self.btn_mes = ft.TextButton("Último Mes", icon=ft.Icons.CALENDAR_MONTH, on_click=self.filtrar_mes, style=ft.ButtonStyle(color="black"))

        # Tabla
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Cédula", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Turno", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Llegada", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Salida", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Horas", weight=ft.FontWeight.BOLD, color="black")),
                ft.DataColumn(ft.Text("Tarde", weight=ft.FontWeight.BOLD, color="black")),
            ],
            rows=[],
            border=ft.border.all(1, "#000000"),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, "#000000"),
        )

        # Layout principal
        self.container = ft.Container(
            expand=True,
            padding=20,
            bgcolor="white",
            content=ft.Column(
                [
                    ft.Row([ft.Row([ft.Icon(ft.Icons.ASSESSMENT, size=36, color="#1976D2"), ft.Text("Reportes de Asistencia", size=26, weight=ft.FontWeight.BOLD, color="black")]), self.btn_bloquear], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        bgcolor="white",
                        padding=25,
                        border_radius=15,
                        shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color="#00000019"),
                        content=ft.Column(
                            [
                                ft.Text("Filtros de Búsqueda", size=18, weight=ft.FontWeight.BOLD, color="black"),
                                ft.Row([ft.Text("Filtros rápidos:", weight=ft.FontWeight.BOLD, color="black"), self.btn_hoy, self.btn_semana, self.btn_mes]),
                                ft.Divider(),
                                ft.Row([self.f_inicio, self.f_fin, self.f_texto, self.f_tarde], wrap=True, spacing=10),
                                ft.Row([self.btn_filtrar, self.btn_limpiar, self.btn_export_excel, self.btn_export_pdf], spacing=15),
                            ],
                            spacing=15,
                        ),
                    ),
                    ft.Container(height=15),
                    ft.Container(bgcolor="white", padding=25, border_radius=15, shadow=ft.BoxShadow(spread_radius=2, blur_radius=10, color="#00000019"), content=ft.Column([ft.Text("Resultados", size=18, weight=ft.FontWeight.BOLD, color="black"), self.table], spacing=15)),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        self.cargar_tabla()

    # FILTROS RÁPIDOS
    def filtrar_hoy(self, e):
        hoy = datetime.now().strftime("%Y-%m-%d")
        self.f_inicio.value = hoy
        self.f_fin.value = hoy
        self.cargar_tabla()

    def filtrar_semana(self, e):
        hoy = datetime.now()
        hace_semana = hoy - timedelta(days=7)
        self.f_inicio.value = hace_semana.strftime("%Y-%m-%d")
        self.f_fin.value = hoy.strftime("%Y-%m-%d")
        self.cargar_tabla()

    def filtrar_mes(self, e):
        hoy = datetime.now()
        hace_mes = hoy - timedelta(days=30)
        self.f_inicio.value = hace_mes.strftime("%Y-%m-%d")
        self.f_fin.value = hoy.strftime("%Y-%m-%d")
        self.cargar_tabla()

    # CARGAR TABLA
    def cargar_tabla(self, e=None):
        f_inicio = self.f_inicio.value.strip() if self.f_inicio.value else None
        f_fin = self.f_fin.value.strip() if self.f_fin.value else None
        filas = database.consultar_asistencias(f_inicio=f_inicio, f_fin=f_fin)
        texto = self.f_texto.value.strip().lower() if self.f_texto.value else ""
        if texto:
            filas = [f for f in filas if texto in f["nombre"].lower() or texto in f["cedula"].lower()]
        if self.f_tarde.value:
            filas = [f for f in filas if f["llego_tarde"] == "SI"]

        rows = []
        for r in filas:
            turno = r["turno"]
            turno_color = "#FFA726" if "DIA" in turno.upper() or "DÍA" in turno.upper() else "#5C6BC0"
            turno_icon = "🌞" if turno_color == "#FFA726" else "🌙"
            tarde_color = "#C62828" if r["llego_tarde"] == "SI" else "#2E7D32"
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(r["nombre"], color="black")),
                ft.DataCell(ft.Text(r["cedula"], color="black")),
                ft.DataCell(ft.Text(str(r["fecha"]), color="black")),
                ft.DataCell(ft.Container(bgcolor=turno_color, padding=5, border_radius=5, content=ft.Text(f"{turno_icon} {turno}", color="white"))),
                ft.DataCell(ft.Text(str(r["hora_llegada"]) if r["hora_llegada"] else "-", color="black")),
                ft.DataCell(ft.Text(str(r["hora_salida"]) if r["hora_salida"] else "-", color="black")),
                ft.DataCell(ft.Text(r["horas_trabajadas"] if r["horas_trabajadas"] else "-", color="black")),
                ft.DataCell(ft.Container(bgcolor=tarde_color, padding=5, border_radius=5, content=ft.Text(r["llego_tarde"], color="white"))),
            ]))
        self.table.rows = rows
        self.page.update()

    # LIMPIAR FILTROS
    def limpiar_filtros(self, e):
        self.f_inicio.value = ""
        self.f_fin.value = ""
        self.f_texto.value = ""
        self.f_tarde.value = False
        self.cargar_tabla()

    # EXPORTAR ARCHIVO WEB (descarga directa, compatible con Railway)
    def exportar_archivo_web(self, tipo):
        f_inicio = self.f_inicio.value.strip() if self.f_inicio.value else None
        f_fin = self.f_fin.value.strip() if self.f_fin.value else None

        filas = database.consultar_asistencias(f_inicio=f_inicio, f_fin=f_fin)
        texto = self.f_texto.value.strip().lower() if self.f_texto.value else ""
        if texto:
            filas = [f for f in filas if texto in f["nombre"].lower() or texto in f["cedula"].lower()]
        if self.f_tarde.value:
            filas = [f for f in filas if f["llego_tarde"] == "SI"]

        if not filas:
            self.mostrar_snackbar("⚠️ No hay datos para exportar", "#C62828")
            return

        # Generar archivo temporal
        if tipo == "excel":
            datos = [{"Nombre": r["nombre"], "Cédula": r["cedula"], "Fecha": str(r["fecha"]), "Turno": r["turno"],
                      "Llegada": str(r["hora_llegada"]) if r["hora_llegada"] else "-", "Salida": str(r["hora_salida"]) if r["hora_salida"] else "-",
                      "Horas": r["horas_trabajadas"] if r["horas_trabajadas"] else "-", "Tarde": r["llego_tarde"]} for r in filas]
            archivo_path = exportar_excel(datos)
        else:
            datos = [[r["nombre"], r["cedula"], str(r["fecha"]), r["turno"],
                      str(r["hora_llegada"]) if r["hora_llegada"] else "-", str(r["hora_salida"]) if r["hora_salida"] else "-",
                      r["horas_trabajadas"] if r["horas_trabajadas"] else "-", r["llego_tarde"]] for r in filas]
            archivo_path = exportar_pdf(datos)

        # Convertir a base64 y crear enlace de descarga
        with open(archivo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        href = f"data:application/octet-stream;base64,{b64}"
        filename = Path(archivo_path).name

        # Descargar directamente en el navegador
        self.page.launch_url(href, new_tab=False)
        self.mostrar_snackbar(f"✅ Archivo {tipo.upper()} listo para descargar", "#2E7D32")

    # SNACKBAR
    def mostrar_snackbar(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
