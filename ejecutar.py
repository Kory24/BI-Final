import subprocess
import os
import time
import sys
import shutil
import webbrowser
from datetime import datetime

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

def verificar_herramientas():
    """Verifica si Git está instalado y disponible en el sistema."""
    imprimir_titulo("Paso 0: Verificación de Requisitos")
    
    # shutil.which busca el ejecutable en las variables de entorno (PATH)
    if shutil.which("git") is None:
        print("⚠️  ADVERTENCIA: Git no se encontró instalado o en el PATH.")
        print("   La subida automática a GitHub no funcionará, pero el resto sí.")
        return False
    else:
        print("✅ Git detectado correctamente.")
        return True

def limpiar_base_datos():
    """Elimina el archivo de base de datos SQLite para asegurar una carga limpia."""
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

def subir_a_git():
    """Realiza el proceso de add, commit y push a GitHub."""
    imprimir_titulo("Paso 4: Actualización Automática en GitHub")
    
    try:
        print("📦 Preparando archivos para subir...")
        # Agrega todos los cambios (incluyendo nuevos archivos)
        subprocess.check_call("git add .", shell=True)
        
        # Crea el commit con fecha y hora actual
        mensaje_commit = f"Actualización automática: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # Usamos subprocess.call en lugar de check_call para que no falle si no hay cambios
        subprocess.call(f'git commit -m "{mensaje_commit}"', shell=True)
        
        print("🚀 Subiendo a GitHub (Streamlit Cloud detectará el cambio)...")
        subprocess.check_call("git push", shell=True)
        print("✅ ¡Cambios subidos exitosamente a GitHub!")
        print("⏳ Esperando unos segundos para que Streamlit Cloud procese los cambios...")
        time.sleep(5) # Darle un momento a la nube
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error al subir a Git: {e}")
        print("   (Asegúrate de haber configurado 'git remote' y tus credenciales previamente)")

def main():
    # URL de tu aplicación desplegada
    APP_URL = "https://software-rapido.streamlit.app/"

    # 0. Verificar si tenemos Git
    tiene_git = verificar_herramientas()

    # 1. Limpiar BD antigua
    limpiar_base_datos()
    
    # 2. Generar Datos Sintéticos (Simulación)
    imprimir_titulo("Paso 2: Generación de Datos (Simulación)")
    ejecutar_comando("python simulacion_dwh.py", "Simulación de Datos DWH")
    
    # 3. ETL y Creación de SQLite
    imprimir_titulo("Paso 3: Proceso ETL y Carga a SQLite")
    ejecutar_comando("python migrar_a_sqlite.py", "Migración a SQLite y Creación de Vistas")
    
    # 4. Subir a GitHub (Opcional pero recomendado para actualizar la nube)
    if tiene_git:
        respuesta = input("\n¿Quieres subir los cambios a GitHub para actualizar la web pública? (s/n): ").lower()
        if respuesta == 's':
            subir_a_git()
    
    # 5. Abrir la Aplicación en la Nube
    imprimir_titulo("Paso 5: Apertura de Aplicación Web")
    print(f"🌐 Abriendo tu entorno de prueba en: {APP_URL}")
    webbrowser.open(APP_URL)
    print("\n✨ ¡Proceso finalizado! Tu aplicación está lista en el navegador.")

if __name__ == "__main__":
    main()