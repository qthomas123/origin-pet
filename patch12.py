#!/usr/bin/env python3
# เวอร์ชัน 12: แก้ไม่ให้สไปรต์เดินค้างเฟรมเดียว (เดิมใช้ walkFr[2] ตายตัว)
# ตอนนี้จะไล่เฟรมเดินทั้งหมด (irin_walk_1..N.png / arin_walk_1..N.png) ตามจังหวะก้าวเดินจริง (phase)
# ทำให้เห็นรอบขาสวิงเต็มรอบ ไม่ใช่ภาพนิ่งภาพเดียวสลับกับ idle
# รันต่อจาก patch11.py (ต้องรันหลัง patch11 เสมอ)
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
        raise SystemExit("patch12: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = J + "AnimeGirl.java"
t = rd(p)

t = rep(
    t,
    "        Bitmap wb = walkFr.length > 2 ? walkFr[2] : walkFr[walkFr.length - 1];\n",
    '''        Bitmap wb;
        if (walkFr.length > 1) {
            float step = (float) (Math.PI * 2.0 / walkFr.length);
            int wi = (int) (phase / step) % walkFr.length;
            if (wi < 0) {
                wi += walkFr.length;
            }
            wb = walkFr[wi];
        } else {
            wb = walkFr[0];
        }
''',
)
wr(p, t)

# ---------- เวอร์ชัน ----------
p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 12", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "12.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch12: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v12"', t)
if n != 1:
    raise SystemExit("patch12: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch12 สำเร็จ: สไปรต์เดินจะไล่ครบทุกเฟรมตามจังหวะก้าวจริงแล้ว")
