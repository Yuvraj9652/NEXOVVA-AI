from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response
    response = exception_handler(exc, context)

    errors = []
    if response is not None:
        # Standardize the response body
        if isinstance(response.data, dict):
            for field, val in response.data.items():
                if isinstance(val, list):
                    for msg in val:
                        errors.append(
                            {
                                "code": getattr(exc, "default_code", "invalid"),
                                "field": field,
                                "message": str(msg),
                            }
                        )
                else:
                    errors.append(
                        {
                            "code": getattr(exc, "default_code", "invalid"),
                            "field": field,
                            "message": str(val),
                        }
                    )
        elif isinstance(response.data, list):
            for val in response.data:
                errors.append(
                    {
                        "code": getattr(exc, "default_code", "invalid"),
                        "field": None,
                        "message": str(val),
                    }
                )
        else:
            errors.append(
                {
                    "code": getattr(exc, "default_code", "invalid"),
                    "field": None,
                    "message": str(response.data),
                }
            )

        response.data = {
            "status": "error",
            "data": None,
            "errors": errors,
            "meta": {},
        }
    else:
        # For non-REST framework exceptions (unhandled server errors)
        response = Response(
            {
                "status": "error",
                "data": None,
                "errors": [
                    {
                        "code": "server_error",
                        "field": None,
                        "message": "An internal server error occurred.",
                    }
                ],
                "meta": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
