#!/usr/bin/env python3
# เวอร์ชัน 8: เปลี่ยนชื่อทีม (ไอริน / อาริน / เซร่า / เซริน) แชทแยกต่อตัวละครแต่ซิงค์ความจำกัน
# + ปุ่มตอบกลับแอบพูด  รันต่อจาก patch7.py
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
        raise SystemExit("patch8: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


def between(text, a, b):
    i = text.index(a)
    j = text.index(b, i)
    return i, j


p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 8", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "8.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch8: แก้เวอร์ชันใน build.gradle ไม่ได้")
wr(p, t)

p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v8"', t)
if n != 1:
    raise SystemExit("patch8: หาชื่อหัวแอปใน MainActivity ไม่เจอ")
t = t.replace("เมโม", "เซริน").replace("เซจ", "เซร่า")
t = rep(t, '.remove("memory").remove("notes")', '.remove("memory").remove("memory_a").remove("notes")')
wr(p, t)

p = J + "PetService.java"
t = rd(p)

for a, b in [
    ("ทีมของคุณมีเซจ", "ทีมของคุณมีเซร่า"),
    ("ให้เซจช่วย", "ให้เซร่าช่วย"),
    ("เซจ: ", "เซร่า: "),
    ("(เซจกำลังทำงาน", "(เซร่ากำลังทำงาน"),
    ("[รายงานจากเซจ", "[รายงานจากเซร่า"),
    ("[เซจตอบเรื่อง", "[เซร่าตอบเรื่อง"),
    ("ผลงานของเซจ", "ผลงานของเซร่า"),
    ("คุณคือเซจ", "คุณคือเซร่า"),
    ("เมโม", "เซริน"),
]:
    t = t.replace(a, b)

t = rep(t, 's.lastIndexOf("\\nไอริน:"), s.lastIndexOf("\\nเซจ:")',
        'Math.max(s.lastIndexOf("\\nไอริน:"), s.lastIndexOf("\\nอาริน:")), s.lastIndexOf("\\nเซร่า:")')

t = rep(t, '} else if (s.startsWith("เซจ", pos)) {',
        '} else if (s.startsWith("อาริน", pos)) {\n                cur = 0xFFF9A8D4;\n'
        '            } else if (s.startsWith("เซร่า", pos) || s.startsWith("เซริน", pos)) {')

t = rep(t, "    private boolean sageBusy = false;\n",
        "    private boolean sageBusy = false;\n    private int activeChar = 0;\n"
        "    private String lastWhisperText = \"\";\n")
t = rep(t, 'private static final String THINK = "ไอริน: ...\\n";',
        'private String THINK = "ไอริน: ...\\n";\n'
        '    private static final String ARIN_P = "ข้อกำหนดสำคัญที่สุด: ตอนนี้คุณไม่ใช่ไอริน คุณคือ อาริน ผู้หญิง "\n'
        '            + "คู่หูของไอรินบนหน้าจอ บุคลิกนิ่ง คม มั่นใจ พูดน้อยแต่แม่น สไตล์สาวนักแฮกเกอร์ไซเบอร์ "\n'
        '            + "ลงท้ายค่ะ/คะ เรียกผู้ใช้ว่า Q กฎและแท็กทุกอย่างด้านล่างใช้เหมือนเดิม "\n'
        '            + "แต่ให้เรียกตัวเองว่า อาริน แทนคำว่า ไอริน";')

t = rep(t, "    private void saveMemory() {\n",
        "    private void saveMemory() {\n"
        "        if (activeChar == 1) {\n"
        "            MemStore.write(this, \"q_profile.txt\", notes);\n"
        "            MemStore.write(this, \"important.txt\", important);\n"
        "            MemStore.write(this, \"history_arin.txt\", history.toString());\n"
        "            getSharedPreferences(\"pet\", Context.MODE_PRIVATE).edit()\n"
        "                    .putString(\"memory_a\", history.toString())\n"
        "                    .putString(\"notes\", notes)\n"
        "                    .apply();\n"
        "            return;\n"
        "        }\n")

i, j = between(t, "    private void buildLogFromHistory() {", "    private JSONObject item(")
fn = t[i:j]
fn = rep(fn, '"(ไอรินจำการคุยครั้งก่อนได้ค่ะ)\\n"', '"(" + charName() + "จำการคุยครั้งก่อนได้ค่ะ)\\n"')
fn = rep(fn, ': "ไอริน: ")', ': (charName() + ": "))')
fn = rep(fn, 'logBuf.append("ไอริน: สวัสดีค่ะ Q มีอะไรให้ช่วยไหมคะ\\n");',
         'logBuf.append(activeChar == 1 ? "อาริน: สวัสดีค่ะ Q อารินอยู่ตรงนี้แล้วนะคะ\\n"\n'
         '                    : "ไอริน: สวัสดีค่ะ Q มีอะไรให้ช่วยไหมคะ\\n");')
t = t[:i] + fn + t[j:]

t = rep(t, 'append("ไอริน: " + applyTags(reply, true) + "\\n");',
        'append(charName() + ": " + applyTags(reply, true) + "\\n");')
t = rep(t, "speakPitch = 1.0f;\n", "speakPitch = activeChar == 1 ? 0.92f : 1.0f;\n") if t.count("speakPitch = 1.0f;\n") == 1 else t

t = rep(t, "if (!dragging) {\n                            toggleChat();",
        "if (!dragging) {\n                            openFor(0);")
i, j = between(t, "    private void onSageTap() {", "    private final Runnable sageStopTalk")
t = t[:i] + "    private void onSageTap() {\n        openFor(1);\n    }\n\n" + t[j:]

t = rep(t, 'title.setText("ไอริน x Origin AI");',
        'title.setText(charName() + " x Origin AI  ⇄");\n'
        '        title.setOnClickListener(new View.OnClickListener() {\n'
        '            @Override\n'
        '            public void onClick(View v) {\n'
        '                ui.post(new Runnable() {\n'
        '                    @Override\n'
        '                    public void run() {\n'
        '                        openFor(1 - activeChar);\n'
        '                    }\n'
        '                });\n'
        '            }\n'
        '        });')
t = rep(t, "bg.setStroke(dpf(1.5f), C_BLUE);", "bg.setStroke(dpf(1.5f), accent());")
t = rep(t, "capsuleBg(0xFF0369A1, C_BLUE)", "capsuleBg(0xFF0369A1, accent())")

t = rep(t, "        chip(row4, b4);\n",
        "        chip(row4, b4);\n"
        "        LinearLayout row5 = hudRow(box);\n"
        "        Button b5 = hudBtn(\"💬 ตอบกลับแอบพูด\", new View.OnClickListener() {\n"
        "            @Override\n"
        "            public void onClick(View v) {\n"
        "                replyWhisper();\n"
        "            }\n"
        "        });\n"
        "        b5.setTextSize(11);\n"
        "        chip(row5, b5);\n"
        "        Button b6 = hudBtn(\"🔍 ถามเซร่า\", new View.OnClickListener() {\n"
        "            @Override\n"
        "            public void onClick(View v) {\n"
        "                if (input != null) {\n"
        "                    input.setText(\"เซร่า \");\n"
        "                    input.setSelection(input.getText().length());\n"
        "                    input.requestFocus();\n"
        "                }\n"
        "            }\n"
        "        });\n"
        "        b6.setTextSize(11);\n"
        "        chip(row5, b6);\n")

t = rep(t, 'if (text.startsWith("เซจ")) {', "if (sagePrefix(text) > 0) {")
t = rep(t, "text.substring(2).trim()", "text.substring(sagePrefix(text)).trim()")

t = rep(t, 'showBubble(clean);\n                            append("\\nไอริน (แอบพูด): " + clean + "\\n");',
        'lastWhisperText = clean;\n                            showBubble(clean);\n'
        '                            append("\\n" + charName() + " (แอบพูด): " + clean + "\\n");')
i, j = between(t, "    private void showBubble(String text) {", "    private void hideBubble() {")
fn = t[i:j]
fn = rep(fn, "| WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE", "| WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL")
fn = rep(fn, "tv.setBackground(g);",
         "tv.setBackground(g);\n        tv.setOnClickListener(new View.OnClickListener() {\n"
         "            @Override\n            public void onClick(View v) {\n"
         "                replyWhisper();\n            }\n        });")
t = t[:i] + fn + t[j:]

t = rep(t, "        sb.append(screenContext());\n        return sb.toString();",
        "        sb.append(teamContext());\n        sb.append(screenContext());\n        return sb.toString();")
old_sys = t[t.index("    private String systemText() {"):t.index("    private String askGemini(String key) {")]
new_sys = '''    private String systemText() {
        String base = activeChar == 1 ? ARIN_P + "\\n\\n" + SYSTEM : SYSTEM;
        if (notes.isEmpty()) {
            return base + extraContext();
        }
        return base + "\\n\\nความจำเกี่ยวกับ Q จากการคุยครั้งก่อน:\\n" + notes + extraContext();
    }

'''
t = t.replace(old_sys, new_sys)

NEW = r'''    private String charName() {
        return activeChar == 1 ? "อาริน" : "ไอริน";
    }

    private int accent() {
        return activeChar == 1 ? 0xFFF472B6 : C_BLUE;
    }

    private int sagePrefix(String s) {
        String[] ps = {"เซร่า", "เซรา", "เซจ"};
        for (String x : ps) {
            if (s.startsWith(x)) {
                return x.length();
            }
        }
        return 0;
    }

    private String otherDigest() {
        try {
            String k = activeChar == 1 ? "memory" : "memory_a";
            JSONArray a = new JSONArray(getSharedPreferences("pet", Context.MODE_PRIVATE).getString(k, "[]"));
            StringBuilder sb = new StringBuilder();
            String who = activeChar == 1 ? "ไอริน" : "อาริน";
            for (int i = Math.max(0, a.length() - 4); i < a.length(); i++) {
                JSONObject o = a.getJSONObject(i);
                String s = stripTags(textOf(o));
                if (s.length() > 160) {
                    s = s.substring(0, 160) + "...";
                }
                sb.append("user".equals(o.optString("role")) ? "Q: " : who + ": ").append(s).append('\n');
            }
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }

    private String teamContext() {
        String other = activeChar == 1 ? "ไอริน" : "อาริน";
        StringBuilder sb = new StringBuilder("\n\nทีมของ Q (ผู้หญิงทั้งหมด): ไอริน ซุกซนแต่ฉลาด กับ อาริน นิ่งคมสไตล์แฮกเกอร์ "
                + "อยู่บนหน้าจอ แยกแชทกันแต่แชร์ความจำร่วมกัน  เซร่านักค้นคว้า และ เซรินผู้ดูแลความจำ ทำงานเบื้องหลัง "
                + "ตอนนี้คุณคือ " + charName() + " ถ้าเกี่ยวข้องคุณปรึกษาหรืออ้างถึง" + other + "ได้");
        String d = otherDigest();
        if (!d.isEmpty()) {
            sb.append("\n\nบทสนทนาล่าสุดของ ").append(other).append(" กับ Q (คุณรับรู้ไว้):\n").append(d);
        }
        return sb.toString();
    }

    private void loadHist(int c) {
        while (history.length() > 0) {
            history.remove(history.length() - 1);
        }
        try {
            JSONArray a = new JSONArray(getSharedPreferences("pet", Context.MODE_PRIVATE)
                    .getString(c == 1 ? "memory_a" : "memory", "[]"));
            for (int i = 0; i < a.length(); i++) {
                history.put(a.getJSONObject(i));
            }
            while (history.length() > 0
                    && !"user".equals(history.getJSONObject(0).optString("role"))) {
                history.remove(0);
            }
            if (history.length() > 0
                    && "user".equals(history.getJSONObject(history.length() - 1).optString("role"))) {
                history.remove(history.length() - 1);
            }
        } catch (Exception ignored) {
        }
    }

    private void switchChar(int c) {
        if (c == activeChar) {
            return;
        }
        saveMemory();
        activeChar = c;
        loadHist(c);
        THINK = charName() + ": ...\n";
        speakPitch = c == 1 ? 0.92f : 1.0f;
        buildLogFromHistory();
    }

    private void openFor(int c) {
        if (chat != null && activeChar == c) {
            closeChat();
            return;
        }
        if (busy && c != activeChar) {
            if (chat == null) {
                toggleChat();
            }
            append("\n(รอ" + charName() + "ตอบให้เสร็จก่อนนะคะ)\n");
            return;
        }
        if (chat != null) {
            closeChat();
        }
        switchChar(c);
        toggleChat();
    }

    private void replyWhisper() {
        if (lastWhisperText.isEmpty()) {
            return;
        }
        hideBubble();
        if (chat == null) {
            openFor(activeChar);
        }
        if (input != null) {
            String w = lastWhisperText.length() > 300 ? lastWhisperText.substring(0, 300) : lastWhisperText;
            input.setText("(ตอบกลับที่" + charName() + "แอบพูดว่า \"" + w + "\") ");
            input.setSelection(input.getText().length());
            input.requestFocus();
        }
    }

    private String systemText() {'''
t = rep(t, "    private String systemText() {", NEW)
wr(p, t)
print("patch8 สำเร็จ: เปลี่ยนชื่อทีม แชทแยกซิงค์กัน ปุ่มตอบกลับแอบพูด")
