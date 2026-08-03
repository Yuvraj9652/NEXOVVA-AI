import jwt
from allauth.socialaccount.internal import jwtkit


_original_verify_and_decode = jwtkit.verify_and_decode


def verify_and_decode_with_leeway(
    *,
    credential,
    keys_url,
    issuer,
    audience,
    lookup_kid,
    verify_signature=True,
):
    try:
        if verify_signature:
            alg, key = jwtkit.fetch_key(
                credential,
                keys_url,
                lookup_kid,
            )
            algorithms = [alg]
        else:
            key = ""
            algorithms = None

        data = jwt.decode(
            credential,
            key=key,
            options={
                "verify_signature": verify_signature,
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
            },
            issuer=issuer,
            audience=audience,
            algorithms=algorithms,
            leeway=5,
        )

        jwtkit.verify_jti(data)

        return data

    except jwt.PyJWTError as e:
        from allauth.socialaccount.providers.oauth2.client import OAuth2Error
        raise OAuth2Error("Invalid id_token") from e


jwtkit.verify_and_decode = verify_and_decode_with_leeway