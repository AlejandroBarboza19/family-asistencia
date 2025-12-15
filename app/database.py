# database.py
# PostgreSQL Railway - Sistema de Asistencia + Login

import psycopg2
import psycopg2.extras
import datetime
from typing import List, Optional
import bcrypt

# =========================
# CONFIGURACIÓN DATABASE
# =========================

DATABASE_URL = "postgresql://postgres:BDgnfVbngAljWYPjXyeKHlXeLtPjcdAq@gondola.proxy.rlwy.net:17526/railway"

# =========================
# CONEXIÓN
# =========================

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# =========================
# TURNOS
# =========================

TURNOS = {
    "DIA": {
        "nombre": "Turno Día",
        "inicio": datetime.time(9, 0, 0),
        "fin": datetime.time(16, 0, 0),
        "limite_tarde": datetime.time(9, 10, 0)
    },
    "NOCHE": {
        "nombre": "Turno Noche",
        "inicio": datetime.time(16, 0, 0),
        "fin": datetime.time(23, 0, 0),
        "limite_tarde": datetime.time(16, 10, 0)
    }
}

def detectar_turno_automatico(hora: datetime.time) -> str:
    return "DIA" if hora < datetime.time(16, 0, 0) else "NOCHE"

# =========================
# CREACIÓN DE TABLAS
# =========================

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    # EMPLEADOS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            numero TEXT,
            activo BOOLEAN DEFAULT TRUE
        );
    """)

    # ASISTENCIAS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id SERIAL PRIMARY KEY,
            empleado_id INTEGER REFERENCES empleados(id) ON DELETE CASCADE,
            fecha DATE NOT NULL,
            hora_llegada TIME,
            hora_salida TIME,
            turno TEXT NOT NULL,
            llego_tarde TEXT DEFAULT 'NO',
            horas_trabajadas TEXT
        );
    """)

    # USUARIOS (LOGIN)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol VARCHAR(20) NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# =========================
# USUARIOS (LOGIN)
# =========================

def crear_usuario(username: str, password: str, rol: str):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO usuarios (username, password_hash, rol)
        VALUES (%s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
    """, (username, password_hash, rol))

    conn.commit()
    cur.close()
    conn.close()

def autenticar_usuario(username: str, password: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, password_hash, rol
        FROM usuarios
        WHERE username = %s AND activo = TRUE
    """, (username,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return None

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {
            "id": user["id"],
            "username": user["username"],
            "rol": user["rol"]
        }

    return None

# =========================
# CRUD EMPLEADOS
# =========================

def crear_empleado(nombre: str, cedula: str, numero: str = "") -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO empleados (nombre, cedula, numero)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (nombre.strip(), cedula.strip(), numero.strip()))

    emp_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()

    return emp_id

def obtener_empleados() -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nombre, cedula, numero
        FROM empleados
        WHERE activo = TRUE
        ORDER BY nombre
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# =========================
# MARCACIONES
# =========================

def registrar_llegada(empleado_id: int) -> dict:
    ahora = datetime.datetime.now()
    fecha = ahora.date()
    hora = ahora.time()

    turno_key = detectar_turno_automatico(hora)
    turno = TURNOS[turno_key]
    llego_tarde = "SI" if hora > turno["limite_tarde"] else "NO"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO asistencias
        (empleado_id, fecha, hora_llegada, turno, llego_tarde)
        VALUES (%s, %s, %s, %s, %s)
    """, (empleado_id, fecha, hora, turno["nombre"], llego_tarde))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "fecha": str(fecha),
        "hora": hora.strftime("%H:%M:%S"),
        "turno": turno["nombre"],
        "tarde": llego_tarde
    }

# =========================
# CONSULTAR ASISTENCIAS CON FILTROS
# =========================

def consultar_asistencias(
    f_inicio: str,
    f_fin: str,
    texto: str = "",
    solo_tarde: bool = False
) -> List[dict]:
    """
    Retorna asistencias entre fechas f_inicio y f_fin,
    filtrando opcionalmente por texto (nombre o cédula) y solo llegadas tarde.
    """
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT a.id, e.nombre, e.cedula, a.fecha, a.hora_llegada, a.hora_salida, a.turno, a.llego_tarde, a.horas_trabajadas
        FROM asistencias a
        JOIN empleados e ON a.empleado_id = e.id
        WHERE a.fecha BETWEEN %s AND %s
    """
    params = [f_inicio, f_fin]

    if texto:
        query += " AND (e.nombre ILIKE %s OR e.cedula ILIKE %s)"
        params += [f"%{texto}%", f"%{texto}%"]

    if solo_tarde:
        query += " AND a.llego_tarde = 'SI'"

    query += " ORDER BY a.fecha, e.nombre"

    cur.execute(query, params)
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    return resultados

# =========================
# INICIALIZACIÓN AUTOMÁTICA
# =========================

if __name__ == "__main__":
    print("🔄 Inicializando base de datos...")
    initialize_database()

    print("👤 Creando usuarios por defecto...")
    crear_usuario("admin", "123456", "admin")
    crear_usuario("jefe", "654321", "jefe")

    print("✅ Base de datos lista y funcionando")
