[app]

# ชื่อแอปของคิว
title = Origin Pet

# ชื่อแพ็กเกจ (ห้ามมีขีดกลาง ใช้ตัวอักษรเล็กกับจุด)
package.name = originpet

# ชื่อโดเมนแพ็กเกจ
package.domain = org.qthomas

# โฟลเดอร์โค้ดต้นฉบับ
source.dir = .

# นามสกุลไฟล์ที่นำไปแพ็ก
source.include_exts = py,png,jpg,kv,atlas,json,txt

# เวอร์ชันแอป
version = 0.1

# ไลบรารีที่ต้องใช้ (เริ่มจาก python3,kivy ก่อน แล้วค่อยเพิ่มทีหลังได้)
requirements = python3,kivy

# การวางหน้าจอ
orientation = portrait

# เต็มจอหรือไม่ (0 = ไม่เต็มจอ, 1 = เต็มจอ)
fullscreen = 0

# เวอร์ชัน Android SDK / NDK และ API ที่รองรับ
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# สถาปัตยกรรม CPU มือถือ Android ส่วนใหญ่
android.archs = arm64-v8a

[buildozer]

# ระดับ log (0 = น้อย, 1 = ปกติ, 2 = ละเอียด)
log_level = 2

# เตือนถ้ารันเป็น root
warn_on_root = 1
