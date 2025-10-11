# دليل إعداد Workspace في تطبيق LogiStay

## المشكلة الأساسية
عند تثبيت تطبيق LogiStay على خادم جديد، لا يتم إنشاء Workspace تلقائياً، مما يتطلب إعداد يدوي.

## الحل المطبق

### 1. هيكل الملفات المطلوب

```
apps/logistay/logistay/
├── hooks.py                          # تكوين التطبيق الأساسي
├── install.py                        # ملف التثبيت التلقائي
├── patches/
│   └── v1_0/
│       └── setup_workspaces.py       # patch لإعداد Workspace
├── fleet_management/
│   └── workspace/
│       └── fleet_management.json     # تعريف workspace إدارة الأسطول
└── accommodation_management/
    └── workspace/
        └── accommodation_management.json  # تعريف workspace إدارة الإقامة
```

### 2. ملف hooks.py

```python
app_name = "logistay"
app_title = "LogiStay"
app_publisher = "AFMCOltd"
app_description = "LogiStay: Fleet and Accommodation Management"
app_email = "afm@afmcoltd.com"
app_license = "MIT"

# Installation hooks - يتم تنفيذها عند تثبيت التطبيق
after_install = "logistay.install.after_install"

# Fixtures - لتصدير واستيراد البيانات
fixtures = [
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["Fleet Management", "Accommodation Management"]]
        ]
    }
]
```

### 3. ملف install.py

هذا الملف يحتوي على الدوال التي تنفذ عند تثبيت التطبيق:

```python
import frappe
import json
import os

def after_install():
    """يتم تنفيذها بعد تثبيت التطبيق"""
    try:
        print("🚀 Setting up LogiStay workspaces...")
        
        # إنشاء workspace إدارة الأسطول
        create_workspace_from_file(
            workspace_name="Fleet Management",
            file_path="fleet_management/workspace/fleet_management.json"
        )
        
        # إنشاء workspace إدارة الإقامة
        create_workspace_from_file(
            workspace_name="Accommodation Management", 
            file_path="accommodation_management/workspace/accommodation_management.json"
        )
        
        frappe.db.commit()
        print("✅ LogiStay workspaces setup completed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error in LogiStay after_install: {str(e)}")
        print(f"❌ Error setting up LogiStay: {str(e)}")

def create_workspace_from_file(workspace_name, file_path):
    """إنشاء workspace من ملف JSON"""
    # ... باقي الكود
```

### 4. ملف patches.txt

```
logistay.patches.v1_0.create_fleet_workspace
logistay.patches.v1_0.setup_workspaces
```

### 5. ملفات Workspace JSON

#### fleet_management.json
```json
{
 "app": "logistay",
 "charts": [],
 "content": "[{\"id\": \"header\", \"type\": \"header\", \"data\": {\"text\": \"Fleet Management\", \"col\": 12}}]",
 "creation": "2025-01-09 12:00:00.000000",
 "docstatus": 0,
 "doctype": "Workspace",
 "hide_custom": 0,
 "icon": "truck",
 "idx": 0,
 "indicator_color": "blue",
 "is_hidden": 0,
 "label": "Fleet Management",
 "modified": "2025-01-09 12:00:00.000000",
 "modified_by": "Administrator",
 "module": "Fleet Management",
 "name": "Fleet Management",
 "owner": "Administrator",
 "public": 1,
 "title": "Fleet Management",
 "type": "Workspace"
}
```

## كيفية عمل النظام

### 1. عند تثبيت التطبيق لأول مرة:
- يتم تنفيذ `after_install` من `hooks.py`
- يتم استدعاء `logistay.install.after_install()`
- يتم قراءة ملفات JSON وإنشاء Workspace تلقائياً

### 2. عند تحديث التطبيق:
- يتم تنفيذ patches من `patches.txt`
- يتم تنفيذ `setup_workspaces.py` إذا لم يتم تنفيذه من قبل

### 3. عند استيراد fixtures:
- يمكن استخدام `bench --site [site] export-fixtures` لتصدير
- يمكن استخدام `bench --site [site] import-fixtures` لاستيراد

## الأوامر المفيدة

### تثبيت التطبيق:
```bash
bench --site [site_name] install-app logistay
```

### تنفيذ patches يدوياً:
```bash
bench --site [site_name] migrate
```

### تصدير workspace:
```bash
bench --site [site_name] export-fixtures
```

### إنشاء workspace يدوياً:
```bash
bench --site [site_name] console
>>> from logistay.install import after_install
>>> after_install()
```

## المزايا

1. **التثبيت التلقائي**: لا حاجة لإعداد يدوي
2. **المرونة**: يمكن تعديل ملفات JSON بسهولة
3. **الأمان**: التحقق من وجود workspace قبل الإنشاء
4. **التوافق**: يعمل مع جميع إصدارات Frappe v13+
5. **سهولة الصيانة**: كود منظم وقابل للقراءة

## نصائح مهمة

1. **تأكد من صحة JSON**: استخدم أدوات التحقق من صحة JSON
2. **اختبر على بيئة تطوير**: قبل النشر على الإنتاج
3. **احتفظ بنسخ احتياطية**: من ملفات workspace
4. **استخدم أسماء واضحة**: للـ workspace والملفات
5. **وثق التغييرات**: في ملف CHANGELOG

## استكشاف الأخطاء

### المشكلة: workspace لا يظهر
```bash
# تحقق من وجود الملف
ls apps/logistay/logistay/fleet_management/workspace/

# تحقق من صحة JSON
cat apps/logistay/logistay/fleet_management/workspace/fleet_management.json | python -m json.tool

# تنفيذ التثبيت يدوياً
bench --site [site] console
>>> from logistay.install import after_install
>>> after_install()
```

### المشكلة: خطأ في التثبيت
```bash
# تحقق من logs
tail -f logs/bench.log

# تنفيذ migrate
bench --site [site] migrate

# إعادة تثبيت التطبيق
bench --site [site] uninstall-app logistay
bench --site [site] install-app logistay
```

## الخلاصة

هذا النظام يضمن إنشاء Workspace تلقائياً عند تثبيت تطبيق LogiStay على أي خادم، مما يوفر تجربة مستخدم سلسة ويقلل من الحاجة للإعداد اليدوي.