from datetime import datetime
from pydantic import BaseModel, Field


class CertificateData(BaseModel):
    certificate_id: str = Field(alias="id", description="Sertifikatning noyob identifikatori (UUID).")
    certificate_name: str = Field(description="Sertifikatning seriya raqami/nomi.")
    certificate_alias: str = Field(description="Sertifikatning egasi va boshqa ma'lumotlari (DN) kiritilgan qismi.")
    created_at: datetime = Field(description="Sertifikat obyekti bazada yaratilgan sana va vaqt.")

    pkcs7_data: str = Field(alias="pkcs7", description="PKCS#7 formatidagi sertifikatning bazaga kodlangan qiymati.")

    class Config:
        populate_by_name = True


__all__ = ["CertificateData"]
