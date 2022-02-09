from LicensePlateRecognizer import main
import azure.functions as func

main(func.HttpRequest.get_json())