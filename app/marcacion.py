# marcacion.py
# Pantalla de marcación con diseño premium

import flet as ft
import database
from datetime import datetime
import threading
import time
from diseño_premium import (
    COLORS, GlassCard, PremiumButton, PremiumTextField,
    Badge
)

class MarcacionView:
    def __init__(self, page, on_refresh_callback):
        self.page = page
        self.on_refresh = on_refresh_callback
        self.empleado_actual = None
        self.reloj_activo = True
        self.build_ui()
        self.iniciar_reloj()
    
    def build_ui(self):
        # Campo de cédula premium
        self.cedula_input = PremiumTextField(
            label="Ingrese su cédula",
            hint_text="Ej: 1234567890",
            width=450,
            on_submit=self.buscar_empleado,
            prefix_icon=ft.Icons.CREDIT_CARD_ROUNDED,
        )
        
        # Botón de búsqueda premium
        self.btn_buscar = PremiumButton(
            "Buscar Empleado",
            icon=ft.Icons.SEARCH_ROUNDED,
            on_click=self.buscar_empleado,
            width=200,
        )
        
        # Información del empleado con glassmorphism
        self.info_empleado = ft.Container(
            visible=False,
            content=GlassCard(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.PERSON_ROUNDED,
                                size=60,
                                color=COLORS["text_primary"],
                            ),
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.Alignment(-1, -1),
                                end=ft.alignment.Alignment(1, 1),
                                colors=[COLORS["gradient_start"], COLORS["gradient_mid"]],
                            ),
                            width=100,
                            height=100,
                            border_radius=50,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "",
                            size=15,
                            color=COLORS["text_secondary"],
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                padding=32,
            ),
        )
        
        # Botones de acción premium
        self.btn_llegada = PremiumButton(
            "MARCAR LLEGADA",
            icon=ft.Icons.LOGIN_ROUNDED,
            on_click=self.marcar_llegada,
            width=300,
            height=60,
        )
        
        self.btn_salida = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=20, color=COLORS["text_primary"]),
                    ft.Text(
                        "MARCAR SALIDA",
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color=COLORS["text_primary"],
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, 0),
                end=ft.alignment.Alignment(1, 0),
                colors=[COLORS["warning"], "#FB923C"],
            ),
            padding=15,
            border_radius=12,
            width=300,
            height=60,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=COLORS["warning"] + "60",
                offset=ft.Offset(0, 6),
            ),
            on_click=self.marcar_salida,
            ink=True,
        )
        
        self.botones_accion = ft.Container(
            visible=False,
            content=ft.Column(
                [
                    self.btn_llegada,
                    self.btn_salida,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
        )
        
        # Mensaje de estado
        self.mensaje_estado = ft.Container(
            visible=False,
            content=ft.Text(
                "",
                size=15,
                color=COLORS["text_secondary"],
                text_align=ft.TextAlign.CENTER,
            ),
        )
        
        # Reloj con gradiente
        self.reloj = ft.Container(
            content=ft.Text(
                datetime.now().strftime("%H:%M:%S"),
                size=56,
                weight=ft.FontWeight.BOLD,
                color=COLORS["text_primary"],
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, 0),
                end=ft.alignment.Alignment(1, 0),
                colors=[COLORS["gradient_start"], COLORS["gradient_mid"], COLORS["gradient_end"]],
            ),
            padding=24,
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=30,
                color=COLORS["accent_purple"] + "40",
            ),
        )
        
        # Indicador de turno
        self.turno_badge = Badge("", icon=ft.Icons.WB_SUNNY_ROUNDED)
        
        # Fecha en español
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        ahora = datetime.now()
        dia_semana = dias[ahora.weekday()]
        mes = meses[ahora.month - 1]
        
        self.fecha = ft.Text(
            f"{dia_semana}, {ahora.day} de {mes} de {ahora.year}",
            size=16,
            color=COLORS["text_secondary"],
        )
        
        # Actualizar turno inicial
        self.actualizar_turno()
        
        # Layout principal con scroll
        self.container = ft.Container(
            content=ft.Column(
                [
                    # Header con reloj
                    ft.Container(
                        content=ft.Column(
                            [
                                self.reloj,
                                ft.Container(height=12),
                                self.fecha,
                                ft.Container(height=16),
                                self.turno_badge,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(bottom=30),
                    ),
                    
                    # Título
                    ft.Text(
                        "Sistema de Marcación",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text_primary"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Ingrese su cédula para registrar su asistencia",
                        size=15,
                        color=COLORS["text_secondary"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    
                    ft.Container(height=30),
                    
                    # Búsqueda
                    ft.Row(
                        [
                            self.cedula_input,
                            self.btn_buscar,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=16,
                    ),
                    
                    ft.Container(height=40),
                    
                    # Info empleado
                    self.info_empleado,
                    
                    ft.Container(height=20),
                    
                    # Mensaje de estado
                    self.mensaje_estado,
                    
                    ft.Container(height=24),
                    
                    # Botones de acción
                    self.botones_accion,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
        )
    
    def iniciar_reloj(self):
        """Inicia el reloj en tiempo real."""
        def actualizar():
            while self.reloj_activo:
                try:
                    self.reloj.content.value = datetime.now().strftime("%H:%M:%S")
                    self.actualizar_turno()
                    self.page.update()
                except:
                    break
                time.sleep(1)
        
        hilo = threading.Thread(target=actualizar, daemon=True)
        hilo.start()
    
    def actualizar_turno(self):
        """Actualiza el badge del turno actual."""
        from database import detectar_turno_automatico, TURNOS
        
        # ✅ CORRECTO: Usar datetime.time(), no string
        hora_actual = datetime.now().time()
        turno_key = detectar_turno_automatico(hora_actual)
        turno_info = TURNOS[turno_key]
        
        if turno_key == "DIA":
            self.turno_badge = Badge(
                f"TURNO DÍA  {turno_info['inicio'].strftime('%H:%M')} - {turno_info['fin'].strftime('%H:%M')}",
                color_start=COLORS["warning"],
                color_end="#FB923C",
                icon=ft.Icons.WB_SUNNY_ROUNDED,
            )
        else:
            self.turno_badge = Badge(
                f"TURNO NOCHE  {turno_info['inicio'].strftime('%H:%M')} - {turno_info['fin'].strftime('%H:%M')}",
                color_start=COLORS["accent_purple"],
                color_end=COLORS["accent_blue"],
                icon=ft.Icons.NIGHTLIGHT_ROUNDED,
            )
    
    def buscar_empleado(self, e):
        """Busca un empleado por cédula."""
        cedula = (self.cedula_input.value or "").strip()
        
        if not cedula:
            self.mostrar_snackbar("⚠️ Por favor ingrese una cédula")
            return
        
        # Buscar empleado en la base de datos
        empleados = database.obtener_empleados()
        empleado = None
        
        for emp in empleados:
            if emp["cedula"] == cedula:
                empleado = emp
                break
        
        if not empleado:
            self.mostrar_snackbar("❌ Empleado no encontrado")
            self.ocultar_info()
            return
        
        self.empleado_actual = empleado
        self.mostrar_info_empleado()
    
    def mostrar_info_empleado(self):
        """Muestra la información del empleado y opciones de marcación."""
        if not self.empleado_actual:
            return
        
        info_col = self.info_empleado.content.content
        info_col.controls[2].value = self.empleado_actual["nombre"]
        info_col.controls[3].value = f"📱 {self.empleado_actual['cedula']}"
        
        self.info_empleado.visible = True
        
        # Verificar si ya tiene registro hoy
        conn = database.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT hora_llegada, hora_salida
            FROM asistencias
            WHERE empleado_id = %s AND fecha = %s
        """, (self.empleado_actual["id"], datetime.now().date()))
        
        registro_hoy = cur.fetchone()
        cur.close()
        conn.close()
        
        if not registro_hoy:
            # No tiene registro, puede marcar llegada
            self.btn_llegada.visible = True
            self.btn_salida.visible = False
            self.mensaje_estado.content.value = "✨ Bienvenido! Registre su llegada"
            self.mensaje_estado.content.color = COLORS["success"]
        elif registro_hoy["hora_salida"]:
            # Ya completó la jornada
            self.btn_llegada.visible = False
            self.btn_salida.visible = False
            self.mensaje_estado.content.value = f"✅ Jornada completa\nLlegada: {registro_hoy['hora_llegada']} | Salida: {registro_hoy['hora_salida']}"
            self.mensaje_estado.content.color = COLORS["text_secondary"]
        else:
            # Ya marcó llegada, puede marcar salida
            self.btn_llegada.visible = False
            self.btn_salida.visible = True
            self.mensaje_estado.content.value = f"⏰ Llegada: {registro_hoy['hora_llegada']}\nAhora puede marcar su salida"
            self.mensaje_estado.content.color = COLORS["warning"]
        
        self.mensaje_estado.visible = True
        self.botones_accion.visible = True
        self.page.update()
    
    def marcar_llegada(self, e):
        """Registra la llegada del empleado."""
        if not self.empleado_actual:
            return
        
        resultado = database.registrar_llegada(self.empleado_actual["id"])
        
        if resultado['tarde'] == "SI":
            mensaje = f"⚠️ Llegada registrada (TARDE)\n{resultado['hora']} - {resultado['turno']}"
        else:
            mensaje = f"✅ Llegada registrada\n{resultado['hora']} - {resultado['turno']}"
        
        self.mostrar_snackbar(mensaje)
        self.limpiar_formulario()
        if self.on_refresh:
            self.on_refresh()
    
    def marcar_salida(self, e):
        """Registra la salida del empleado."""
        if not self.empleado_actual:
            return
        
        # Calcular horas trabajadas
        conn = database.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE asistencias
            SET hora_salida = %s
            WHERE empleado_id = %s AND fecha = %s AND hora_salida IS NULL
            RETURNING hora_llegada, hora_salida
        """, (datetime.now().time(), self.empleado_actual["id"], datetime.now().date()))
        
        resultado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if resultado:
            # Calcular horas trabajadas
            llegada = datetime.combine(datetime.now().date(), resultado["hora_llegada"])
            salida = datetime.combine(datetime.now().date(), resultado["hora_salida"])
            diferencia = salida - llegada
            horas = diferencia.total_seconds() / 3600
            
            mensaje = f"👋 Salida registrada\n{resultado['hora_salida'].strftime('%H:%M:%S')} | Trabajadas: {horas:.2f}h"
            self.mostrar_snackbar(mensaje)
            self.limpiar_formulario()
            if self.on_refresh:
                self.on_refresh()
        else:
            self.mostrar_snackbar("❌ Error al registrar salida")
    
    def ocultar_info(self):
        """Oculta la información del empleado."""
        self.info_empleado.visible = False
        self.botones_accion.visible = False
        self.mensaje_estado.visible = False
        self.page.update()
    
    def limpiar_formulario(self):
        """Limpia el formulario y resetea el estado."""
        self.cedula_input.value = ""
        self.empleado_actual = None
        self.ocultar_info()
    
    def mostrar_snackbar(self, mensaje):
        """Muestra un mensaje en el snackbar."""
        self.page.snack_bar.content.value = mensaje
        self.page.snack_bar.open = True
        self.page.update()