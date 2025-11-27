import subprocess
import os
import time
import sys

def imprimir_titulo(mensaje):
    """Imprime un mensaje con formato visual para separar pasos."""
    print("\n" + "="*60)
    print(f"🚀 {mensaje.upper()}")
    print("="*60 + "\n")

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando de sistema y maneja errores."""
    print(f"⏳ Iniciando: {descripcion}...")
    try:
        # shell=True permite ejecutar comandos como si estuvieras en la terminal
        subprocess.check_call(comando, shell=True)
        print(f"✅ Éxito: {descripcion} completado.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error crítico al ejecutar: {descripcion}")
        print(f"   Detalle: {e}")
        sys.exit(1) # Detiene todo si un paso falla

def limpiar_base_datos():
    """Elimina el archivo de base de datos SQLite para empezar de cero."""
    archivo_db = 'proyecto_bi.db'
    imprimir_titulo("Paso 1: Limpieza de Base de Datos")
    
    if os.path.exists(archivo_db):
        try:
            os.remove(archivo_db)
            print(f"🗑️  Archivo '{archivo_db}' eliminado correctamente.")
        except Exception as e:
            print(f"⚠️  No se pudo eliminar la BD (puede estar en uso): {e}")
    else:
        print(f"ℹ️  No se encontró '{archivo_db}', se creará una nueva.")

def main():
    # 1. Limpiar BD antigua
    limpiar_base_datos()
    
    # 2. Generar Datos Sintéticos (Simulación)
    imprimir_titulo("Paso 2: Generación de Datos (Simulación)")
    ejecutar_comando("python simulacion_dwh.py", "Simulación de Datos DWH")
    
    # 3. ETL y Creación de SQLite
    imprimir_titulo("Paso 3: Proceso ETL y Carga a SQLite")
    ejecutar_comando("python migrar_a_sqlite.py", "Migración a SQLite y Creación de Vistas")
    
    # 4. Desplegar Streamlit
    imprimir_titulo("Paso 4: Despliegue de Aplicación")
    print("🌐 Iniciando servidor de Streamlit...")
    print("   (Presiona Ctrl + C en esta terminal para detener la app)")
    time.sleep(2) # Pausa dramática para leer
    
    # Usamos subprocess.run sin check_call para que el script se mantenga vivo con la app
    try:
        subprocess.run("streamlit run app.py", shell=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario.")

if __name__ == "__main__":
    main()