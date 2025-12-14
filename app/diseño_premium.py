# diseño_premium.py
# Diseño Dark Premium con Glassmorphism - Estilo Dashboard Moderno

import flet as ft

# === PALETA DE COLORES DARK PREMIUM ===
COLORS = {
    # Fondos base
    "bg_primary": "#FFFFFF",    # blanco principal
    "bg_secondary": "#F7F8FA",  # gris muy claro

    # Tarjetas, contenedores y vidrio
    "bg_card": "#FFFFFF",
    "glass": "#FFFFFFAA",       # vidrio suave blanco
    "glass_border": "#E5E7EB",  # bordecito gris claro

    # Texto
    "text_primary": "#000000",   # gris oscuro elegante
    "text_secondary": "#000000", # NEGRO
    "text_muted": "#000000",     # NEGRO

    # Colores de acento (pastel premium)
    "accent_blue": "#2563EB",    # azul moderno
    "accent_cyan": "#0891B2",    # cian
    "accent_green": "#10B981",   # verde esmeralda suave
    "accent_purple": "#6366F1",  # morado elegante (no chillón)
    "accent_orange": "#F97316",  # naranja suave

    # Advertencias / estados
    "success": "#22C55E",  # verde claro
    "warning": "#F59E0B",  # amarillo oscuro suave
    "danger": "#EF4444",   # rojo moderado

    # Gradientes (pasteles premium)
    "gradient_start": "#EFF6FF",
    "gradient_mid": "#DBEAFE",
    "gradient_end": "#BFDBFE",
}


# === COMPONENTE BASE CON GLASSMORPHISM ===
def GlassCard(content, gradient=False, **kwargs):

    begin_align = ft.alignment.Alignment(-1, -1)
    end_align = ft.alignment.Alignment(1, 1)

    if gradient:
        return ft.Container(
            content=content,
            gradient=ft.LinearGradient(
                begin=begin_align,
                end=end_align,
                colors=[
                    COLORS["gradient_start"],
                    COLORS["gradient_mid"],
                    COLORS["gradient_end"],
                ],
            ),
            padding=kwargs.get("padding", 24),
            border_radius=kwargs.get("border_radius", 20),
            border=ft.border.all(1, COLORS["glass_border"]),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=40,
                color=COLORS["accent_purple"] + "40",
                offset=ft.Offset(0, 10),
            ),
            **{k: v for k, v in kwargs.items() if k not in ["padding", "border_radius"]},
        )
    else:
        return ft.Container(
            content=content,
            bgcolor=COLORS["glass"],
            padding=kwargs.get("padding", 24),
            border_radius=kwargs.get("border_radius", 20),
            border=ft.border.all(1, COLORS["glass_border"]),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=30,
                color="#00000040",
                offset=ft.Offset(0, 8),
            ),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            **{k: v for k, v in kwargs.items() if k not in ["padding", "border_radius"]},
        )

# === BOTÓN PREMIUM CON GRADIENTE ===
def PremiumButton(text, on_click=None, icon=None, gradient=True, width=None, height=50, **kwargs):

    begin_align = ft.alignment.Alignment(-1, -1)
    end_align = ft.alignment.Alignment(1, 1)

    if gradient:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=20, color=COLORS["text_primary"]) if icon else ft.Container(),
                    ft.Text(text, size=15, weight=ft.FontWeight.W_600, color=COLORS["text_primary"]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            gradient=ft.LinearGradient(
                begin=begin_align,
                end=end_align,
                colors=[COLORS["gradient_start"], COLORS["gradient_mid"]],
            ),
            padding=15,
            border_radius=12,
            width=width,
            height=height,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=COLORS["accent_purple"] + "60",
                offset=ft.Offset(0, 6),
            ),
            on_click=on_click,
            ink=True,
            animate=ft.Animation(200, "easeOut"),
        )
    else:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=20, color=COLORS["text_secondary"]) if icon else ft.Container(),
                    ft.Text(text, size=15, weight=ft.FontWeight.W_500, color=COLORS["text_secondary"]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=COLORS["glass"],
            border=ft.border.all(1, COLORS["glass_border"]),
            padding=15,
            border_radius=12,
            width=width,
            height=height,
            on_click=on_click,
            ink=True,
            animate=ft.Animation(200, "easeOut"),
        )

# === INPUT FIELD PREMIUM ===
def PremiumTextField(label, **kwargs):
    return ft.TextField(
        label=label,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        text_style=ft.TextStyle(color=COLORS["text_primary"], size=15),
        border_radius=12,
        border_color=COLORS["glass_border"],
        focused_border_color=COLORS["accent_purple"],
        bgcolor=COLORS["glass"],
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
        cursor_color=COLORS["accent_purple"],
        **kwargs,
    )

# === STAT CARD CON GRADIENTE ===
def StatCard(title, value, icon, trend=None, gradient_colors=None):

    begin_align = ft.alignment.Alignment(-1, -1)
    end_align = ft.alignment.Alignment(1, 1)

    if gradient_colors is None:
        gradient_colors = [COLORS["gradient_start"], COLORS["gradient_mid"]]

    trend_widget = ft.Container()
    if trend:
        trend_color = COLORS["success"] if trend.startswith("+") else COLORS["error"]
        trend_widget = ft.Container(
            content=ft.Text(trend, size=12, weight=ft.FontWeight.BOLD, color=trend_color),
            bgcolor=trend_color + "20",
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=8,
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=28, color=COLORS["text_primary"]),
                            gradient=ft.LinearGradient(
                                begin=begin_align,
                                end=end_align,
                                colors=gradient_colors,
                            ),
                            width=56,
                            height=56,
                            border_radius=16,
                            alignment=ft.alignment.Alignment(0, 0),
                        ),
                        trend_widget,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=12),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                ft.Text(title, size=14, color=COLORS["text_secondary"], weight=ft.FontWeight.W_500),
            ],
            spacing=4,
        ),
        bgcolor=COLORS["glass"],
        border=ft.border.all(1, COLORS["glass_border"]),
        padding=20,
        border_radius=20,
        width=220,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=30,
            color="#00000030",
            offset=ft.Offset(0, 8),
        ),
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
    )

# === BADGE PREMIUM ===
def Badge(text, color_start=None, color_end=None, icon=None):

    begin_align = ft.alignment.Alignment(-1, 0)
    end_align = ft.alignment.Alignment(1, 0)

    if color_start is None:
        color_start = COLORS["gradient_start"]
        color_end = COLORS["gradient_mid"]

    content_items = []
    if icon:
        content_items.append(ft.Icon(icon, size=14, color=COLORS["text_primary"]))

    content_items.append(
        ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])
    )

    return ft.Container(
        content=ft.Row(content_items, spacing=6, tight=True),
        gradient=ft.LinearGradient(
            begin=begin_align,
            end=end_align,
            colors=[color_start, color_end],
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=20,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color=color_start + "40",
            offset=ft.Offset(0, 2),
        ),
    )

# === HEADER PREMIUM ===
def PremiumHeader(title, subtitle=None, icon=None, actions=None):

    begin_align = ft.alignment.Alignment(-1, -1)
    end_align = ft.alignment.Alignment(1, 1)

    content_items = []

    if icon:
        content_items.append(
            ft.Container(
                content=ft.Icon(icon, size=32, color=COLORS["text_primary"]),
                gradient=ft.LinearGradient(
                    begin=begin_align,
                    end=end_align,
                    colors=[COLORS["gradient_start"], COLORS["gradient_mid"]],
                ),
                width=60,
                height=60,
                border_radius=16,
                alignment=ft.alignment.Alignment(0, 0),
            )
        )

    text_column = [
        ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])
    ]

    if subtitle:
        text_column.append(ft.Text(subtitle, size=14, color=COLORS["text_secondary"]))

    content_items.append(ft.Column(text_column, spacing=4))

    return ft.Container(
        content=ft.Row(
            [
                ft.Row(content_items, spacing=16),
                ft.Row(actions if actions else [], spacing=12),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=COLORS["glass"],
        border=ft.border.all(1, COLORS["glass_border"]),
        padding=24,
        border_radius=20,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=30,
            color="#00000040",
            offset=ft.Offset(0, 8),
        ),
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
    )

# === SIDEBAR ITEM ===
def SidebarItem(icon, text, active=False, on_click=None, badge=None):

    if active:
        bg_color = COLORS["glass"]
        text_color = COLORS["text_primary"]
        icon_color = COLORS["accent_purple"]
    else:
        bg_color = "transparent"
        text_color = COLORS["text_secondary"]
        icon_color = COLORS["text_secondary"]

    badge_widget = ft.Container()
    if badge:
        badge_widget = ft.Container(
            content=ft.Text(badge, size=11, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            bgcolor=COLORS["accent_purple"],
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10,
        )

    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, size=22, color=icon_color),
                ft.Text(
                    text,
                    size=14,
                    weight=ft.FontWeight.W_500 if not active else ft.FontWeight.W_600,
                    color=text_color,
                ),
                badge_widget,
            ],
            spacing=12,
        ),
        bgcolor=bg_color,
        border=ft.border.all(1, COLORS["glass_border"]) if active else None,
        padding=12,
        border_radius=12,
        on_click=on_click,
        ink=True,
        animate=ft.Animation(150, "easeOut"),
    )
