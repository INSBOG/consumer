import json
from io import BytesIO
import minio

from openpyxl.cell.cell import Cell
from openpyxl.comments import Comment
from openpyxl.styles import PatternFill

from adapters.minio_adapter import MinioAdapter
from adapters.mongo import MongoAdapter
from services.validator import ValidatorService
from services.socket import SocketService

error_cell_color = "ff7675"


def show_error_on_cell(cell: Cell, error_message: str):
    # Crear relleno y comentario de error una vez
    error_fill = PatternFill(start_color=error_cell_color,
                             end_color=error_cell_color, fill_type="solid")
    cell.fill = error_fill
    cell.comment = Comment(error_message, "Sistema")
    return cell


class FileProcessorService(ValidatorService):

    def __init__(self):
        super().__init__()
        self.minio = MinioAdapter()
        self.mongo_adapter = MongoAdapter()
        self.socket_service = SocketService()

    def process(self, ch, method, props, body):
        try:
            
            print("Procesando:", body.decode("utf-8"))
            q_data = json.loads(body)

            self.minio.bucket = "files"
            response = self.minio.get_file(q_data["filename"])

            data = BytesIO(response.data)

            col = self.mongo_adapter.get_collection("reportes")
            query_filter = {"filename": q_data["filename"]}
            report = col.find_one(query_filter)

            filename = self.validate(data, report)

            if report:

                if "processed_file" in report:
                    self.minio.delete_file(report["processed_file"], "processed")

                col.update_one(query_filter, {
                    "$set": {
                        "status": 2,
                        "processed_file": filename
                    }
                })
                self.socket_service.emit("handle_file_processed", {
                    "error": False,
                    "message": f"Reporte {q_data['original_filename']} {q_data['month']} generado"
                })
            else:
                col.update_one(query_filter, {
                    "$set": {
                        "status": 0,
                        "processed_file": filename
                    }
                })
                self.socket_service.emit("handle_file_processed", {
                    "error": True,
                    "message": "No se pudo generar el reporte"
                })
            print("Archivo Procesado")
        except minio.error.S3Error:
            print("Archivo no encontrado")
            self.socket_service.emit("handle_file_processed", {
                "error": True,
                "message": "No se pudo generar el reporte"
            })
        except Exception as e:
            print(f"Error: No se pudo generar el reporte - {str(e)}")
            self.socket_service.emit("handle_file_processed", {
                "error": True,
                "message": str(e)
            })
        finally:
            self.socket_service.disconnect_socket()
            ch.basic_ack(delivery_tag=method.delivery_tag)