# เวอร์ชัน 18: จำกัด maxNumTokens = 4000 (ค่าเดียวกับที่ใช้ใน AI Edge Gallery) และรายงานละเอียดขึ้น
# ต้องรันหลัง patch17.py
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
        raise SystemExit("patch18: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = J + "OfflineActivity.java"
t = rd(p)
# พารามิเตอร์ตัวที่ 5 คือ maxNumTokens
t = rep(t, "new Backend.CPU(), null, null, null, null,", "new Backend.CPU(), null, null, 4000, null,")

# เก็บแรมว่างก่อนโหลด
t = rep(t, '                        mark("กำลังโหลดโมเดล");\n',
        '                        ram = memory();\n                        mark("กำลังโหลดโมเดล");\n')
t = rep(t, '    private void mark(String step) {', '''    private String ram = "";

    private String memory() {
        android.app.ActivityManager.MemoryInfo m = new android.app.ActivityManager.MemoryInfo();
        ((android.app.ActivityManager) getSystemService(ACTIVITY_SERVICE)).getMemoryInfo(m);
        return "แรมว่าง " + gb(m.availMem) + " จาก " + gb(m.totalMem);
    }

    private void mark(String step) {''')

# รายงาน: แสดง error ครบทุกบรรทัด และข้อมูลแรม
t = rep(t, '''            s.append("ขั้นล่าสุด: ").append(r.readLine()).append('\\n');
''', '''            s.append("ขั้นล่าสุด: ");
            String line;
            int n = 0;
            while ((line = r.readLine()) != null && n++ < 25) {
                s.append(line).append('\\n');
            }
''')
t = rep(t, '''        if (android.os.Build.VERSION.SDK_INT >= 30) {''',
'''        s.append("ตั้งค่า: CPU, maxNumTokens=4000\\n");
        s.append("ตอนนี้: ").append(memory()).append('\\n');
        if (!ram.isEmpty()) s.append("ก่อนโหลดโมเดล: ").append(ram).append('\\n');
        if (android.os.Build.VERSION.SDK_INT >= 30) {''')

# ถ้าผิดพลาด ปิด engine เพื่อให้รอบหน้าเริ่มโหลดใหม่
t = rep(t, '''                    show("ผิดพลาด: " + e);
''', '''                    show("ผิดพลาด: " + e);
                    if (engine != null) {
                        try {
                            engine.close();
                        } catch (Throwable ignored) {
                        }
                        engine = null;
                    }
''')
wr(p, t)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 18", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "18.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch18: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v18"', t)
if n != 1:
    raise SystemExit("patch18: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch18 สำเร็จ: maxNumTokens=4000")
