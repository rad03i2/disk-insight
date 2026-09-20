# Disk Insight

**Safe, dependency-free local disk usage analysis for Python 3.10+.**

Disk Insight scans a directory without modifying it and turns filesystem metadata into useful answers: what consumes the most space, which extensions dominate storage, which files are old, and what could not be inspected. It is intentionally read-only: there is no delete or cleanup command.

## Why
Storage problems are easier to solve when the evidence is visible. Disk Insight provides a small auditable CLI and Python API instead of silently deleting files or uploading file information to a service.

## Features
- Recursive local directory scanning
- Largest-file ranking with configurable limit/minimum size
- Storage totals grouped by extension
- Old-file discovery by age
- Hidden files excluded by default
- Symbolic links not followed by default
- Permission/I/O failures recorded instead of aborting the scan
- Full machine-readable JSON export
- Stable SHA-256 fingerprint of scan metadata for comparison workflows
- Zero runtime dependencies
- Read-only operation; no network calls or file deletion

## Requirements & installation
Python 3.10 or newer.

```bash
git clone https://github.com/rad03i2/disk-insight.git
cd disk-insight
python -m pip install -e .
```

## Usage
```bash
# Analyze the current directory
disk-insight .

# Show the 30 largest files of at least 10 MiB
disk-insight ~/Downloads --top 30 --min-size 10485760

# Find files older than one year
disk-insight /path/to/data --older-than 365

# Export the complete scan
disk-insight /path/to/data --json report.json

# Explicitly include hidden files
disk-insight . --include-hidden
```

`--follow-symlinks` is available when link traversal is deliberately required. Be careful with cyclic or unexpectedly large linked trees.

## Python API
```python
from pathlib import Path
from disk_insight import scan, human_size

result = scan(Path.home() / "Downloads")
print(result.total_bytes, human_size(result.total_bytes))
for item in result.largest(10):
    print(item.size, item.path)
```

## JSON report
The report contains the resolved root, total bytes, file count, skipped paths/errors, every collected file record, and extension totals. File records contain path, byte size, modification timestamp and extension. Reports can expose filenames and directory structure; treat them as potentially sensitive.

## Project structure
```text
src/disk_insight/core.py   scanner, analysis, JSON export, fingerprint
src/disk_insight/cli.py    command-line interface
src/disk_insight/__init__.py public API
tests/test_core.py         functional tests
.github/workflows/ci.yml   cross-platform CI
```

## Testing
```bash
pip install -e . pytest ruff
ruff check src tests
pytest -q
```
CI runs the same checks on Windows, Linux and macOS using Python 3.10, 3.12 and 3.13.

## Security & privacy
Disk Insight operates locally, makes no network requests, and does not delete or rewrite scanned files. It reads filesystem metadata and paths; scanning protected locations may produce skipped entries. JSON reports may contain sensitive paths, so review them before sharing.

## Limitations
- Reported size is logical file size, not filesystem allocation size.
- Hard-linked files may be counted more than once when reached by different paths.
- Results are a point-in-time scan; files can change while scanning.
- The tool does not estimate safe-to-delete files and intentionally performs no cleanup.
- Permission-restricted files may be skipped and are reported as such.

## Contributing
Bug fixes and focused improvements are welcome. Keep the scanner read-only by default, add tests for behavioral changes, and run `ruff check src tests` plus `pytest -q` before proposing changes.

## License
MIT License — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

**Disk Insight** أداة محلية آمنة ومفتوحة المصدر لتحليل استهلاك مساحة القرص باستخدام Python 3.10 أو أحدث. تفحص مجلدًا دون تعديل محتوياته وتوضح الملفات الأكبر، وأنواع الملفات الأكثر استهلاكًا، والملفات القديمة، والمسارات التي تعذر فحصها.

## لماذا هذا المشروع؟
معالجة امتلاء القرص تبدأ بمعرفة أين تذهب المساحة. صُممت الأداة لتقديم معلومات واضحة وقابلة للتدقيق من دون حذف تلقائي ومن دون رفع أسماء الملفات أو بياناتها إلى خدمة خارجية.

## المزايا
- فحص المجلدات بصورة متكررة.
- ترتيب أكبر الملفات مع تحديد العدد والحد الأدنى للحجم.
- تجميع استهلاك المساحة حسب امتداد الملف.
- اكتشاف الملفات الأقدم من عدد أيام محدد.
- تجاهل الملفات المخفية افتراضيًا.
- عدم تتبع الروابط الرمزية افتراضيًا.
- تسجيل أخطاء الصلاحيات والإدخال/الإخراج بدل إيقاف الفحص بالكامل.
- تصدير تقرير JSON كامل.
- بصمة SHA-256 ثابتة لبيانات الفحص لاستخدامها في المقارنات البرمجية.
- لا توجد مكتبات تشغيل خارجية.
- الأداة للقراءة فقط: لا حذف، لا تنظيف تلقائي، ولا اتصالات شبكية.

## التثبيت
```bash
git clone https://github.com/rad03i2/disk-insight.git
cd disk-insight
python -m pip install -e .
```

## أمثلة الاستخدام
```bash
# فحص المجلد الحالي
disk-insight .

# عرض أكبر 30 ملفًا بحجم 10 MiB فأكثر
disk-insight ~/Downloads --top 30 --min-size 10485760

# الملفات الأقدم من سنة
disk-insight /path/to/data --older-than 365

# إنشاء تقرير JSON
disk-insight /path/to/data --json report.json
```

يمكن استخدام `--include-hidden` لإدخال الملفات المخفية، و`--follow-symlinks` لتتبع الروابط الرمزية بصورة صريحة.

## الاختبارات
```bash
pip install -e . pytest ruff
ruff check src tests
pytest -q
```
يختبر GitHub Actions المشروع على Windows وLinux وmacOS مع Python 3.10 و3.12 و3.13.

## الخصوصية والأمان
كل المعالجة محلية. لا ترسل الأداة البيانات إلى الإنترنت ولا تحذف أو تعيد كتابة الملفات. تقرير JSON قد يحتوي أسماء ومسارات حساسة، لذلك يجب مراجعته قبل مشاركته.

## القيود
- الحجم المعروض هو الحجم المنطقي وليس المساحة الفعلية المحجوزة على نظام الملفات.
- قد تُحسب الروابط الصلبة أكثر من مرة عند الوصول إليها من مسارات مختلفة.
- الملفات قد تتغير أثناء عملية الفحص.
- لا تحدد الأداة الملفات «الآمنة للحذف» ولا تنفذ تنظيفًا تلقائيًا.
- قد تتعذر قراءة بعض المسارات بسبب الصلاحيات، وتظهر ضمن العناصر المتخطاة.

## المساهمة
الإصلاحات والتحسينات المركزة مرحب بها. يجب الحفاظ على مبدأ القراءة فقط افتراضيًا، وإضافة اختبارات للتغييرات السلوكية وتشغيل `ruff` و`pytest` قبل إرسال التعديلات.

## الترخيص
المشروع متاح تحت ترخيص MIT. راجع [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
