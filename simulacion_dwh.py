import pandas as pd
import numpy as np
from datetime import timedelta

# --- 1. CONFIGURACIÓN DE PARÁMETROS ---
N_EMPLEADOS = 8  # Reducido para parecer más Startup
N_CLIENTES = 5
N_PROYECTOS = 12
FECHA_INICIO_SIMULACION = pd.to_datetime('2024-01-01')
FECHA_FIN_SIMULACION = pd.to_datetime('2024-12-31')

# Horizonte para proyectos (2024)
HORIZONTE_TIEMPO = pd.date_range(FECHA_INICIO_SIMULACION, FECHA_FIN_SIMULACION, freq='D')
# Horizonte extendido para Dim_Tiempo (evita errores de fechas futuras)
HORIZONTE_DIMENSION = pd.date_range(FECHA_INICIO_SIMULACION, '2025-03-30', freq='D')

# --- 1.1 FUNCIÓN RAYLEIGH (Modelo Predictivo) ---
def predecir_defectos_rayleigh(esfuerzo, nivel_madurez):
    # Ajustamos factores para que sean realistas
    if nivel_madurez == 4:
        factor_base = 0.005 
    elif nivel_madurez == 3:
        factor_base = 0.01 
    else: 
        factor_base = 0.02 
        
    N_esperado = esfuerzo * factor_base
    N_defectos_predichos = np.random.poisson(N_esperado)
    return max(3, N_defectos_predichos) # Mínimo 3 defectos para que haya datos

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
df_tiempo['es_laboral'] = ~df_tiempo['fecha_completa'].dt.dayofweek.isin([5, 6])
df_tiempo.to_csv('Dim_Tiempo.csv', index=False)

## Dim_Cliente
print("Generando Dim_Cliente...")
sectores = ['Pymes', 'Comercio Local', 'Salud', 'Educación']
contratos = ['Precio Fijo', 'Bolsa de Horas']
df_cliente = pd.DataFrame({
    'id_cliente': range(1, N_CLIENTES + 1),
    'nombre_cliente': [f'Cliente_{i}' for i in range(1, N_CLIENTES + 1)],
    'sector': np.random.choice(sectores, N_CLIENTES),
    'tipo_contrato_principal': np.random.choice(contratos, N_CLIENTES)
})
df_cliente.to_csv('Dim_Cliente.csv', index=False)

## Dim_Empleado (Salarios ajustados a Startup)
print("Generando Dim_Empleado...")
roles = ['Líder de Proyecto', 'Desarrollador Senior', 'Desarrollador Mid', 'Desarrollador Junior', 'Tester QA']
seniority = ['Senior', 'Mid', 'Junior']

# PRECIOS REALISTAS PARA STARTUP (MXN por Hora)
# Promedio aprox: $300/hr
salarios = {
    'Desarrollador Junior': 150, 
    'Desarrollador Mid': 280, 
    'Desarrollador Senior': 450, 
    'Líder de Proyecto': 550, 
    'Tester QA': 200
}

df_empleado = pd.DataFrame({
    'id_empleado': range(1, N_EMPLEADOS + 1),
    'nombre_completo': [f'Colaborador_{i}' for i in range(1, N_EMPLEADOS + 1)],
    'rol_en_la_empresa': np.random.choice(roles, N_EMPLEADOS),
    'seniority': np.random.choice(seniority, N_EMPLEADOS),
})
df_empleado['salario_hora_base'] = df_empleado['rol_en_la_empresa'].map(salarios)
df_empleado['equipo_asignado'] = np.random.choice(['Dev Team A', 'Dev Team B'], N_EMPLEADOS)
df_empleado.to_csv('Dim_Empleado.csv', index=False)

## Dim_Proceso_Interno
print("Generando Dim_Proceso_Interno...")
procesos_data = [
    (1, 'Definición de Requisitos', 'Análisis', 'Obligatorio'),
    (2, 'Diseño UX/UI', 'Diseño', 'Obligatorio'),
    (3, 'Desarrollo Backend', 'Implementación', 'Obligatorio'),
    (4, 'Desarrollo Frontend', 'Implementación', 'Obligatorio'),
    (5, 'Code Review', 'Pruebas', 'Obligatorio'),
    (6, 'Pruebas QA', 'Pruebas', 'Obligatorio'),
    (7, 'Despliegue', 'Despliegue', 'Obligatorio')
]
df_proceso = pd.DataFrame(procesos_data, columns=['id_proceso', 'nombre_proceso', 'fase_sdlc', 'indicador_cumplimiento'])
df_proceso['documentacion_link'] = 'http://docs.softwarerapido.com/'
df_proceso.to_csv('Dim_Proceso_Interno.csv', index=False)

## Dim_Proyecto (Presupuesto Inteligente)
print("Generando Dim_Proyecto...")
proyectos_data = []
costo_promedio_hr = 300 # Referencia para calcular presupuesto

for i in range(1, N_PROYECTOS + 1):
    id_cliente = np.random.choice(df_cliente['id_cliente'])
    duracion_dias = np.random.randint(30, 180) # Proyectos de 1 a 6 meses
    start_date = FECHA_INICIO_SIMULACION + timedelta(days=np.random.randint(0, 300))
    
    # Esfuerzo más moderado (200 a 1200 horas)
    esfuerzo_estimado = np.random.randint(200, 1200)
    
    # LÓGICA DE PRESUPUESTO RENTABLE:
    # Presupuesto = Costo Estimado + Margen de Ganancia (30% a 60%)
    # Esto asegura que casi siempre haya dinero de sobra ("En Presupuesto")
    margen_ganancia = np.random.uniform(1.30, 1.60) 
    presupuesto = (esfuerzo_estimado * costo_promedio_hr) * margen_ganancia
    
    proyectos_data.append({
        'id_proyecto': i,
        'id_cliente': id_cliente,
        'nombre_proyecto': f'App v{i}.0',
        'estado_actual': np.random.choice(['Entregado', 'Activo'], p=[0.6, 0.4]),
        'esfuerzo_estimado_total': esfuerzo_estimado,
        'presupuesto_total_mxn': round(presupuesto, 2),
        'tipo_desarrollo': np.random.choice(['Web', 'Móvil', 'E-commerce']),
        'nivel_madurez_aplicado': np.random.choice([2, 3], p=[0.4, 0.6]) # Startups suelen estar en nivel 2 o 3
    })
df_proyecto = pd.DataFrame(proyectos_data)
df_proyecto.to_csv('Dim_Proyecto.csv', index=False)


# --- 3. GENERACIÓN DE TABLAS DE HECHOS ---

## Fact_Trazabilidad_Esfuerzo
print("Generando base para Fact_Trazabilidad_Esfuerzo...")
registros_esfuerzo = []
id_registro = 1

for _, proyecto in df_proyecto.iterrows():
    # Simular que trabajamos cerca de lo estimado (con un poco de variación)
    # Variación del +/- 10% sobre lo estimado para que sea realista pero rentable
    variacion_real = np.random.uniform(0.9, 1.15) 
    horas_totales_a_simular = int(proyecto['esfuerzo_estimado_total'] * variacion_real)
    
    # Distribuir esas horas en registros diarios pequeños (ej. 4-8 horas por día)
    num_dias_trabajo = int(horas_totales_a_simular / 6) # Promedio 6 horas/día por persona
    
    if num_dias_trabajo < 1: num_dias_trabajo = 1
    
    # Generar fechas dentro del rango posible
    fechas_registro = [start_date + timedelta(days=x) for x in range(num_dias_trabajo)]
    
    # Asignamos horas aleatorias hasta completar el paquete
    for fecha in fechas_registro:
        if fecha > FECHA_FIN_SIMULACION: continue # No pasarse de 2024
        
        id_empleado = np.random.choice(df_empleado['id_empleado'])
        id_proceso = np.random.choice(df_proceso['id_proceso'])
        
        horas_imputadas = round(np.random.uniform(2.0, 9.0), 2)
        
        # Costo real basado en salario
        costo_hora = df_empleado[df_empleado['id_empleado'] == id_empleado]['salario_hora_base'].iloc[0]
        costo_imputado = round(horas_imputadas * costo_hora, 2)
        
        registros_esfuerzo.append({
            'id_registro': id_registro,
            'id_proyecto': proyecto['id_proyecto'],
            'id_tiempo': int(fecha.strftime('%Y%m%d')),
            'id_empleado': id_empleado,
            'id_proceso': id_proceso,
            'horas_imputadas': horas_imputadas,
            'costo_imputado': costo_imputado,
            'horas_estimadas_fase': np.nan,
            'varianza_esfuerzo': np.nan
        })
        id_registro += 1

df_fact_esfuerzo = pd.DataFrame(registros_esfuerzo)
df_fact_esfuerzo.to_csv('Fact_Trazabilidad_Esfuerzo_BASE.csv', index=False)


## Fact_Defectos_Calidad
print("Generando Fact_Defectos_Calidad...")
registros_defectos = []
id_defecto = 1

gravedades = ['Bloqueador', 'Grave', 'Menor', 'Leve']
tiempos_resolucion_media = {'Bloqueador': 6.0, 'Grave': 3.5, 'Menor': 1.5, 'Leve': 0.5}

for _, proyecto in df_proyecto.iterrows():
    N_defectos = predecir_defectos_rayleigh(
        proyecto['esfuerzo_estimado_total'], 
        proyecto['nivel_madurez_aplicado']
    )
    
    lideres = df_empleado[df_empleado['rol_en_la_empresa'] == 'Líder de Proyecto']['id_empleado'].tolist()
    desarrolladores = df_empleado[df_empleado['rol_en_la_empresa'] != 'Líder de Proyecto']['id_empleado'].tolist()
    
    # Fechas posibles
    fecha_inicio_proy = pd.to_datetime('2024-01-01') # Simplificación
    fechas_proyecto = pd.date_range(fecha_inicio_proy, periods=100)
    
    for i in range(N_defectos):
        # CORRECCIÓN: Convertir explícitamente a datetime de Pandas para evitar TypeError
        fecha_creacion = pd.to_datetime(np.random.choice(fechas_proyecto))
        fecha_cierre = fecha_creacion + timedelta(days=int(np.random.randint(1, 8)))
        
        gravedad = np.random.choice(gravedades, p=[0.05, 0.25, 0.4, 0.3])
        tiempo_neto = max(0.25, np.random.normal(tiempos_resolucion_media[gravedad], 1.0))
        
        id_responsable = np.random.choice(desarrolladores if desarrolladores else [1])
        id_proceso_enc = np.random.choice(df_proceso['id_proceso'], p=[0.05, 0.05, 0.15, 0.15, 0.20, 0.30, 0.10])
        
        registros_defectos.append({
            'id_defecto': id_defecto,
            'id_proyecto': proyecto['id_proyecto'],
            'id_tiempo_reporte': int(fecha_creacion.strftime('%Y%m%d')),
            'id_tiempo_cierre': int(fecha_cierre.strftime('%Y%m%d')),
            'id_responsable': id_responsable,
            'id_proceso': id_proceso_enc,
            'severidad': gravedad,
            'tiempo_neto_horas': round(tiempo_neto, 2),
            'varianza_cierre_esperado': int((fecha_cierre - fecha_creacion).days) - 3,
            'conteo_defectos': 1
        })
        id_defecto += 1

df_fact_defectos = pd.DataFrame(registros_defectos)
df_fact_defectos.to_csv('Fact_Defectos_Calidad.csv', index=False)

print("\n--- ¡SIMULACIÓN DE STARTUP COMPLETADA! DATOS REALISTAS GENERADOS ---")