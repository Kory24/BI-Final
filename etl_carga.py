import pandas as pd
from sqlalchemy import create_engine
import os

# --- 1. CONFIGURACIÓN DE CONEXIÓN A MYSQL ---
USUARIO = 'bi_user'
PASSWORD = 'bi_pass'  
HOST = 'localhost'
PUERTO = '3310'
BASE_DATOS = 'bi_software_dwh'

# Crear la cadena de conexión
cadena_conexion = f"mysql+pymysql://{USUARIO}:{PASSWORD}@{HOST}:{PUERTO}/{BASE_DATOS}"
engine = create_engine(cadena_conexion)

# --- 2. LISTA DE ARCHIVOS A CARGAR (EN ORDEN) ---
# El orden es CRÍTICO: Primero las Dimensiones, luego los Hechos
archivos_carga = [
    ('Dim_Tiempo.csv', 'Dim_Tiempo'),
    ('Dim_Cliente.csv', 'Dim_Cliente'),
    ('Dim_Empleado.csv', 'Dim_Empleado'),
    ('Dim_Proceso_Interno.csv', 'Dim_Proceso_Interno'),
    ('Dim_Proyecto.csv', 'Dim_Proyecto'),
    ('Fact_Trazabilidad_Esfuerzo_BASE.csv', 'Fact_Trazabilidad_Esfuerzo'),
    ('Fact_Defectos_Calidad.csv', 'Fact_Defectos_Calidad')
]

# --- 3. PROCESO DE CARGA ---
print("--- INICIANDO PROCESO ETL DE CARGA ---")

try:
    with engine.connect() as conn:
        for archivo, tabla in archivos_carga:
            if os.path.exists(archivo):
                print(f"Cargando {archivo} en tabla '{tabla}'...")
                
                # Leer CSV con Pandas
                df = pd.read_csv(archivo)
                
                # Cargar a SQL
                # if_exists='append' agrega los datos a la tabla ya creada por tu script SQL
                # index=False evita que suba el índice de pandas como columna
                df.to_sql(name=tabla, con=engine, if_exists='append', index=False)
                
                print(f" -> Éxito: {len(df)} filas insertadas.")
            else:
                print(f" -> ERROR: El archivo {archivo} no existe.")

    print("\n--- ¡CARGA ETL COMPLETADA EXITOSAMENTE! ---")

except Exception as e:
    print(f"\nFATAL ERROR DURANTE LA CARGA: {e}")
    print("Asegúrate de que la base de datos existe y las tablas están creadas.")