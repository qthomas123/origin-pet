# เวอร์ชัน 17: ลอง LiteRT-LM 0.18.1 (0.16.1 เกิด native crash ตอนสร้างคำตอบ)
# ต้องรันหลัง patch16.py
import os
import re

ROOT = "app-project"
J = ROOT + "/app/src/main/java/com/origin/pet/"


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rep(text, old, new):
    if text.count(old) != 1:
        raise SystemExit("patch17: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = ROOT + "/app/build.gradle"
t = rd(p)
t = rep(t, "litertlm-android:0.16.1", "litertlm-android:0.18.1")
t, n1 = re.subn(r"versionCode \d+", "versionCode 17", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "17.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch17: แก้เวอร์ชันไม่ได้")
wr(p, t)

# ใช้โฟลเดอร์แคชใหม่ ไม่ปนกับแคชของรุ่นเก่า
p = J + "OfflineActivity.java"
t = rd(p)
t = rep(t, '''                        Engine e = new Engine(''', '''                        File cache = new File(getCacheDir(), "litertlm-0.18.1");
                        cache.mkdirs();
                        Engine e = new Engine(''')
t = rep(t, "getCacheDir().getAbsolutePath()));", "cache.getAbsolutePath()));")
t = rep(t, 'StringBuilder s = new StringBuilder("== รายงาน AI ออฟไลน์ ==\\n");',
        'StringBuilder s = new StringBuilder("== รายงาน AI ออฟไลน์ (LiteRT-LM 0.18.1) ==\\n");')
wr(p, t)

p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v17"', t)
if n != 1:
    raise SystemExit("patch17: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch17 สำเร็จ: เปลี่ยนเป็น LiteRT-LM 0.18.1")
