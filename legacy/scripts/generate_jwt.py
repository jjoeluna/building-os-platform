import time
import base64
import hmac
import hashlib
import json

# This is the secret from the API documentation
SECRET = "t3hILevRdzfFyd05U2g+XT4lPZCmT6CB+ytaQljWWOk="


def generate_jwt(secret):
    header = {"alg": "HS256", "typ": "JWT"}
    exp = int(time.time()) + 300  # Expires in 5 minutes
    payload = {"exp": exp}

    # URL-safe base64 encoding without padding
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(
        b"="
    )

    data = encoded_header + b"." + encoded_payload
    secret_bytes = secret.encode(
        "utf-8"
    )  # Use UTF-8 encoding instead of Base64 decoding

    signature = hmac.new(secret_bytes, data, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=")

    jwt_token = b".".join([encoded_header, encoded_payload, encoded_signature]).decode()
    print(jwt_token)


if __name__ == "__main__":
    generate_jwt(SECRET)
