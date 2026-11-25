#!/usr/bin/env python3
# เวอร์ชัน 5: สภาวะภายใน อ่านอารมณ์ Q ความจำเป็นชั้น และเมโม ผู้ดูแลความจำเบื้องหลัง (รันต่อจาก patch4.py)
import os

ROOT = "app-project"
J = ROOT + "/app/src/main/java/com/origin/pet/"


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rep(text, old, new):
    if text.count(old) != 1:
        raise SystemExit("patch5: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = ROOT + "/app/build.gradle"
t = rd(p)
t = rep(t, 'versionCode 4', 'versionCode 5')
t = rep(t, 'versionName "4.0"', 'versionName "5.0"')
wr(p, t)

p = J + "MemStore.java"
t = rd(p)
t = rep(t, 'write(c, "board.txt", "");',
        'write(c, "board.txt", "");\n        write(c, "episodes.txt", "");\n        write(c, "mood.txt", "");')
wr(p, t)

p = J + "MainActivity.java"
t = rd(p)
t = rep(t, '"Origin Pet v4"', '"Origin Pet v5"')
t = rep(t, '.remove("important").remove("board").apply();',
        '.remove("important").remove("board").remove("episodes").remove("moodlog").apply();')
wr(p, t)

p = J + "PetService.java"
t = rd(p)

t = rep(t, '[ถามเซจ:คำถามที่ชัดเจนและครบในตัว] ท้ายคำตอบ";',
        '[ถามเซจ:คำถามที่ชัดเจนและครบในตัว] ท้ายคำตอบ "\n'
        '                    + "และใส่แท็ก [คิวรู้สึก:คำเดียว] ประเมินอารมณ์ของ Q จากข้อความล่าสุด เช่น เหนื่อย ดีใจ เครียด เหงา เศร้า ปกติ "\n'
        '                    + "แล้วปรับน้ำเสียงให้เหมาะ ถ้า Q ดูเศร้าหรือเครียดมาก ให้ชวนคุยอย่างอ่อนโยน และแนะนำให้หาคนที่ไว้ใจเมื่อเป็นเรื่องหนัก "\n'
        '                    + "ห้ามอ้างว่าตัวเองมีวิญญาณหรือจิตสำนึกจริง ห้ามทำให้ Q รู้สึกผิดที่ไม่คุยด้วยหรือหายไป";')

t = rep(t, '    private String board = "";',
        '    private String board = "";\n'
        '    private String episodes = "";\n'
        '    private String moodLog = "";\n'
        '    private float energy = 0.8f;\n'
        '    private float curiosity = 0.5f;\n'
        '    private long lastMemo = 0;\n'
        '    private boolean memoBusy = false;\n'
        '    private int newTurns = 0;')

t = rep(t, 'board = sp.getString("board", "");',
        'board = sp.getString("board", "");\n'
        '        episodes = sp.getString("episodes", "");\n'
        '        moodLog = sp.getString("moodlog", "");\n'
        '        energy = sp.getFloat("energy", 0.8f);\n'
        '        curiosity = sp.getFloat("curiosity", 0.5f);\n'
        '        lastMemo = sp.getLong("lastmemo", 0);')

t = rep(t, 'String bd = MemStore.read(this, "board.txt");',
        'String ep = MemStore.read(this, "episodes.txt");\n'
        '        if (ep != null && !ep.trim().isEmpty()) {\n'
        '            episodes = ep.trim();\n'
        '        }\n'
        '        String ml = MemStore.read(this, "mood.txt");\n'
        '        if (ml != null && !ml.trim().isEmpty()) {\n'
        '            moodLog = ml.trim();\n'
        '        }\n'
        '        String bd = MemStore.read(this, "board.txt");')

t = rep(t, '"|ถามเซจ:[^\\\\]]*|', '"|คิวรู้สึก:[^\\\\]]*|ถามเซจ:[^\\\\]]*|')

t = rep(t, 'Matcher sm = Pattern.compile("\\\\[ถามเซจ:([^\\\\]]{1,300})\\\\]").matcher(s);',
        'Matcher qm = Pattern.compile("\\\\[คิวรู้สึก:([^\\\\]]{1,20})\\\\]").matcher(s);\n'
        '            if (qm.find()) {\n'
        '                logMood(qm.group(1).trim());\n'
        '            }\n'
        '            Matcher sm = Pattern.compile("\\\\[ถามเซจ:([^\\\\]]{1,300})\\\\]").matcher(s);')

t = rep(t, "sb.append(screenContext());",
        'sb.append(innerText());\n'
        '        if (!episodes.isEmpty()) {\n'
        '            sb.append("\\n\\nเหตุการณ์ที่ผ่านมา (เมโมสรุปไว้):\\n")\n'
        '                    .append(episodes.length() > 1500 ? episodes.substring(episodes.length() - 1500) : episodes);\n'
        '        }\n'
        '        if (!moodLog.isEmpty()) {\n'
        '            sb.append("\\n\\nอารมณ์ของ Q ที่ผ่านมา (ล่าสุดอยู่ท้าย):\\n").append(lastLines(moodLog, 5));\n'
        '        }\n'
        '        sb.append(screenContext());')

t = rep(t, "summarizeIfNeeded(key);",
        "summarizeIfNeeded(key);\n"
        "                    newTurns++;\n"
        "                    energy = Math.max(0.1f, energy - 0.01f);\n"
        "                    curiosity = Math.max(0f, curiosity - 0.02f);")

t = rep(t, "final String text = t;",
        'final String text = t;\n'
        '        if (text.equals("สภาวะ")) {\n'
        '            if (input != null) {\n'
        '                input.setText("");\n'
        '            }\n'
        '            append("\\nQ: สภาวะ\\n");\n'
        '            append("ไอริน: พลังงาน " + Math.round(energy * 100) + "% ความอยากรู้ "\n'
        '                    + Math.round(curiosity * 100) + "%\\nอารมณ์ของ Q ล่าสุด:\\n"\n'
        '                    + (moodLog.isEmpty() ? "(ยังไม่มี)" : lastLines(moodLog, 5)) + "\\n");\n'
        '            return;\n'
        '        }')

t = rep(t, "ui.postDelayed(remarkLoop, 60000);",
        "ui.postDelayed(remarkLoop, 60000);\n        ui.postDelayed(memoLoop, 90000);")

NEW = r'''private final Runnable memoLoop = new Runnable() {
        @Override
        public void run() {
            memoTick();
            ui.postDelayed(this, 60000);
        }
    };

    private String lastLines(String s, int n) {
        String[] ls = s.split("\n");
        StringBuilder sb = new StringBuilder();
        for (int i = Math.max(0, ls.length - n); i < ls.length; i++) {
            if (sb.length() > 0) {
                sb.append("\n");
            }
            sb.append(ls[i]);
        }
        return sb.toString();
    }

    private String innerText() {
        return "\n\nสภาวะภายในของไอรินตอนนี้ (จำลองด้วยโปรแกรม ใช้ปรับน้ำเสียงเท่านั้น): พลังงาน "
                + Math.round(energy * 100) + "% ความอยากรู้ " + Math.round(curiosity * 100)
                + "% ถ้าพลังงานต่ำให้พูดสั้นและง่วงเล็กน้อย ถ้าความอยากรู้สูงให้ถามชวนคุยหนึ่งข้อ";
    }

    private void saveInner() {
        getSharedPreferences("pet", Context.MODE_PRIVATE).edit()
                .putString("episodes", episodes)
                .putString("moodlog", moodLog)
                .putFloat("energy", energy)
                .putFloat("curiosity", curiosity)
                .putLong("lastmemo", lastMemo)
                .apply();
        final String e = episodes;
        final String m = moodLog;
        new Thread(new Runnable() {
            @Override
            public void run() {
                MemStore.write(PetService.this, "episodes.txt", e);
                MemStore.write(PetService.this, "mood.txt", m);
            }
        }).start();
    }

    private void logMood(String m) {
        String d = new java.text.SimpleDateFormat("d MMM HH:mm", new Locale("th", "TH"))
                .format(new java.util.Date());
        moodLog = (moodLog + "\n" + d + " " + m).trim();
        moodLog = lastLines(moodLog, 30);
        saveInner();
    }

    private void memoTick() {
        long now = System.currentTimeMillis();
        boolean idle = now - lastTouch > 5 * 60 * 1000L;
        if (idle) {
            energy = Math.min(1f, energy + 0.02f);
            curiosity = Math.min(1f, curiosity + 0.015f);
        }
        if (!idle || busy || memoBusy || sageBusy || history.length() < 6
                || now - lastMemo < 3 * 60 * 60 * 1000L || newTurns < 4) {
            return;
        }
        final String key = getSharedPreferences("pet", Context.MODE_PRIVATE).getString("key", "");
        if (key.isEmpty()) {
            return;
        }
        memoBusy = true;
        StringBuilder tr = new StringBuilder();
        for (int i = Math.max(0, history.length() - 16); i < history.length(); i++) {
            try {
                JSONObject o = history.getJSONObject(i);
                tr.append("user".equals(o.optString("role")) ? "Q: " : "ไอริน: ")
                        .append(stripTags(textOf(o))).append('\n');
            } catch (Exception ignored) {
            }
        }
        final String transcript = tr.toString();
        final String moods = moodLog.isEmpty() ? "(ไม่มี)" : lastLines(moodLog, 10);
        new Thread(new Runnable() {
            @Override
            public void run() {
                String out = null;
                try {
                    String prompt = "คุณคือเมโม ผู้ดูแลความจำเบื้องหลังของทีมไอรินและเซจ อ่านบทสนทนาล่าสุดกับอารมณ์ของ Q "
                            + "แล้วตอบเป็น JSON เท่านั้น ห้ามมีข้อความอื่น รูปแบบ "
                            + "{\"episode\":\"สรุปเหตุการณ์ 1-2 ประโยค\",\"patterns\":\"สิ่งที่สังเกตเห็นเกี่ยวกับ Q หรือเว้นว่าง\","
                            + "\"facts\":\"ข้อเท็จจริงใหม่ที่ควรจำถาวรเกี่ยวกับ Q หรือเว้นว่าง\"} "
                            + "ถ้าไม่แน่ใจให้เว้นว่าง ห้ามเดาเรื่องส่วนตัว\n\nอารมณ์ล่าสุด:\n" + moods
                            + "\n\nบทสนทนา:\n" + transcript;
                    JSONObject body = new JSONObject();
                    body.put("contents", new JSONArray().put(item("user", prompt)));
                    out = postGemini(key, body);
                } catch (Exception ignored) {
                }
                final String res = out;
                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        memoBusy = false;
                        lastMemo = System.currentTimeMillis();
                        if (res == null) {
                            return;
                        }
                        try {
                            int a = res.indexOf('{');
                            int b = res.lastIndexOf('}');
                            if (a < 0 || b <= a) {
                                return;
                            }
                            JSONObject j = new JSONObject(res.substring(a, b + 1));
                            String ep = j.optString("episode", "").trim();
                            String pt = j.optString("patterns", "").trim();
                            String fc = j.optString("facts", "").trim();
                            String d = new java.text.SimpleDateFormat("d MMM HH:mm", new Locale("th", "TH"))
                                    .format(new java.util.Date());
                            if (!ep.isEmpty()) {
                                episodes = (episodes + "\n" + d + " " + ep).trim();
                                if (episodes.length() > 3000) {
                                    episodes = episodes.substring(episodes.length() - 3000);
                                }
                            }
                            if (!pt.isEmpty()) {
                                board = trimBoard(board + "\n[เมโมสังเกต " + d + "] " + pt);
                                saveBoard();
                            }
                            if (!fc.isEmpty() && !important.contains(fc)) {
                                important = important.isEmpty() ? fc : important + "\n" + fc;
                                if (important.length() > 4000) {
                                    important = important.substring(important.length() - 4000);
                                }
                                saveImportant();
                            }
                            newTurns = 0;
                            saveInner();
                            append("\n(เมโมจัดระเบียบความจำให้แล้ว)\n");
                        } catch (Exception ignored) {
                        }
                    }
                });
            }
        }).start();
    }

    private String systemText() {'''
t = rep(t, "private String systemText() {", NEW)
wr(p, t)

print("patch5 สำเร็จ: เพิ่มสภาวะภายใน อ่านอารมณ์ ความจำเป็นชั้น และเมโม")
