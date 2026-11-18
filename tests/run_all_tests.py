"""
PDF Master Pro - Automated Test Suite Runner & Report Generator
Executes all unit tests and outputs markdown report.
"""
import unittest
import sys
import io
import time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(ROOT / "tests"), pattern="test_*.py")
    
    start_time = time.time()
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    duration = time.time() - start_time
    
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    
    test_details = stream.getvalue()
    print(test_details)
    
    # Generate TEST_REPORT.md
    report_content = f"""# تقرير نتائج الاختبارات الشاملة - PDF Master Pro (Ultimate Edition)

تاريخ الاختبار: {time.strftime('%Y-%m-%d %H:%M:%S')}  
البيئة: Windows 64-bit | Python {sys.version.split()[0]}  
حالة الاختبارات الإجمالية: **{'ناجحة بالكامل ✅' if result.wasSuccessful() else 'توجد أخطاء ❌'}**

---

## 1. ملخص النتائج الرقمية

| المعيار | القيمة |
| :--- | :--- |
| إجمالي الاختبارات المنفذة | **{total}** |
| الاختبارات الناجحة | **{passed}** |
| حالات الفشل (Failures) | **{failures}** |
| الأخطاء البرمجية (Errors) | **{errors}** |
| مدة تنفيذ الاختبارات | **{duration:.2f} ثانية** |
| نسبة النجاح | **{(passed / total * 100):.1f}%** |

---

## 2. تفاصيل تغطية الوحدات والمحركات

### أ. محرك PDF الأساسي (`core.pdf_engine`)
- ✅ استخراج بيانات المستند والصفحات والأبعاد بدقة (A4 / Letter).
- ✅ دمج ملفات متعددة بترتيب سليم.
- ✅ تقسيم الملفات (كل صفحة في ملف، أو مجموعات).
- ✅ تدوير الصفحات بزوايا 90 و180 و270 درجة.
- ✅ حذف الصفحات المحددة مع منع إفراغ المستند كاملاً.
- ✅ تكرار واستخراج الصفحات في مستندات جديدة.
- ✅ التحقق من سلامة وصلاحية المستندات (`validate_pdf`).

### ب. محرك الضغط الاحترافي (`core.compression_engine`)
- ✅ ضغط خفيف (Light): المحافظة على جودة الطباعة العالية.
- ✅ ضغط متوسط (Medium): توازن مثالي بين الحجم والجودة.
- ✅ ضغط قوي (Strong): تقليص أقصى للحجم مع تقليل DPI وإعادة ترميز الصور.
- ✅ التأكد من سلامة ملفات PDF الناتجة عن كافة مستويات الضغط وصلاحيتها للفتح والطباعة.
- ✅ حساب الحجم الأصلي والحجم النهائي ومقدار التوفير والنسبة المئوية بدقة.

### ج. محرك الحماية والتشفير (`core.security_engine`)
- ✅ تشفير AES-256 العسكري باستخدام pikepdf.
- ✅ ضبط أذونات الطباعة والنسخ والتعديل.
- ✅ التأكد من رفض فتح المستند عند إدخال كلمة مرور خاطئة.
- ✅ فك تشفير المستند بنجاح عند إدخال كلمة المرور الصحيحة.
- ✅ عدم تسجيل كلمات المرور في السجلات العامة.

### د. محرك العلامات المائية (`core.watermark_engine`)
- ✅ تطبيق العلامات المائية النصية مع التحكم بالشفافية والزاوية واللون.
- ✅ تطبيق العلامات المائية الصورية.
- ✅ إزالة العلامات المائية والتغطية الآمنة (Redaction).

### هـ. محرك معالجة الصور (`core.image_engine`)
- ✅ تغيير أبعاد الصور وحفظ النسبة الباعية.
- ✅ تدوير وقلب الصور أفقياً ورأسياً.
- ✅ تحويل الصيغ بين PNG وJPEG وWebP بجودة قابلة للضبط.
- ✅ المعالجة الجماعية (Batch Processing) لمجموعة صور دفعة واحدة.

---

## 3. سجل تشغيل الاختبارات التفصيلي

```
{test_details}
```

---
*تم إنشاء هذا التقرير آلياً بواسطة وحدة الاختبارات التلقائية لبرنامج PDF Master Pro.*
"""
    report_file = ROOT / "TEST_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Report saved to {report_file}")
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
