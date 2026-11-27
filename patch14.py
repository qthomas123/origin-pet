# เวอร์ชัน 14: กู้คืนประวัติของอารินจาก history_arin.txt
# ต้องรันหลัง patch13.py
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
        raise SystemExit("patch14: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = J + "PetService.java"
t = rd(p)
# กู้เฉพาะตอนที่ในแอปยังไม่มีประวัติอาริน จึงไม่เขียนทับของที่มีอยู่
t = rep(t, '        String h = MemStore.read(this, "history.txt");\n',
'''        SharedPreferences arinSp = getSharedPreferences("pet", Context.MODE_PRIVATE);
        String ha = MemStore.read(this, "history_arin.txt");
        if (ha != null && arinSp.getString("memory_a", "[]").equals("[]")) {
            try {
                arinSp.edit().putString("memory_a", new JSONArray(ha).toString()).apply();
            } catch (Exception ignored) {
            }
        }
        String h = MemStore.read(this, "history.txt");
''')
wr(p, t)

# ปุ่มล้างความจำต้องล้างไฟล์ของอารินด้วย
p = J + "MemStore.java"
t = rd(p)
t = rep(t, '        write(c, "history.txt", "[]");\n',
        '        write(c, "history.txt", "[]");\n        write(c, "history_arin.txt", "[]");\n')
wr(p, t)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 14", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "14.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch14: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v14"', t)
if n != 1:
    raise SystemExit("patch14: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch14 สำเร็จ: กู้คืนประวัติอารินได้")
