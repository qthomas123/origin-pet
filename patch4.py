#!/usr/bin/env python3
# เวอร์ชัน 4: เพิ่มเซจ นักค้นคว้า (ค้นเว็บได้) และกระดานกลางของทีม  (รันต่อจาก patch3b.py)
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
        raise SystemExit("patch4: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


p = ROOT + "/app/build.gradle"
t = rd(p)
t = rep(t, 'versionCode 3', 'versionCode 4')
t = rep(t, 'versionName "3.0"', 'versionName "4.0"')
wr(p, t)

p = J + "MemStore.java"
t = rd(p)
t = rep(t, 'write(c, "history.txt", "[]");', 'write(c, "history.txt", "[]");\n        write(c, "board.txt", "");')
wr(p, t)

p = J + "MainActivity.java"
t = rd(p)
t = rep(t, '"Origin Pet v3"', '"Origin Pet v4"')
t = rep(t, '.remove("important").apply();', '.remove("important").remove("board").apply();')
wr(p, t)

p = J + "PetService.java"
t = rd(p)

t = rep(t, 'ไม่จำเรื่องเล็กน้อย";',
        'ไม่จำเรื่องเล็กน้อย "\n'
        '                    + "ทีมของคุณมีเซจ นักค้นคว้าที่ค้นเว็บได้ ถ้า Q ถามข่าวสาร ข้อมูลล่าสุด หรือเรื่องที่คุณไม่แน่ใจ "\n'
        '                    + "ให้ตอบสั้นๆ ว่าจะให้เซจช่วย แล้วใส่แท็ก [ถามเซจ:คำถามที่ชัดเจนและครบในตัว] ท้ายคำตอบ";')

t = rep(t, "    private FxView fx;",
        "    private FxView fx;\n    private boolean sageBusy = false;\n    private String board = \"\";")

t = rep(t, 'important = sp.getString("important", "");',
        'important = sp.getString("important", "");\n        board = sp.getString("board", "");')

t = rep(t, 'String h = MemStore.read(this, "history.txt");',
        'String bd = MemStore.read(this, "board.txt");\n'
        '        if (bd != null && !bd.trim().isEmpty()) {\n'
        '            board = bd.trim();\n'
        '        }\n'
        '        String h = MemStore.read(this, "history.txt");')

t = rep(t, '"|จำ:[^\\\\]]*|', '"|ถามเซจ:[^\\\\]]*|จำ:[^\\\\]]*|')

t = rep(t, 'Matcher mm = Pattern.compile("\\\\[จำ:([^\\\\]]{1,300})\\\\]").matcher(s);',
        'Matcher sm = Pattern.compile("\\\\[ถามเซจ:([^\\\\]]{1,300})\\\\]").matcher(s);\n'
        '            if (sm.find()) {\n'
        '                startSage(sm.group(1).trim());\n'
        '            }\n'
        '            Matcher mm = Pattern.compile("\\\\[จำ:([^\\\\]]{1,300})\\\\]").matcher(s);')

t = rep(t, "sb.append(screenContext());",
        'if (!board.isEmpty()) {\n'
        '            sb.append("\\n\\nกระดานกลางของทีม (ผลงานของเซจ):\\n")\n'
        '                    .append(board.length() > 1500 ? board.substring(board.length() - 1500) : board);\n'
        '        }\n'
        '        sb.append(screenContext());')

t = rep(t, "final String text = t;",
        'final String text = t;\n'
        '        if (text.startsWith("เซจ")) {\n'
        '            if (input != null) {\n'
        '                input.setText("");\n'
        '            }\n'
        '            append("\\nQ: " + text + "\\n");\n'
        '            String qs = text.substring(2).trim();\n'
        '            startSage(qs.isEmpty() ? "ทักทาย Q หน่อย" : qs);\n'
        '            return;\n'
        '        }')

NEW = r'''private static final String SAGE =
            "คุณคือเซจ นักค้นคว้าในทีมเอไอของ Q และไอริน ตอบเป็นภาษาไทย ตรงประเด็น ถูกต้อง "
                    + "ใช้ข้อมูลล่าสุดจากการค้นหาเมื่อจำเป็น แยกข้อเท็จจริงออกจากความเห็น ไม่เกิน 10 ประโยค "
                    + "ไม่ใช้ตัวหนาหรือสัญลักษณ์มาร์กดาวน์ ถ้าไม่แน่ใจให้บอกว่าไม่แน่ใจ";
    private static final String[] SAGE_MODELS = {
            "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"
    };

    private String postModels(String[] models, String key, JSONObject body) {
        byte[] payload = body.toString().getBytes(StandardCharsets.UTF_8);
        for (String model : models) {
            HttpURLConnection con = null;
            try {
                URL url = new URL("https://generativelanguage.googleapis.com/v1beta/models/"
                        + model + ":generateContent");
                con = (HttpURLConnection) url.openConnection();
                con.setConnectTimeout(15000);
                con.setReadTimeout(60000);
                con.setRequestMethod("POST");
                con.setDoOutput(true);
                con.setRequestProperty("Content-Type", "application/json");
                con.setRequestProperty("x-goog-api-key", key);
                OutputStream os = con.getOutputStream();
                os.write(payload);
                os.close();
                if (con.getResponseCode() == 200) {
                    JSONObject j = new JSONObject(readAll(con.getInputStream()));
                    JSONArray parts = j.getJSONArray("candidates").getJSONObject(0)
                            .getJSONObject("content").getJSONArray("parts");
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < parts.length(); i++) {
                        sb.append(parts.getJSONObject(i).optString("text", ""));
                    }
                    if (sb.length() > 0) {
                        return sb.toString();
                    }
                }
            } catch (Exception ignored) {
            } finally {
                if (con != null) {
                    con.disconnect();
                }
            }
        }
        return null;
    }

    private String askSage(String key, String question) {
        try {
            JSONObject body = new JSONObject();
            String sys = SAGE + (important.isEmpty() ? "" : "\n\nข้อมูลสำคัญของ Q:\n" + important);
            body.put("system_instruction", new JSONObject()
                    .put("parts", new JSONArray().put(new JSONObject().put("text", sys))));
            body.put("contents", new JSONArray().put(item("user", question)));
            body.put("tools", new JSONArray().put(new JSONObject().put("google_search", new JSONObject())));
            String out = postModels(SAGE_MODELS, key, body);
            if (out == null) {
                body.remove("tools");
                out = postModels(SAGE_MODELS, key, body);
            }
            return out;
        } catch (Exception e) {
            return null;
        }
    }

    private String trimBoard(String b) {
        String s = b.trim();
        return s.length() > 6000 ? s.substring(s.length() - 6000) : s;
    }

    private void saveBoard() {
        getSharedPreferences("pet", Context.MODE_PRIVATE).edit().putString("board", board).apply();
        final String snap = board;
        new Thread(new Runnable() {
            @Override
            public void run() {
                MemStore.write(PetService.this, "board.txt", snap);
            }
        }).start();
    }

    private void startSage(final String question) {
        if (sageBusy) {
            append("\n(เซจกำลังทำงานอยู่ รอสักครู่นะคะ)\n");
            return;
        }
        final String key = getSharedPreferences("pet", Context.MODE_PRIVATE).getString("key", "");
        if (key.isEmpty()) {
            append("\n(ยังไม่ได้ใส่ API key ในแอป Origin Pet)\n");
            return;
        }
        sageBusy = true;
        append("\nเซจ: รับทราบ กำลังค้นหาเรื่อง " + question + " ...\n");
        if (pet != null) {
            pet.setMood(PetView.THINK, 900);
        }
        new Thread(new Runnable() {
            @Override
            public void run() {
                final String ans = askSage(key, question);
                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        sageBusy = false;
                        if (pet != null) {
                            pet.setMood(PetView.NONE, 0);
                        }
                        if (ans == null) {
                            append("เซจ: ขอโทษค่ะ ค้นหาไม่สำเร็จตอนนี้ ลองใหม่อีกครั้งนะคะ\n");
                            return;
                        }
                        String clean = ans.trim();
                        append("เซจ: " + clean + "\n");
                        board = trimBoard(board + "\n[เซจตอบเรื่อง: " + question + "]\n" + clean);
                        saveBoard();
                        if (!busy) {
                            try {
                                history.put(item("user", "[รายงานจากเซจ เรื่อง " + question + "] " + clean));
                                history.put(item("model", "รับทราบค่ะ"));
                            } catch (Exception ignored) {
                            }
                        }
                        speak(clean);
                    }
                });
            }
        }).start();
    }

    private String systemText() {'''
t = rep(t, "private String systemText() {", NEW)
wr(p, t)

print("patch4 สำเร็จ: เพิ่มเซจและกระดานกลาง")
