# import hashlib
# import uuid
# from typing import Optional
#
# from sqlalchemy.orm import Session
#
# from app.core.redis import get_redis_client
#
#
# class IpakYuli:
#     def __init__(self, company_id: uuid.UUID, db: Optional[Session] = None):
#         self.redis_client = get_redis_client()
#         self.company_id = company_id
#         self.db = db
#         self.device_id = self.redis_client.get(f"kapitalbank:{company_id}:device")
#
#         if self.device_id is None:
#             self.device_id = self._generate_device_id()
#             self.redis_client.setex(name=f"kapitalbank:{company_id}:device", value=self.device_id, time=30 * 24 * 3600)
#
#         self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
#
#     def _generate_device_id(self):
#         generated = hashlib.md5(str(uuid.getnode()).encode()).hexdigest()
#         return generated
