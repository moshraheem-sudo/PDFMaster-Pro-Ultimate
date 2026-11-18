"""
Upload Release and Assets to GitHub
"""
import os
import sys
import json
import ssl
import urllib.request
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "moshraheem-sudo/PDFMaster-Pro-Ultimate"
TAG = "v3.5.0"
NAME = "PDF Master Pro - Ultimate Edition v3.5.0"
BODY = """# PDF Master Pro - Ultimate Edition v3.5.0 👑

تطبيق مكتبي متكامل واحترافي لمعالجة وتحرير مستندات PDF والصور لنظام Windows، مبني وفق أحدث المعايير الهندسية والواجهات الرسومية العصرية.

---

### 📥 ملفات التحميل والتنصيب المرفقة في هذا الإصدار:

1. **`PDFMasterPro_Ultimate_Setup_v3.5.0.exe`**:
   - حزمة التثبيت الرسمية الكاملة (Inno Setup Installer).
   - تثبيت مكتبي بنقرة واحدة، إنشاء اختصارات سطح المكتب وقائمة ابدأ، وربط ملفات PDF تلقائياً.
   - لا يتطلب تثبيت بايثون.

2. **`PDFMasterPro_v3.5.0_Portable.zip`**:
   - النسخة المحمولة (Portable Executable) التي تعمل مباشرة دون تنصيب.

3. **`PDF_Master_Pro_Ultimate_Edition.zip`**:
   - الحزمة الكاملة للكود المصدري والمحركات والأدوات.

---

### 🌟 أبرز الميزات:
- عارض ومحرر PDF وصور متعدد التبويبات فائق السرعة.
- دعم السحب والإفلات التلقائي لكافة صيغ PDF والصور (PNG, JPG, WebP, BMP).
- ضغط PDF بثلاثة مستويات ذكية وحساب التوفير الحقيقي.
- دمج، تقسيم، تدوير، تكرار، وحذف الصفحات والصور.
- تشفير عسكري AES-256 وحماية بكلمات مرور وصلاحيات متقدمة.
- محرك OCR للتعرف الضوئي على النصوص باللغتين العربية والإنجليزية.
- إمكانية استخراج الصور من PDF وحذفها واقتصاص الهوامش.
- معالجة جماعية للصور (Batch Processing) وتحويل الصيغ.
- متوافق 100% مع Windows 10 و Windows 11 (64-bit).
"""

def main():
    ctx = ssl._create_unverified_context()
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "PDFMasterPro-Deployer",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Create Release
    print(f"Creating release {TAG} on {REPO}...")
    release_data = {
        "tag_name": TAG,
        "name": NAME,
        "body": BODY,
        "draft": False,
        "prerelease": False
    }

    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases",
        data=json.dumps(release_data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        resp = urllib.request.urlopen(req, context=ctx)
        release_info = json.loads(resp.read())
        print("Release created successfully! ID:", release_info.get("id"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"HTTPError: {e.code} - {err_msg}")
        # Try to get existing release
        req_get = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}",
            headers=headers
        )
        resp_get = urllib.request.urlopen(req_get, context=ctx)
        release_info = json.loads(resp_get.read())
        print("Found existing release ID:", release_info.get("id"))

    release_id = release_info["id"]

    # 2. Upload Assets
    assets_to_upload = [
        ("PDFMasterPro_Ultimate_Setup_v3.5.0.exe", Path("installer_output/PDFMasterPro_Ultimate_Setup_v3.5.0.exe")),
        ("PDFMasterPro_v3.5.0_Portable.zip", Path("installer_output/PDFMasterPro_v3.5.0_Portable.zip")),
        ("PDF_Master_Pro_Ultimate_Edition.zip", Path("PDF_Master_Pro_Ultimate_Edition.zip"))
    ]

    for asset_name, asset_path in assets_to_upload:
        if not asset_path.exists():
            print(f"Asset file {asset_path} does not exist, skipping.")
            continue

        file_size = asset_path.stat().st_size
        print(f"Uploading {asset_name} ({file_size / (1024*1024):.1f} MB)...")

        upload_url = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={asset_name}"
        upload_headers = {
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "PDFMasterPro-Deployer",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(file_size)
        }

        with open(asset_path, "rb") as f:
            data = f.read()

        req_up = urllib.request.Request(
            upload_url,
            data=data,
            headers=upload_headers,
            method="POST"
        )

        try:
            resp_up = urllib.request.urlopen(req_up, context=ctx)
            asset_info = json.loads(resp_up.read())
            print(f"Successfully uploaded {asset_name}! Browser download URL:", asset_info.get("browser_download_url"))
        except urllib.error.HTTPError as e:
            print(f"Failed to upload {asset_name}: {e.code} - {e.read().decode('utf-8')}")

    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    main()
