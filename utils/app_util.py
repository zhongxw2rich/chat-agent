import hmac
import hashlib

def hmac_sha256(message):
    default_key='ed87895fe109871c0a89f035102f695e'
    key_bytes = default_key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)
    hmac_digest = hmac_obj.hexdigest()
    return hmac_digest