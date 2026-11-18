"""
PDF Master Pro - Security & Encryption Engine
Military-grade AES-256 encryption, granular permissions, password verification, and decryption using pikepdf.
"""
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import pikepdf
from core.models import SecurityConfig

class SecurityEngine:
    @staticmethod
    def encrypt_pdf(
        input_path: str,
        output_path: str,
        config: SecurityConfig
    ) -> bool:
        """
        Encrypts PDF with AES-256 and custom permissions.
        """
        if not config.user_password and not config.owner_password:
            raise ValueError("يجب تحديد كلمة مرور واحدة على الأقل (فتح أو إدارة).")
            
        with pikepdf.open(input_path) as pdf:
            # Configure permissions
            permissions = pikepdf.Permissions(
                print_lowres=config.allow_printing,
                print_highres=config.allow_printing,
                extract=config.allow_copying,
                modify_annotation=config.allow_annotations,
                modify_form=config.allow_modifying,
                modify_assembly=config.allow_modifying,
                modify_other=config.allow_modifying
            )
            
            # AES-256 (R=6)
            enc = pikepdf.Encryption(
                owner=config.owner_password or config.user_password,
                user=config.user_password,
                allow=permissions,
                R=6
            )
            
            pdf.save(output_path, encryption=enc)
        return True

    @staticmethod
    def decrypt_pdf(
        input_path: str,
        output_path: str,
        password: str
    ) -> Tuple[bool, str]:
        """
        Decrypts an encrypted PDF given the correct password and saves an unencrypted copy.
        """
        try:
            with pikepdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
            return True, "تم فك تشفير الملف وإزالة الحماية بنجاح."
        except pikepdf.PasswordError:
            return False, "كلمة المرور غير صحيحة."
        except Exception as e:
            return False, f"فشل فك الحماية: {str(e)}"

    @staticmethod
    def check_encryption_status(file_path: str) -> Dict[str, Any]:
        """
        Inspects if file is encrypted and its protection flags.
        """
        try:
            with pikepdf.open(file_path) as pdf:
                return {
                    "is_encrypted": False,
                    "requires_password": False,
                    "can_read": True
                }
        except pikepdf.PasswordError:
            return {
                "is_encrypted": True,
                "requires_password": True,
                "can_read": False
            }
        except Exception as e:
            return {
                "is_encrypted": False,
                "error": str(e)
            }
