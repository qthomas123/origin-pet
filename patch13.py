# เวอร์ชัน 13: สวิตช์ออนไลน์ของ AI (ค่าเริ่มต้น: ปิด)
# ต้องรันหลัง patch12.py
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
        raise SystemExit("patch13: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = J + "PetService.java"
t = rd(p)

# ตัวเช็กสวิตช์
t = rep(t, "    private String postModels(String[] models, String key, JSONObject body) {\n",
'''    private boolean isOnline() {
        return getSharedPreferences("pet", Context.MODE_PRIVATE).getBoolean("online", false);
    }

    private String postModels(String[] models, String key, JSONObject body) {
''')

# จุดส่งข้อมูลทั้งสอง: เช็กก่อนเชื่อมต่อทุกครั้ง
t = rep(t, '''        for (String model : models) {
            HttpURLConnection con = null;
''', '''        for (String model : models) {
            if (!isOnline()) {
                return null;
            }
            HttpURLConnection con = null;
''')
t = rep(t, '''            for (int attempt = 0; attempt < 2; attempt++) {
                HttpURLConnection con = null;
''', '''            for (int attempt = 0; attempt < 2; attempt++) {
                if (!isOnline()) {
                    lastErr = "ปิดโหมดออนไลน์อยู่";
                    return null;
                }
                HttpURLConnection con = null;
''')

# ไม่ย่อหรือลบประวัติขณะออฟไลน์
t = rep(t, '''        if (history.length() <= MAX_TURNS) {
            return;
        }
''', '''        if (!isOnline() || history.length() <= MAX_TURNS) {
            return;
        }
''')

# เซร่าตอนออฟไลน์
t = rep(t, "    private void startSage(final String question) {\n",
'''    private void startSage(final String question) {
        if (!isOnline()) {
            append("\\n(ออฟไลน์อยู่: เซร่ายังค้นหาไม่ได้ เปิดออนไลน์ในแอปก่อนนะคะ)\\n");
            return;
        }
''')

# แชตตอนออฟไลน์: ตอบในเครื่อง และไม่แก้ประวัติ
t = rep(t, '''        SharedPreferences sp = getSharedPreferences("pet", Context.MODE_PRIVATE);
        final String key = sp.getString("key", "");
        if (key.isEmpty()) {
''', '''        if (!isOnline()) {
            if (input != null) {
                input.setText("");
            }
            append("\\nQ: " + text + "\\n");
            if (text.equals("เวลา")) {
                append("ไอริน: ตอนนี้ "
                        + new java.text.SimpleDateFormat("HH:mm", Locale.US).format(new java.util.Date())
                        + " น. ค่ะ\\n");
            } else {
                append("ไอริน: ตอนนี้ออฟไลน์อยู่ค่ะ ใช้ได้: เวลา, สภาวะ ถ้าอยากคุยกับ AI ให้เปิดออนไลน์ในแอปนะคะ\\n");
            }
            return;
        }
        SharedPreferences sp = getSharedPreferences("pet", Context.MODE_PRIVATE);
        final String key = sp.getString("key", "");
        if (key.isEmpty()) {
''')

# งานความจำเบื้องหลัง: ข้ามขณะออฟไลน์
t, n = re.subn(r"(\n    private void memoTick\(\) \{\n)",
               r"\1        if (!isOnline()) {\n            return;\n        }\n", t)
if n != 1:
    raise SystemExit("patch13: หา memoTick ไม่เจอ")
wr(p, t)

# ปุ่มสวิตช์ในหน้าแอป
p = J + "MainActivity.java"
t = rd(p)
t = rep(t, '        addButton(root, "1) อนุญาตแสดงทับแอปอื่น",',
'''        final android.widget.Button netBtn = new android.widget.Button(this);
        netBtn.setAllCaps(false);
        netBtn.setText(getSharedPreferences("pet", MODE_PRIVATE).getBoolean("online", false)
                ? "AI ออนไลน์: เปิด" : "AI ออนไลน์: ปิด");
        netBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean on = !getSharedPreferences("pet", MODE_PRIVATE).getBoolean("online", false);
                getSharedPreferences("pet", MODE_PRIVATE).edit().putBoolean("online", on).apply();
                netBtn.setText(on ? "AI ออนไลน์: เปิด" : "AI ออนไลน์: ปิด");
            }
        });
        root.addView(netBtn);

        addButton(root, "1) อนุญาตแสดงทับแอปอื่น",''')
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v13"', t)
if n != 1:
    raise SystemExit("patch13: หาชื่อหัวแอปไม่เจอ")
wr(p, t)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 13", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "13.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch13: แก้เวอร์ชันไม่ได้")
wr(p, t)
print("patch13 สำเร็จ: เพิ่มสวิตช์ AI ออนไลน์ (ค่าเริ่มต้น: ปิด)")
