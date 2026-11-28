# เวอร์ชัน 16: ปุ่มดูสาเหตุที่หน้าทดสอบ AI ออฟไลน์เด้ง
# ต้องรันหลัง patch15.py
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
        raise SystemExit("patch16: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = J + "OfflineActivity.java"
t = rd(p)

# ปุ่มรายงาน (อยู่เหนือช่องผลลัพธ์)
t = rep(t, '''        status = new TextView(this);
''', '''        Button whyBtn = new Button(this);
        whyBtn.setText("ดูสาเหตุที่เด้ง (และคัดลอก)");
        whyBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        final String r = report();
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                status.setText(r);
                                android.content.ClipboardManager cm = (android.content.ClipboardManager)
                                        getSystemService(CLIPBOARD_SERVICE);
                                cm.setPrimaryClip(android.content.ClipData.newPlainText("crash", r));
                            }
                        });
                    }
                }).start();
            }
        });
        root.addView(whyBtn);

        status = new TextView(this);
''')

# จดว่าทำถึงขั้นไหน ก่อนเข้าแต่ละขั้น
t = rep(t, '''                    if (engine == null) {
                        Engine e''', '''                    if (engine == null) {
                        mark("กำลังโหลดโมเดล");
                        Engine e''')
t = rep(t, '''                    try (Conversation chat''', '''                    mark("โหลดโมเดลแล้ว กำลังสร้างบทสนทนา");
                    try (Conversation chat''')
t = rep(t, '''                        String answer''', '''                        mark("กำลังตอบ");
                        String answer''')
t = rep(t, '''                        show(answer + ''', '''                        mark("ตอบสำเร็จ");
                        show(answer + ''')
t = rep(t, '''                    show("ผิดพลาด: " + e);
''', '''                    mark("เกิดข้อผิดพลาด: " + e);
                    show("ผิดพลาด: " + e);
''')

# ฟังก์ชันจดขั้นตอนและสร้างรายงาน
t = rep(t, '''    @Override
    protected void onDestroy() {''', '''    private void mark(String step) {
        try (OutputStream out = new FileOutputStream(new File(getFilesDir(), "llm_stage.txt"))) {
            out.write(step.getBytes("UTF-8"));
            out.flush();
        } catch (Exception ignored) {
        }
    }

    private String report() {
        StringBuilder s = new StringBuilder("== รายงาน AI ออฟไลน์ ==\\n");
        s.append("เครื่อง: ").append(android.os.Build.MODEL)
                .append(" Android ").append(android.os.Build.VERSION.RELEASE).append('\\n');
        s.append("ไฟล์โมเดล: ").append(model().exists() ? gb(model().length()) : "ไม่มี").append('\\n');
        try (java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(
                new java.io.FileInputStream(new File(getFilesDir(), "llm_stage.txt")), "UTF-8"))) {
            s.append("ขั้นล่าสุด: ").append(r.readLine()).append('\\n');
        } catch (Exception e) {
            s.append("ขั้นล่าสุด: ยังไม่มีบันทึก\\n");
        }
        if (android.os.Build.VERSION.SDK_INT >= 30) {
            try {
                android.app.ActivityManager am =
                        (android.app.ActivityManager) getSystemService(ACTIVITY_SERVICE);
                int count = 0;
                for (android.app.ApplicationExitInfo x
                        : am.getHistoricalProcessExitReasons(getPackageName(), 0, 20)) {
                    if (!String.valueOf(x.getProcessName()).endsWith(":llm")) continue;
                    s.append("\\n-- การปิดตัวครั้งที่ ").append(count + 1).append(" --\\n");
                    s.append(new java.util.Date(x.getTimestamp())).append('\\n');
                    s.append("reason=").append(x.getReason())
                            .append(" status=").append(x.getStatus())
                            .append(" rss_kb=").append(x.getRss()).append('\\n');
                    s.append(x.getDescription()).append('\\n');
                    if (count == 0) {
                        try (InputStream in = x.getTraceInputStream()) {
                            if (in != null) s.append(readable(in));
                        } catch (Exception e) {
                            s.append("อ่าน trace ไม่ได้: ").append(e).append('\\n');
                        }
                    }
                    if (++count == 2) break;
                }
                if (count == 0) s.append("ระบบไม่มีบันทึกการปิดตัวของหน้าทดสอบ\\n");
            } catch (Exception e) {
                s.append("อ่านบันทึกระบบไม่ได้: ").append(e).append('\\n');
            }
        }
        s.append("\\n-- log ของแอป --\\n").append(logTail());
        // กันคีย์หลุดไปกับรายงาน
        return s.toString().replaceAll("AIza[0-9A-Za-z_\\\\-]{20,}", "[ซ่อนคีย์]")
                .replaceAll("key=[^&\\\\s]+", "key=[ซ่อนคีย์]");
    }

    // ดึงเฉพาะข้อความที่อ่านได้จาก trace (ของ native crash เป็นข้อมูลไบนารี)
    private static String readable(InputStream in) throws java.io.IOException {
        StringBuilder out = new StringBuilder();
        StringBuilder run = new StringBuilder();
        java.io.BufferedInputStream b = new java.io.BufferedInputStream(in);
        int c;
        int total = 0;
        while ((c = b.read()) != -1 && total++ < 2000000 && out.length() < 2500) {
            if (c >= 32 && c < 127) {
                run.append((char) c);
            } else {
                if (run.length() >= 8) out.append(run).append('\\n');
                run.setLength(0);
            }
        }
        return out.toString();
    }

    private static String logTail() {
        java.util.ArrayDeque<String> keep = new java.util.ArrayDeque<>();
        try {
            Process proc = Runtime.getRuntime().exec(new String[]{"logcat", "-d", "-t", "3000"});
            try (java.io.BufferedReader r = new java.io.BufferedReader(
                    new java.io.InputStreamReader(proc.getInputStream(), "UTF-8"))) {
                String line;
                while ((line = r.readLine()) != null) {
                    String low = line.toLowerCase(java.util.Locale.US);
                    if (low.contains("litert") || low.contains("fatal")
                            || low.contains("androidruntime") || low.contains("abort")
                            || low.contains("f debug")) {
                        keep.add(line.length() > 300 ? line.substring(0, 300) : line);
                        if (keep.size() > 40) keep.removeFirst();
                    }
                }
            }
        } catch (Exception e) {
            return "อ่าน log ไม่ได้: " + e;
        }
        if (keep.isEmpty()) return "ไม่พบบรรทัดที่เกี่ยวข้อง";
        StringBuilder s = new StringBuilder();
        for (String line : keep) s.append(line).append('\\n');
        return s.toString();
    }

    @Override
    protected void onDestroy() {''')
wr(p, t)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 16", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "16.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch16: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v16"', t)
if n != 1:
    raise SystemExit("patch16: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch16 สำเร็จ: เพิ่มปุ่มดูสาเหตุที่เด้ง")
