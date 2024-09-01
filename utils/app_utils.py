import oss2
import hmac
import hashlib

from typing import Dict, Union, Any
from chainlit.data import BaseStorageClient
from chainlit.logger import logger

def hmac_sha256(message):
    default_key='ed87895fe109871c0a89f035102f695e'
    key_bytes = default_key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)
    hmac_digest = hmac_obj.hexdigest()
    return hmac_digest

class OSS2StorageClient(BaseStorageClient):

    def __init__(self, access_key_id: str, access_key_secret: str):
        self.endpoint="oss-cn-shenzhen.aliyuncs.com"
        self.bucket_name="chainlit-bucket"
        self.bucket = oss2.Bucket(
            oss2.Auth(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret
            ),
            endpoint=self.endpoint,
            bucket_name=self.bucket_name
        )

    async def upload_file(self, object_key: str, data: Union[bytes, str], mime: str = 'application/octet-stream', overwrite: bool = True) -> Dict[str, Any]:
        try:
            self.bucket.put_object(key=object_key,data=data, headers={'Content-Type': mime})
            url = f"https://{self.bucket_name}.oss-cn-shenzhen.aliyuncs.com/{object_key}"
            return {"object_key": object_key, "url": url}
        except Exception as e:
            logger.warn(f"OSS2StorageClient, upload_file error: {e}")
            return {}

            
    
        
    