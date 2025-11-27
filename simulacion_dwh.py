import pandas as pd
import numpy as np
from datetime import timedelta

# --- 1. CONFIGURACIÓN DE PARÁMETROS ---
N_EMPLEADOS = 10
N_CLIENTES = 8
N_PROYECTOS = 15
FECHA_INICIO_SIMULACION = pd.to_datetime('2024-01-01')
FECHA_FIN_SIMULACION = pd.to_datetime('2024-12-31')
HORIZONTE_TIEMPO = pd.date_range(FECHA_INICIO_SIMULACION, FECHA_FIN_SIMULACION, freq='D')
# Creamos fechas hasta Febrero 2025 para cubrir los cierres de defectos de fin de año
HORIZONTE_DIMENSION = pd.date_range(FECHA_INICIO_SIMULACION, '2025-02-28', freq='D')


# Función para predecir el número total de defectos (N)
# Usaremos una aproximación estocástica, donde la media de defectos
# es proporcional al esfuerzo estimado, modulado por la calidad del proceso.

def predecir_defectos_rayleigh(esfuerzo_estimado, nivel_madurez):
    # La tasa de defectos (defects per hour) esperada disminuye con la madurez.
    # Nivel 2 (Bajo): 0.1 defectos por cada 10 horas
    # Nivel 4 (Alto): 0.05 defectos por cada 10 horas
    
    # Factor_base: representa la media de defectos por hora
    if nivel_madurez == 4:
        factor_base = 0.005 # Procesos muy maduros tienen menos errores
    elif nivel_madurez == 3:
        factor_base = 0.01 
    else: # Nivel 2 o inferior
        factor_base = 0.02 # Procesos inmaduros tienen más errores
        
    # N_esperado = Esfuerzo * Tasa
    N_esperado = esfuerzo_estimado * factor_base
    
    # Usamos np.random.poisson para añadir variación realista (conteo de eventos)
    # y asegurarnos de que el resultado sea un entero.
    N_defectos_predichos = np.random.poisson(N_esperado)
    
    # Asegurar al menos 5 defectos para proyectos grandes
    return max(5, N_defectos_predichos)

# --- 2. GENERACIÓN DE DIMENSIONES ---

## Dim_Tiempo
print("Generando Dim_Tiempo...")
df_tiempo = pd.DataFrame({'fecha_completa': HORIZONTE_DIMENSION})
df_tiempo['id_tiempo'] = (df_tiempo['fecha_completa'].dt.strftime('%Y%m%d')).astype(int)
df_tiempo['dia_de_la_semana'] = df_tiempo['fecha_completa'].dt.day_name('es')
df_tiempo['semana_del_año'] = df_tiempo['fecha_completa'].dt.isocalendar().week.astype(int)
df_tiempo['mes_nombre_abreviado'] = df_tiempo['fecha_completa'].dt.strftime('%b')
df_tiempo['trimestre_num'] = df_tiempo['fecha_completa'].dt.quarter
df_tiempo['año'] = df_tiempo['fecha_completa'].dt.year
# Definir si es laboral (excluyendo Sábados y Domingos)
df_tiempo['es_laboral'] = ~df_tiempo['fecha_completa'].dt.dayofweek.isin([5, 6])
df_tiempo.to_csv('Dim_Tiempo.csv', index=False)


## Dim_Cliente
print("Generando Dim_Cliente...")
sectores = ['Finanzas', 'Retail', 'Salud', 'Tecnología', 'Educación']
contratos = ['Precio Fijo', 'Tiempo y Materiales', 'Suscripción']
df_cliente = pd.DataFrame({
    'id_cliente': range(1, N_CLIENTES + 1),
    'nombre_cliente': [f'Cliente_{i}' for i in range(1, N_CLIENTES + 1)],
    'sector': np.random.choice(sectores, N_CLIENTES),
    'tipo_contrato_principal': np.random.choice(contratos, N_CLIENTES)
})
df_cliente.to_csv('Dim_Cliente.csv', index=False)


## Dim_Empleado
print("Generando Dim_Empleado...")
roles = ['Líder de Proyecto', 'Desarrollador Senior', 'Desarrollador Mid', 'Desarrollador Junior', 'Tester QA']
seniority = ['Senior', 'Mid', 'Junior']
salarios = {
    'Desarrollador Junior': 250, 
    'Desarrollador Mid': 400, 
    'Desarrollador Senior': 600, 
    'Líder de Proyecto': 700, 
    'Tester QA': 350
}
df_empleado = pd.DataFrame({
    'id_empleado': range(1, N_EMPLEADOS + 1),
    'nombre_completo': [f'Empleado_{i}' for i in range(1, N_EMPLEADOS + 1)],
    'rol_en_la_empresa': np.random.choice(roles, N_EMPLEADOS),
    'seniority': np.random.choice(seniority, N_EMPLEADOS),
})
# Ajustar salario basado en rol/seniority
df_empleado['salario_hora_base'] = df_empleado['rol_en_la_empresa'].map(salarios)
df_empleado['equipo_asignado'] = np.random.choice(['Alpha', 'Beta', 'Gamma'], N_EMPLEADOS)
df_empleado.to_csv('Dim_Empleado.csv', index=False)


## Dim_Proceso_Interno (Clave para Madurez)
print("Generando Dim_Proceso_Interno...")
procesos_data = [
    (1, 'Definición de Requisitos', 'Análisis', 'Obligatorio'),
    (2, 'Diseño de Arquitectura', 'Diseño', 'Obligatorio'),
    (3, 'Desarrollo Backend', 'Implementación', 'Obligatorio'),
    (4, 'Desarrollo Frontend', 'Implementación', 'Obligatorio'),
    (5, 'Revisión de Código', 'Pruebas', 'Obligatorio'),
    (6, 'Pruebas QA (Funcionales)', 'Pruebas', 'Obligatorio'),
    (7, 'Despliegue en Producción', 'Despliegue', 'Obligatorio')
]
df_proceso = pd.DataFrame(procesos_data, columns=['id_proceso', 'nombre_proceso', 'fase_sdlc', 'indicador_cumplimiento'])
df_proceso['documentacion_link'] = 'http://docs.empresa.com/' + df_proceso['nombre_proceso'].str.replace(' ', '_')
df_proceso.to_csv('Dim_Proceso_Interno.csv', index=False)


## Dim_Proyecto (Clave para Rayleigh)
print("Generando Dim_Proyecto...")
proyectos_data = []
for i in range(1, N_PROYECTOS + 1):
    id_cliente = np.random.choice(df_cliente['id_cliente'])
    
    # Simular duración: entre 60 y 240 días
    duracion_dias = np.random.randint(60, 240)
    
    # Asignar fecha de inicio dentro del horizonte
    start_date = FECHA_INICIO_SIMULACION + timedelta(days=np.random.randint(0, 365 - duracion_dias))
    
    # La clave para Rayleigh: Esfuerzo Estimado (ej. 8 horas/día * duración * 4 empleados)
    esfuerzo_estimado = np.random.randint(200, 2000) # Rango de 200 a 2000 horas
    
    presupuesto = esfuerzo_estimado * np.random.uniform(400, 600) # Costo por hora promedio simulado
    
    proyectos_data.append({
        'id_proyecto': i,
        'id_cliente': id_cliente,
        'nombre_proyecto': f'Sistema_{i}',
        'estado_actual': np.random.choice(['Entregado', 'Activo'], p=[0.7, 0.3]),
        'esfuerzo_estimado_total': esfuerzo_estimado,
        'presupuesto_total_mxn': round(presupuesto, 2),
        'tipo_desarrollo': np.random.choice(['Web', 'Mobile', 'Integración']),
        'nivel_madurez_aplicado': np.random.choice([2, 3, 4], p=[0.2, 0.5, 0.3]) # Mayoría en Nivel 3
    })
df_proyecto = pd.DataFrame(proyectos_data)
df_proyecto.to_csv('Dim_Proyecto.csv', index=False)

# --- 3. GENERACIÓN DE TABLAS DE HECHOS (BASE) ---


## Base para Fact_Trazabilidad_Esfuerzo
print("Generando base para Fact_Trazabilidad_Esfuerzo...")
registros_esfuerzo = []
id_registro = 1
for _, proyecto in df_proyecto.iterrows():
    if proyecto['estado_actual'] == 'Entregado':
        # Simular esfuerzo: 250 a 1500 registros de horas por proyecto
        n_registros = np.random.randint(250, 1500) 
    else:
        # Menos registros si está activo
        n_registros = np.random.randint(50, 500) 

    # Simular fechas de registro dentro del horizonte
    fechas_registro = np.random.choice(HORIZONTE_TIEMPO, n_registros)
    
    for fecha in fechas_registro:
        # Asignar empleado y proceso aleatoriamente
        id_empleado = np.random.choice(df_empleado['id_empleado'])
        id_proceso = np.random.choice(df_proceso['id_proceso'])
        
        # Simular horas: entre 0.5 y 8.5 horas por registro
        horas_imputadas = round(np.random.uniform(0.5, 8.5), 2)
        
        # Obtener costo imputado usando el salario del empleado
        costo_hora = df_empleado[df_empleado['id_empleado'] == id_empleado]['salario_hora_base'].iloc[0]
        costo_imputado = round(horas_imputadas * costo_hora, 2)
        
        
        registros_esfuerzo.append({
            'id_registro': id_registro,
            'id_proyecto': proyecto['id_proyecto'],
            'id_tiempo': int(pd.to_datetime(fecha).strftime('%Y%m%d')),
            'id_empleado': id_empleado,
            'id_proceso': id_proceso,
            'horas_imputadas': horas_imputadas,
            'costo_imputado': costo_imputado,
            'horas_estimadas_fase': np.nan, # Se calculará/llenará después
            'varianza_esfuerzo': np.nan # Se calculará después
        })
        id_registro += 1

df_fact_esfuerzo = pd.DataFrame(registros_esfuerzo)
df_fact_esfuerzo.to_csv('Fact_Trazabilidad_Esfuerzo_BASE.csv', index=False)

# Fact_Defectos_Calidad
print("Generando Fact_Defectos_Calidad...")
registros_defectos = []
id_defecto = 1

gravedades = ['Bloqueador', 'Grave', 'Menor', 'Leve']
tiempos_resolucion_media = {'Bloqueador': 8.0, 'Grave': 4.0, 'Menor': 1.5, 'Leve': 0.5} # Horas promedio

for _, proyecto in df_proyecto.iterrows():
    # 1. PREDECIR EL TOTAL DE DEFECTOS USANDO RAYLEIGH/MADUREZ
    N_defectos = predecir_defectos_rayleigh(
        proyecto['esfuerzo_estimado_total'], 
        proyecto['nivel_madurez_aplicado']
    )
    
    # Simular la distribución de esos N_defectos a lo largo del tiempo del proyecto
    
    # Obtener el líder de proyecto (para asignación del reporte/cierre)
    lideres = df_empleado[df_empleado['rol_en_la_empresa'] == 'Líder de Proyecto']['id_empleado'].tolist()
    
    # Obtener IDs de empleados que NO son líderes (desarrolladores/testers)
    desarrolladores = df_empleado[df_empleado['rol_en_la_empresa'] != 'Líder de Proyecto']['id_empleado'].tolist()
    
    # Definir la ventana de tiempo para el proyecto (aproximación)
    # Usamos el 80% del horizonte para que los defectos se encuentren a tiempo
    fechas_proyecto = np.random.choice(HORIZONTE_TIEMPO, size=int(proyecto['esfuerzo_estimado_total'] / 8), replace=False)
    
    # Generar los N_defectos predichos
    for i in range(N_defectos):
        # La fecha de creación debe estar dentro de las fechas de esfuerzo del proyecto
        fecha_creacion = pd.to_datetime(np.random.choice(fechas_proyecto))
        
        # El cierre debe ser posterior
        fecha_cierre = fecha_creacion + timedelta(days=np.random.randint(1, 10))
        
        # Asignar gravedad y tiempo de resolución
        gravedad = np.random.choice(gravedades, p=[0.1, 0.3, 0.4, 0.2]) # Más graves son menos comunes
        
        # Tiempo neto de resolución: Añadir ruido gaussiano al promedio
        tiempo_neto_horas = max(0.25, np.random.normal(tiempos_resolucion_media[gravedad], 1.5))
        
        # Simular que un desarrollador/tester lo resuelve
        id_responsable = np.random.choice(desarrolladores)
        
        # Simular proceso donde se encontró (ej. Pruebas QA es el más común)
        id_proceso_encontrado = np.random.choice(df_proceso['id_proceso'], p=[0.05, 0.05, 0.15, 0.15, 0.20, 0.30, 0.10])
        
        registros_defectos.append({
            'id_defecto': id_defecto,
            'id_proyecto': proyecto['id_proyecto'],
            # Convierte las fechas a INT (YYYYMMDD) usando la corrección anterior
            'id_tiempo_reporte': int(pd.to_datetime(fecha_creacion).strftime('%Y%m%d')),
            'id_tiempo_cierre': int(pd.to_datetime(fecha_cierre).strftime('%Y%m%d')),
            'id_responsable': id_responsable,
            'id_proceso': id_proceso_encontrado,
            'severidad': gravedad,
            'tiempo_neto_horas': round(tiempo_neto_horas, 2),
            # Calcular la varianza: Suponemos un estándar de 5 días (120 horas) para la planeación
            'varianza_cierre_esperado': int((fecha_cierre - fecha_creacion).days) - 5,
            'conteo_defectos': 1
        })
        id_defecto += 1

df_fact_defectos = pd.DataFrame(registros_defectos)
print(f"Total de registros de defectos simulados: {len(df_fact_defectos)}")
df_fact_defectos.to_csv('Fact_Defectos_Calidad.csv', index=False)


print("\n--- ¡SIMULACIÓN DE DIMENSIONES Y BASE DE HECHOS COMPLETADA! ---")
print(f"Total de registros de esfuerzo simulados: {len(df_fact_esfuerzo)}")

