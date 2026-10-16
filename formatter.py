from openpyxl.chart import BarChart, Reference
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


def estilizar_excel(nombre_archivo):
    wb = openpyxl.load_workbook(nombre_archivo)
    ws = wb.active

    # Estilos
    font_cabecera = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_cabecera = PatternFill(
        start_color="1F4E78", end_color="1F4E78", fill_type="solid"
    )
    borde_fino = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    # Aplicar estilos a la cabecera
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = font_cabecera
        cell.fill = fill_cabecera
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Aplicar bordes y ajustar ancho de columnas automáticamente
    for col in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col)
        max_len = 0
        for row in range(1, ws.max_row + 1):
            cell = ws.cell(row=row, column=col)
            cell.border = borde_fino
            if row > 1:  # Datos
                cell.alignment = Alignment(vertical="center")

            if cell.value:
                max_len = max(max_len, len(str(cell.value)))

        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(nombre_archivo)


def agregar_grafico_barras(nombre_archivo):
    wb = openpyxl.load_workbook(nombre_archivo)
    ws = wb.active  # O ws = wb['NombreDeTuHoja']

    # 1. Crear la instancia del gráfico de barras
    chart = BarChart()
    # 'col' para barras verticales (columnas) o 'bar' para horizontales
    chart.type = "col"
    chart.style = 10  # Estilo predefinido de diseño de Excel
    chart.title = "Rendimiento de Acciones"
    chart.y_axis.title = "Valor / Porcentaje"
    chart.x_axis.title = "Acciones"

    # 2. Definir los rangos de datos y las categorías (etiquetas del eje X)
    # Asumiendo que:
    # - Los datos numéricos están en la columna B (desde la fila 1 hasta la última)
    # - Las categorías (nombres de las acciones) están en la columna A (desde la fila 2 hasta la última)
    max_fila = ws.max_row

    # Referencia para los datos (incluye el encabezado)
    datos = Reference(
        ws, min_col=2, min_row=1, max_col=2, max_row=max_fila
    )  # Ajusta min_col según tu columna de valores
    # Referencia para las etiquetas del eje X (excluyendo el encabezado, desde la fila 2)
    categorias = Reference(
        ws, min_col=1, min_row=2, max_col=1, max_row=max_fila
    )  # Ajusta min_col según tu columna de nombres

    chart.add_data(datos, titles_from_data=True)
    chart.set_categories(categorias)

    # 3. Opcional: ajustar el tamaño del gráfico
    chart.height = 12
    chart.width = 18

    # 4. Insertar el gráfico en la hoja (por ejemplo, en la celda D2)
    ws.add_chart(chart, "D2")

    # Guardar los cambios
    wb.save(nombre_archivo)
