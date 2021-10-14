import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "Healthcheck executed successfully.",
        status_code=200
    )
