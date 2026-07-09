from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response
    response = exception_handler(exc, context)

    errors = []
    message = "An error occurred."
    if response is not None:
        # Standardize the response body
        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = str(response.data["detail"])
            elif len(response.data) > 0:
                first_key = list(response.data.keys())[0]
                val = response.data[first_key]
                if isinstance(val, list) and val:
                    message = f"{first_key}: {val[0]}"
                else:
                    message = f"{first_key}: {val}"

            for field, val in response.data.items():
                if field == "detail":
                    errors.append(
                        {
                            "code": getattr(exc, "default_code", "invalid"),
                            "field": None,
                            "message": str(val),
                        }
                    )
                elif isinstance(val, list):
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
            if response.data:
                message = str(response.data[0])
            for val in response.data:
                errors.append(
                    {
                        "code": getattr(exc, "default_code", "invalid"),
                        "field": None,
                        "message": str(val),
                    }
                )
        else:
            message = str(response.data)
            errors.append(
                {
                    "code": getattr(exc, "default_code", "invalid"),
                    "field": None,
                    "message": str(response.data),
                }
            )

        response.data = {
            "success": False,
            "message": message,
            "data": {},
            "errors": errors,
        }
    else:
        # For non-REST framework exceptions (unhandled server errors)
        response = Response(
            {
                "success": False,
                "message": "An internal server error occurred.",
                "data": {},
                "errors": [
                    {
                        "code": "server_error",
                        "field": None,
                        "message": str(exc),
                    }
                ],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
