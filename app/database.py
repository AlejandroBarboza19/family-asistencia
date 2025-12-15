# database.py
# Manejo de la base de datos SQLite con sistema de turnos mejorado

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

DB_PATH = Path(__file__).parent / "data.db"

# Definición de turnos
TURNOS = {
    "DIA": {
        "nombre": "Turno Día",
        "inicio": "09:00:00",
        "fin": "16:00:00",
        "limite_tarde": "09:10:00"
    },
    "NOCHE": {
        "nombre": "Turno Noche",
        "inicio": "16:00:00",
        "fin": "23:00:00",
        "limite_tarde": "16:10:00"
    }
}

def detectar_turno_automatico(hora_str: str) -> str:
    """Detecta automáticamente el turno según la hora de llegada."""
    h = datetime.strptime(hora_str, "%H:%M:%S").time()
    hora_16 = time(16, 0, 0)
    return "DIA" if h < hora_16 else "NOCHE"

def get_connection():
    """Abrir conexión SQLite (archivo persistente)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Crear archivo y tablas si no existen."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla empleados
    c.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cedula TEXT UNIQUE NOT NULL,
        numero TEXT,
        activo INTEGER DEFAULT 1
    );
    """)
    
    # Tabla asistencias
    c.execute("""
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        hora_llegada TEXT,
        hora_salida TEXT,
        turno TEXT NOT NULL,
        llego_tarde TEXT DEFAULT 'NO',
        horas_trabajadas TEXT,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    );
    """)
    
    conn.commit()
    conn.close()

# ---------- CRUD Empleados ----------
def crear_empleado(nombre: str, cedula: str, numero: str = "") -> int:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO empleados (nombre, cedula, numero) VALUES (?, ?, ?)",
                  (nombre.strip(), cedula.strip(), numero.strip()))
        conn.commit()
        emp_id = c.lastrowid
    except sqlite3.IntegrityError:
        c.execute("SELECT id FROM empleados WHERE cedula = ?", (cedula.strip(),))
        row = c.fetchone()
        emp_id = row["id"] if row else None
    conn.close()
    return emp_id

def actualizar_empleado(emp_id: int, nombre: str, cedula: str, numero: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE empleados SET nombre = ?, cedula = ?, numero = ? WHERE id = ?",
              (nombre.strip(), cedula.strip(), numero.strip(), emp_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def eliminar_empleado(emp_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM asistencias WHERE empleado_id = ?", (emp_id,))
    c.execute("DELETE FROM empleados WHERE id = ?", (emp_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def obtener_empleados() -> List[sqlite3.Row]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, nombre, cedula, numero FROM empleados WHERE activo = 1 ORDER BY nombre COLLATE NOCASE")
    rows = c.fetchall()
    conn.close()
    return rows

def obtener_empleado_por_cedula(cedula: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM empleados WHERE cedula = ? AND activo = 1", (cedula.strip(),))
    row = c.fetchone()
    conn.close()
    return row

def obtener_empleado_por_id(emp_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM empleados WHERE id = ?", (emp_id,))
    row = c.fetchone()
    conn.close()
    return row

# ---------- Sistema de Marcación con Turnos ----------
def obtener_asistencia_hoy(empleado_id: int) -> Optional[sqlite3.Row]:
    """Verifica si el empleado ya tiene registro hoy."""
    hoy = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM asistencias WHERE empleado_id = ? AND fecha = ?", (empleado_id, hoy))
    row = c.fetchone()
    conn.close()
    return row

def registrar_llegada(empleado_id: int) -> dict:
    """Registra la hora de llegada del empleado con detección automática de turno."""
    ahora = datetime.now(ZoneInfo("America/Bogota"))
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")
    
    turno_key = detectar_turno_automatico(hora)
    turno_info = TURNOS[turno_key]

    limite_tarde = turno_info["limite_tarde"]
    llego_tarde = "SI" if hora > limite_tarde else "NO"

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO asistencias (empleado_id, fecha, hora_llegada, turno, llego_tarde)
        VALUES (?, ?, ?, ?, ?)
    """, (empleado_id, fecha, hora, turno_info["nombre"], llego_tarde))
    conn.commit()
    conn.close()

    return {
        "fecha": fecha,
        "hora": hora,
        "tipo": "LLEGADA",
        "turno": turno_info["nombre"],
        "tarde": llego_tarde
    }

def registrar_salida(empleado_id: int) -> dict:
    """Registra la hora de salida del empleado."""
    hoy = date.today().strftime("%Y-%m-%d")
    ahora = datetime.now(ZoneInfo("America/Bogota"))
    hora_salida = ahora.strftime("%H:%M:%S")

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM asistencias WHERE empleado_id = ? AND fecha = ?", (empleado_id, hoy))
    registro = c.fetchone()

    if registro and registro["hora_llegada"]:
        hora_llegada = datetime.strptime(registro["hora_llegada"], "%H:%M:%S")
        hora_sal = datetime.strptime(hora_salida, "%H:%M:%S")
        delta = hora_sal - hora_llegada
        horas_trabajadas = str(delta).split('.')[0]

        c.execute("""
            UPDATE asistencias 
            SET hora_salida = ?, horas_trabajadas = ?
            WHERE id = ?
        """, (hora_salida, horas_trabajadas, registro["id"]))
        conn.commit()
        conn.close()

        return {"fecha": hoy, "hora": hora_salida, "tipo": "SALIDA", "horas": horas_trabajadas}

    conn.close()
    return None

# ---------- Consultas para reportes ----------
def consultar_asistencias(f_inicio: str = None, f_fin: str = None,
                          filtro_texto: str = None, solo_tarde: bool = False) -> List[sqlite3.Row]:
    """Devuelve asistencias con los datos del empleado."""
    conn = get_connection()
    c = conn.cursor()
    sql = """
    SELECT 
        a.id, 
        e.nombre, 
        e.cedula, 
        a.fecha, 
        a.hora_llegada,
        a.hora_salida,
        a.horas_trabajadas,
        a.turno, 
        a.llego_tarde
    FROM asistencias a
    JOIN empleados e ON e.id = a.empleado_id
    WHERE 1=1
    """
    params = []

    if f_inicio:
        sql += " AND fecha >= ?"
        params.append(f_inicio)
    if f_fin:
        sql += " AND fecha <= ?"
        params.append(f_fin)
    if filtro_texto:
        sql += " AND (e.nombre LIKE ? OR e.cedula LIKE ?)"
        like = f"%{filtro_texto}%"
        params.extend([like, like])
    if solo_tarde:
        sql += " AND a.llego_tarde = 'SI'"

    sql += " ORDER BY a.fecha DESC, a.hora_llegada DESC"
    c.execute(sql, tuple(params))
    rows = c.fetchall()
    conn.close()
    return rows

# Inicializar al importar
initialize_database()

if __name__ == "__main__":
    print("Inicializado DB en:", DB_PATH)
    print("Turnos configurados:", TURNOS)
