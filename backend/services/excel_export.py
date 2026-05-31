"""Excel export service for approved lease abstraction records."""
import io

from openpyxl import Workbook
from openpyxl.styles import Font

from services.csv_export import CSV_COLUMNS, build_rows


def build_excel(docs: list) -> bytes:
    output = io.BytesIO()
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Approved Leases"
    worksheet.freeze_panes = "A2"

    worksheet.append(CSV_COLUMNS)
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    for row in build_rows(docs):
        worksheet.append(row)

    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 60)

    workbook.save(output)
    return output.getvalue()
