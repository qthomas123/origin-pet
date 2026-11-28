# เวอร์ชัน 19: ปุ่มสลับ 4 โหมดใน APK เดียว และรายงานเก็บ log ของ tflite / error ที่เคยถูกกรองทิ้ง
# ต้องรันหลัง patch18.py
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
        raise SystemExit("patch19: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = J + "OfflineActivity.java"
t = rd(p)

t = rep(t, '''    private static final int PICK = 15;
''', '''    private static final int PICK = 15;
    private static final String[] MODES = {
            "A: CPU 4000 มีแคช",
            "B: CPU 4000 ไม่ใช้แคช",
            "C: CPU 1024 ไม่ใช้แคช",
            "D: GPU 4000"
    };
    private volatile int mode = 1; // เริ่มที่โหมด B เพราะโหมด A ลองแล้วไม่ผ่าน
''')

# ปุ่มสลับโหมด อยู่เหนือช่องพิมพ์
t = rep(t, '''        input = new EditText(this);
''', '''        final Button modeBtn = new Button(this);
        modeBtn.setAllCaps(false);
        modeBtn.setText("โหมด " + MODES[mode] + " (กดเพื่อเปลี่ยน)");
        modeBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!askBtn.isEnabled()) return;
                mode = (mode + 1) % MODES.length;
                modeBtn.setText("โหมด " + MODES[mode] + " (กดเพื่อเปลี่ยน)");
                worker.execute(new Runnable() {
                    @Override
                    public void run() {
                        if (engine != null) {
                            try {
                                engine.close();
                            } catch (Throwable ignored) {
                            }
                            engine = null;
                        }
                    }
                });
            }
        });
        root.addView(modeBtn);

        input = new EditText(this);
''')

start = t.index('                        File cache = new File(getCacheDir(), "litertlm-0.18.1");')
end = t.index('                        e.initialize();', start)
t = t[:start] + '''                        File cache = new File(getCacheDir(), "litertlm-0.18.1");
                        cache.mkdirs();
                        Backend backend = mode == 3 ? new Backend.GPU() : new Backend.CPU();
                        int tokens = mode == 2 ? 1024 : 4000;
                        String cachePath = (mode == 1 || mode == 2) ? ":nocache" : cache.getAbsolutePath();
                        mark("กำลังโหลดโมเดล โหมด " + MODES[mode]);
                        Engine e = new Engine(new EngineConfig(model().getAbsolutePath(),
                                backend, null, null, tokens, null, cachePath));
''' + t[end:]
t = rep(t, '                        mark("กำลังโหลดโมเดล");\n', '')

t = rep(t, 'ทดสอบ AI ออฟไลน์ (CPU)', 'ทดสอบ AI ออฟไลน์')

# ติดชื่อโหมดไว้กับผลลัพธ์
t = rep(t, 'mark("เกิดข้อผิดพลาด: " + e);', 'mark("โหมด " + MODES[mode] + " เกิดข้อผิดพลาด: " + e);')
t = rep(t, 'show("ผิดพลาด: " + e);', 'show("โหมด " + MODES[mode] + "\\nผิดพลาด: " + e);')
t = rep(t, 'mark("ตอบสำเร็จ");', 'mark("ตอบสำเร็จ โหมด " + MODES[mode]);')
t = rep(t, 'show(answer + "\\n\\n(ใช้เวลา " + sec + " วินาที)");',
        'show(answer + "\\n\\n(โหมด " + MODES[mode] + " ใช้เวลา " + sec + " วินาที)");')
t = rep(t, 's.append("ตั้งค่า: CPU, maxNumTokens=4000\\n");',
        's.append("โหมดที่เลือกตอนนี้: ").append(MODES[mode]).append(\'\\n\');')

# ตัวกรองเดิมทิ้งบรรทัดของ tflite ซึ่งอาจบอกสาเหตุ
start = t.index('                    String low = line.toLowerCase')
end = t.index('            }\n        } catch (Exception e) {\n            return "อ่าน log ไม่ได้: "', start)
t = t[:start] + '''                    String low = line.toLowerCase(java.util.Locale.US);
                    if (low.contains("weight cache: written") || low.contains("magic_number")
                            || low.contains("f debug   :     x")) {
                        continue;
                    }
                    if (line.contains(" E ") || line.contains(" W ") || low.contains("tflite")
                            || low.contains("litert") || low.contains("xnnpack")
                            || low.contains("fatal") || low.contains("abort")) {
                        keep.add(line.length() > 400 ? line.substring(0, 400) : line);
                        if (keep.size() > 80) keep.removeFirst();
                    }
                }
''' + t[end:]
wr(p, t)

# GPU ต้องประกาศไลบรารีของระบบ (ตามเอกสาร LiteRT-LM)
p = ROOT + "/app/src/main/AndroidManifest.xml"
t = rd(p)
t = rep(t, "    </application>",
'''        <uses-native-library android:name="libvndksupport.so" android:required="false" />
        <uses-native-library android:name="libOpenCL.so" android:required="false" />
    </application>''')
wr(p, t)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 19", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "19.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch19: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v19"', t)
if n != 1:
    raise SystemExit("patch19: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch19 สำเร็จ: 4 โหมดทดสอบ + รายงานละเอียดขึ้น")
