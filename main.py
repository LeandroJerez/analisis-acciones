import formatter
import openpyxl
from extractor import obtener_datos_acciones


def principal():
    # 1. Obtenemos el DataFrame procesado desde el módulo extractor
    df_acciones = obtener_datos_acciones()

    if not df_acciones.empty:
        # 2. Guardamos en Excel
        nombre_archivo = "rendimiento_acciones.xlsx"
        df_acciones.to_excel(nombre_archivo, index=False,
                             sheet_name="Resumen Acciones")
        print(
            f"\n¡Planilla generada con éxito! Archivo guardado como: {nombre_archivo}")
    else:
        print("\nNo se pudieron obtener datos para generar la planilla.")


if __name__ == "__main__":
    principal()
