# database.py
# Manejo de la base de datos PostgreSQL con sistema de turnos mejorado

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
import os

# URL de conexión desde variable de entorno o directa
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:BDgnfVbngAljWYPjXyeKHlXeLtPjcdAq@gondola.proxy.rlwy.net:17526/railway"
)

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
    """Abrir conexión PostgreSQL."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def initialize_database():
    """Crear tablas si no existen."""
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla empleados
    c.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        cedula TEXT UNIQUE NOT NULL,
        numero TEXT,
        activo BOOLEAN DEFAULT TRUE
    );
    """)
    
    # Tabla asistencias
    c.execute("""
    CREATE TABLE IF NOT EXISTS asistencias (
        id SERIAL PRIMARY KEY,
        empleado_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        hora_llegada TIME,
        hora_salida TIME,
        turno TEXT NOT NULL,
        llego_tarde TEXT DEFAULT 'NO',
        horas_trabajadas TEXT,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    );
    """)
    
    # Índices para mejor rendimiento
    c.execute("""
    CREATE INDEX IF NOT EXISTS idx_asistencias_empleado_fecha 
    ON asistencias(empleado_id, fecha);
    """)
    
    c.execute("""
    CREATE INDEX IF NOT EXISTS idx_empleados_cedula 
    ON empleados(cedula);
    """)
    
    conn.commit()
    conn.close()

# ---------- CRUD Empleados ----------
def crear_empleado(nombre: str, cedula: str, numero: str = "") -> int:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO empleados (nombre, cedula, numero) 
            VALUES (%s, %s, %s) RETURNING id
        """, (nombre.strip(), cedula.strip(), numero.strip()))
        emp_id = c.fetchone()["id"]
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        c.execute("SELECT id FROM empleados WHERE cedula = %s", (cedula.strip(),))
        row = c.fetchone()
        emp_id = row["id"] if row else None
    finally:
        conn.close()
    return emp_id

def actualizar_empleado(emp_id: int, nombre: str, cedula: str, numero: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE empleados 
        SET nombre = %s, cedula = %s, numero = %s 
        WHERE id = %s
    """, (nombre.strip(), cedula.strip(), numero.strip(), emp_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def eliminar_empleado(emp_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM asistencias WHERE empleado_id = %s", (emp_id,))
    c.execute("DELETE FROM empleados WHERE id = %s", (emp_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def obtener_empleados() -> List[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, nombre, cedula, numero 
        FROM empleados 
        WHERE activo = TRUE 
        ORDER BY nombre
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def obtener_empleado_por_cedula(cedula: str) -> Optional[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM empleados 
        WHERE cedula = %s AND activo = TRUE
    """, (cedula.strip(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def obtener_empleado_por_id(emp_id: int) -> Optional[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM empleados WHERE id = %s", (emp_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

# ---------- Sistema de Marcación con Turnos ----------
def obtener_asistencia_hoy(empleado_id: int) -> Optional[Dict]:
    """Verifica si el empleado ya tiene registro hoy."""
    hoy = date.today()
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM asistencias 
        WHERE empleado_id = %s AND fecha = %s
    """, (empleado_id, hoy))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def registrar_llegada(empleado_id: int) -> dict:
    """Registra la hora de llegada del empleado con detección automática de turno."""
    ahora = datetime.now(ZoneInfo("America/Bogota"))
    fecha = ahora.date()
    hora = ahora.time()
    hora_str = hora.strftime("%H:%M:%S")
    
    turno_key = detectar_turno_automatico(hora_str)
    turno_info = TURNOS[turno_key]

    limite_tarde = turno_info["limite_tarde"]
    llego_tarde = "SI" if hora_str > limite_tarde else "NO"

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO asistencias (empleado_id, fecha, hora_llegada, turno, llego_tarde)
        VALUES (%s, %s, %s, %s, %s)
    """, (empleado_id, fecha, hora, turno_info["nombre"], llego_tarde))
    conn.commit()
    conn.close()

    return {
        "fecha": fecha.strftime("%Y-%m-%d"),
        "hora": hora_str,
        "tipo": "LLEGADA",
        "turno": turno_info["nombre"],
        "tarde": llego_tarde
    }

def registrar_salida(empleado_id: int) -> dict:
    """Registra la hora de salida del empleado."""
    hoy = date.today()
    ahora = datetime.now(ZoneInfo("America/Bogota"))
    hora_salida = ahora.time()
    hora_salida_str = hora_salida.strftime("%H:%M:%S")

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM asistencias 
        WHERE empleado_id = %s AND fecha = %s
    """, (empleado_id, hoy))
    registro = c.fetchone()

    if registro and registro["hora_llegada"]:
        # PostgreSQL maneja TIME automáticamente
        hora_llegada = registro["hora_llegada"]
        
        # Convertir a datetime para calcular diferencia
        hora_llegada_dt = datetime.combine(hoy, hora_llegada)
        hora_salida_dt = datetime.combine(hoy, hora_salida)
        delta = hora_salida_dt - hora_llegada_dt
        horas_trabajadas = str(delta).split('.')[0]

        c.execute("""
            UPDATE asistencias 
            SET hora_salida = %s, horas_trabajadas = %s
            WHERE id = %s
        """, (hora_salida, horas_trabajadas, registro["id"]))
        conn.commit()
        conn.close()

        return {
            "fecha": hoy.strftime("%Y-%m-%d"),
            "hora": hora_salida_str,
            "tipo": "SALIDA",
            "horas": horas_trabajadas
        }

    conn.close()
    return None

# ---------- Consultas para reportes ----------
def consultar_asistencias(f_inicio: str = None, f_fin: str = None,
                          filtro_texto: str = None, solo_tarde: bool = False) -> List[Dict]:
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
        sql += " AND fecha >= %s"
        params.append(f_inicio)
    if f_fin:
        sql += " AND fecha <= %s"
        params.append(f_fin)
    if filtro_texto:
        sql += " AND (e.nombre ILIKE %s OR e.cedula ILIKE %s)"
        like = f"%{filtro_texto}%"
        params.extend([like, like])
    if solo_tarde:
        sql += " AND a.llego_tarde = 'SI'"

    sql += " ORDER BY a.fecha DESC, a.hora_llegada DESC"
    c.execute(sql, tuple(params))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Inicializar al importar
try:
    initialize_database()
    print("✅ Base de datos PostgreSQL inicializada correctamente")
except Exception as e:
    print(f"❌ Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    print("Conexión PostgreSQL:", DATABASE_URL.split('@')[1])  # Oculta credenciales
    print("Turnos configurados:", TURNOS)