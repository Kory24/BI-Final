from sqlalchemy import create_engine, text

# --- CONFIGURACIÓN ---
USUARIO = 'bi_user'
PASSWORD = 'bi_pass'  
HOST = 'localhost'
PUERTO = '3310'
BASE_DATOS = 'bi_software_dwh'

cadena_conexion = f"mysql+pymysql://{USUARIO}:{PASSWORD}@{HOST}:{PUERTO}/{BASE_DATOS}"
engine = create_engine(cadena_conexion)

print("--- INICIANDO LIMPIEZA TOTAL DE LA BASE DE DATOS ---")

with engine.connect() as conn:
    # 1. Apagamos el seguro
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    print(" -> Seguro de llaves foráneas DESACTIVADO.")

    # 2. Borramos las tablas (TRUNCATE)
    tablas = [
        "Fact_Defectos_Calidad",
        "Fact_Trazabilidad_Esfuerzo",
        "Dim_Proyecto",
        "Dim_Empleado",
        "Dim_Proceso_Interno",
        "Dim_Cliente",
        "Dim_Tiempo"
    ]

    for tabla in tablas:
        try:
            conn.execute(text(f"TRUNCATE TABLE {tabla};"))
            print(f" -> Tabla '{tabla}' vaciada correctamente.")
        except Exception as e:
            print(f" -> Error vaciando {tabla}: {e}")

    # 3. Encendemos el seguro de nuevo
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    print(" -> Seguro de llaves foráneas REACTIVADO.")
    
    # Confirmar cambios (aunque truncate es autocommit, es buena práctica en scripts)
    conn.commit()

print("--- ¡LIMPIEZA COMPLETADA! BASE DE DATOS COMO NUEVA ---")