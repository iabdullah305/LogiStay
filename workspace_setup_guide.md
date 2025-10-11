# دليل إعداد Workspace في Frappe

## نظرة عامة
هذا الدليل يوضح الطريقة الصحيحة لإنشاء وإعداد Workspace في تطبيقات Frappe، بناءً على التحليل الشامل لنظام مزامنة Frappe.

## المشكلة الشائعة
```
AttributeError: 'Workspace' object has no attribute 'onboarding_list'
```

هذه المشكلة تحدث عادة بسبب:
1. **مسار خاطئ للـ workspace**
2. **هيكل JSON غير مكتمل**
3. **عدم مزامنة الـ workspace بشكل صحيح**

## الهيكل الصحيح للمسارات

### المسار المطلوب
```
apps/{app_name}/{app_name}/{module_name}/workspace/{workspace_name}/{workspace_name}.json
```

### مثال عملي
```
apps/fleet_management/fleet_management/fleet_management/workspace/fleet_management/fleet_management.json
```

### المسار الخاطئ (تجنبه)
```
apps/fleet_management/fleet_management/workspace/fleet_management/fleet_management.json
```

## هيكل ملف JSON المطلوب

### الحقول الأساسية المطلوبة
```json
{
  "doctype": "Workspace",
  "name": "workspace_name",
  "title": "Display Title",
  "module": "Module Name",
  "public": 1,
  "is_standard": 1,
  "is_hidden": 0,
  "icon": "icon-name",
  "sequence_id": 1,
  "blocks": []
}
```

### مثال كامل
```json
{
  "doctype": "Workspace",
  "name": "fleet_management",
  "route": "fleet-management",
  "title": "Fleet Management",
  "module": "Fleet Management",
  "public": 1,
  "is_hidden": 0,
  "is_standard": 1,
  "icon": "folder-open",
  "sequence_id": 1,
  "blocks": [
    {
      "type": "shortcut",
      "title": "DocTypes",
      "links": [
        {
          "type": "DocType",
          "label": "Fleet Vehicle",
          "name": "Fleet Vehicle"
        }
      ]
    }
  ]
}
```

## خطوات الإعداد الصحيحة

### 1. إنشاء الهيكل
```bash
# إنشاء المجلد بالهيكل الصحيح
mkdir -p apps/{app_name}/{app_name}/{module_name}/workspace/{workspace_name}/

# مثال
mkdir -p apps/fleet_management/fleet_management/fleet_management/workspace/fleet_management/
```

### 2. إنشاء ملف JSON
```bash
# إنشاء الملف
touch apps/fleet_management/fleet_management/fleet_management/workspace/fleet_management/fleet_management.json
```

### 3. المزامنة
```bash
# مزامنة التغييرات
bench migrate
```

### 4. التحقق من النجاح
```bash
# فتح console
bench --site {site_name} console

# التحقق من وجود workspace
frappe.get_all("Workspace", fields=["name", "label", "module"])
```

## كيف يعمل نظام المزامنة في Frappe

### 1. عملية المزامنة التلقائية
- Frappe يقوم بمزامنة workspaces تلقائياً أثناء `bench migrate`
- يتم ذلك من خلال `apps/frappe/frappe/model/sync.py`
- `IMPORTABLE_DOCTYPES` تشمل "workspace"

### 2. البحث عن الملفات
- `sync_for()` function تبحث في مسارات محددة
- يجب أن يكون المسار صحيحاً تماماً
- اسم الملف يجب أن يطابق اسم workspace

### 3. الاستيراد
- `import_file_by_path()` تقوم باستيراد ملف JSON
- يتم إنشاء أو تحديث workspace في قاعدة البيانات

## نصائح مهمة

### ✅ افعل
- تأكد من صحة المسار تماماً
- استخدم `bench migrate` للمزامنة
- تحقق من وجود workspace في قاعدة البيانات
- استخدم أسماء متسقة للملفات والمجلدات

### ❌ لا تفعل
- لا تضع workspace في مسار خاطئ
- لا تستخدم `bench restart` للمزامنة
- لا تنس الحقول المطلوبة في JSON
- لا تستخدم أسماء مختلفة للملف والـ workspace

## استكشاف الأخطاء

### مشكلة: workspace لا يظهر
```bash
# تحقق من المسار
ls -la apps/{app_name}/{app_name}/{module_name}/workspace/

# تحقق من صحة JSON
cat apps/{app_name}/{app_name}/{module_name}/workspace/{workspace_name}/{workspace_name}.json | python -m json.tool

# إعادة المزامنة
bench migrate
```

### مشكلة: AttributeError
- تأكد من وجود جميع الحقول المطلوبة
- تحقق من صحة هيكل JSON
- تأكد من أن workspace تم استيراده بنجاح

## مثال عملي: Fleet Management

### الهيكل النهائي
```
apps/fleet_management/fleet_management/fleet_management/workspace/fleet_management/fleet_management.json
```

### الأمر للتحقق
```bash
bench --site afmco.sa console
frappe.get_doc("Workspace", "fleet_management")
```

### النتيجة المتوقعة
```python
{'name': 'fleet_management', 'label': 'fleet_management', 'module': 'Fleet Management'}
```

## الخلاصة

إعداد Workspace في Frappe يتطلب:
1. **مسار صحيح** حسب هيكل Frappe
2. **ملف JSON مكتمل** بجميع الحقول المطلوبة
3. **مزامنة صحيحة** باستخدام `bench migrate`
4. **تحقق من النجاح** في قاعدة البيانات

اتباع هذه الخطوات يضمن عمل workspace بشكل صحيح وتجنب الأخطاء الشائعة.