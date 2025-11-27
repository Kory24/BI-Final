import pandas as pd
from sqlalchemy import create_engine, text

# 1. CREAMOS EL MOTOR SQLITE (Esto creará un archivo 'proyecto_bi.db')
engine = create_engine('sqlite:///proyecto_bi.db')

print("--- INICIANDO MIGRACIÓN A SQLITE ---")

# 2. LISTA DE ARCHIVOS CSV A CARGAR
# Asegúrate de que estos archivos existan en tu carpeta (ya los generaste con simulacion_dwh.py)
archivos = [
    'Dim_Tiempo.csv', 
    'Dim_Cliente.csv', 
    'Dim_Empleado.csv', 
    'Dim_Proceso_Interno.csv', 
    'Dim_Proyecto.csv', 
    'Fact_Trazabilidad_Esfuerzo_BASE.csv', 
    'Fact_Defectos_Calidad.csv'
]

# Diccionario para corregir nombres de tablas (si los CSV tienen nombres distintos)
nombres_tablas = {
    'Fact_Trazabilidad_Esfuerzo_BASE.csv': 'Fact_Trazabilidad_Esfuerzo'
}

with engine.connect() as conn:
    for archivo in archivos:
        try:
            nombre_tabla = nombres_tablas.get(archivo, archivo.replace('.csv', ''))
            print(f"Cargando {archivo} en tabla '{nombre_tabla}'...")
            
            df = pd.read_csv(archivo)
            # 'replace' borrará la tabla si existe y la creará de nuevo automáticamente
            df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
            print(" -> OK")
        except Exception as e:
            print(f" -> ERROR cargando {archivo}: {e}")

    # 3. CREAR LAS VISTAS (SQLITE SOPORTA VISTAS ESTÁNDAR)
    print("Creando Vistas de Negocio...")
    
    # Vista 1: Calidad
    sql_v1 = """
    CREATE VIEW IF NOT EXISTS Vista_Calidad_Defectos AS
    SELECT 
        P.nombre_proyecto, P.nivel_madurez_aplicado, FD.severidad,
        COUNT(FD.id_defecto) AS Total_Defectos,
        AVG(FD.tiempo_neto_horas) AS Promedio_Horas_Resolucion_MTTR
    FROM Fact_Defectos_Calidad FD
    JOIN Dim_Proyecto P ON FD.id_proyecto = P.id_proyecto
    GROUP BY P.nombre_proyecto, P.nivel_madurez_aplicado, FD.severidad;
    """
    
    # Vista 2: Finanzas
    sql_v2 = """
    CREATE VIEW IF NOT EXISTS Vista_Desempeño_Proyectos AS
    SELECT 
        P.nombre_proyecto, P.estado_actual, C.nombre_cliente,
        P.presupuesto_total_mxn AS Presupuesto_Original,
        SUM(FE.costo_imputado) AS Costo_Real_Actual,
        CASE WHEN SUM(FE.costo_imputado) > P.presupuesto_total_mxn THEN 'Sobre Costo' ELSE 'En Presupuesto' END AS Estatus_Financiero
    FROM Dim_Proyecto P
    JOIN Fact_Trazabilidad_Esfuerzo FE ON P.id_proyecto = FE.id_proyecto
    JOIN Dim_Cliente C ON P.id_cliente = C.id_cliente
    GROUP BY P.id_proyecto, P.nombre_proyecto, P.estado_actual, C.nombre_cliente, P.presupuesto_total_mxn;
    """
    
    # Vista 3: BSC
    sql_v3 = """
    CREATE VIEW IF NOT EXISTS Vista_Balanced_Scorecard AS
    SELECT 'Financiera' AS Perspectiva, 'Rentabilidad' AS KPI, 85.0 AS Valor_Actual
    UNION ALL
    SELECT 'Clientes', 'Satisfacción', 90.0
    UNION ALL
    SELECT 'Procesos', 'Eficiencia MTTR', 78.5
    UNION ALL
    SELECT 'Aprendizaje', 'Capacitación', 65.0;
    """

    conn.execute(text(sql_v1))
    conn.execute(text(sql_v2))
    conn.execute(text(sql_v3))
    print(" -> Vistas Creadas Correctamente")

print("--- MIGRACIÓN COMPLETADA: 'proyecto_bi.db' LISTO ---")