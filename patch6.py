#!/usr/bin/env python3
# เวอร์ชัน 6: หน้าต่างแชทสไตล์ HUD, ปุ่มคัดลอก, ปรับขนาดหน้าต่าง, โหมดคุยต่อเนื่อง, กล้องถ่ายภาพส่งให้ไอริน,
# และกุญแจเซ็นชื่อคงที่ (อัปเดตทับได้โดยไม่ต้องลบแอป)
# รันต่อจาก patch4.py (ถ้ามี patch5.py ให้รันก่อน patch6.py ได้)
import base64
import os
import re
import subprocess

ROOT = "app-project"
J = ROOT + "/app/src/main/java/com/origin/pet/"

KS_B64 = """
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
"""


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rep(text, old, new):
    if text.count(old) != 1:
        raise SystemExit("patch6: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


# ---------- กุญแจเซ็นชื่อคงที่ ----------
ks_path = ROOT + "/app/debug.keystore"
os.makedirs(os.path.dirname(ks_path), exist_ok=True)
with open(ks_path, "wb") as f:
    f.write(base64.b64decode("".join(KS_B64.split())))
chk = subprocess.run(["keytool", "-list", "-keystore", ks_path, "-storepass", "android"],
                     capture_output=True, text=True)
if chk.returncode != 0:
    raise SystemExit("patch6: ข้อความกุญแจ (KS_B64) เพี้ยน วางใหม่ให้ครบทุกบรรทัด\n" + chk.stdout + chk.stderr)

# ---------- build.gradle ----------
p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 6", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "6.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch6: แก้เวอร์ชันใน build.gradle ไม่ได้")
t = rep(t, "    buildTypes {",
        "    signingConfigs {\n"
        "        debug {\n"
        "            storeFile file('debug.keystore')\n"
        "            storePassword 'android'\n"
        "            keyAlias 'androiddebugkey'\n"
        "            keyPassword 'android'\n"
        "        }\n"
        "    }\n\n"
        "    buildTypes {")
wr(p, t)

# ---------- MainActivity: ชื่อหัวแอป ----------
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v6"', t)
if n != 1:
    raise SystemExit("patch6: หาชื่อหัวแอปใน MainActivity ไม่เจอ")
wr(p, t)

# ---------- Manifest: ให้แอปมองเห็นแอปกล้อง ----------
p = ROOT + "/app/src/main/AndroidManifest.xml"
t = rd(p)
t = rep(t, '<action android:name="android.intent.action.TTS_SERVICE" />\n        </intent>',
        '<action android:name="android.intent.action.TTS_SERVICE" />\n        </intent>\n'
        '        <intent>\n'
        '            <action android:name="android.media.action.IMAGE_CAPTURE" />\n'
        '        </intent>')
wr(p, t)

# ---------- PickActivity: โหมดกล้อง ----------
p = J + "PickActivity.java"
t = rd(p)
t = rep(t, "public class PickActivity extends Activity {\n",
        "public class PickActivity extends Activity {\n\n    private Uri camUri;\n")
t = rep(t, "        super.onCreate(b);\n        Intent i = new Intent(Intent.ACTION_GET_CONTENT);",
        r'''        super.onCreate(b);
        if (getIntent().getBooleanExtra("cam", false)) {
            if (b != null && b.getString("camUri") != null) {
                camUri = Uri.parse(b.getString("camUri"));
            }
            if (b == null) {
                startCamera();
            }
            return;
        }
        Intent i = new Intent(Intent.ACTION_GET_CONTENT);''')
t = rep(t, "        super.onActivityResult(req, res, data);\n",
        "        super.onActivityResult(req, res, data);\n"
        "        if (req == 2) {\n"
        "            onCamResult(res, data);\n"
        "            return;\n"
        "        }\n")
t = rep(t, "    private InputStream open(Uri uri) throws Exception {",
        r'''    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        if (camUri != null) {
            out.putString("camUri", camUri.toString());
        }
    }

    private void startCamera() {
        try {
            android.content.ContentValues cv = new android.content.ContentValues();
            cv.put(android.provider.MediaStore.Images.Media.DISPLAY_NAME,
                    "irin_cam_" + System.currentTimeMillis() + ".jpg");
            cv.put(android.provider.MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
            if (android.os.Build.VERSION.SDK_INT >= 29) {
                cv.put(android.provider.MediaStore.Images.Media.RELATIVE_PATH, "Pictures/IrinCam");
            }
            camUri = getContentResolver().insert(
                    android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI, cv);
        } catch (Exception e) {
            camUri = null;
        }
        Intent i = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
        if (camUri != null) {
            i.putExtra(android.provider.MediaStore.EXTRA_OUTPUT, camUri);
            i.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
        }
        try {
            startActivityForResult(i, 2);
        } catch (Exception e) {
            dropCam(camUri);
            camUri = null;
            PetService.deliverImage(null);
            finish();
        }
    }

    private void dropCam(Uri u) {
        if (u != null) {
            try {
                getContentResolver().delete(u, null, null);
            } catch (Exception ignored) {
            }
        }
    }

    private void onCamResult(int res, Intent data) {
        final Uri u = camUri;
        camUri = null;
        if (res != RESULT_OK) {
            dropCam(u);
            finish();
            return;
        }
        Bitmap th = null;
        if (u == null && data != null && data.getExtras() != null) {
            Object o = data.getExtras().get("data");
            if (o instanceof Bitmap) {
                th = (Bitmap) o;
            }
        }
        final Bitmap thumb = th;
        new Thread(new Runnable() {
            @Override
            public void run() {
                String b64 = null;
                if (u != null) {
                    b64 = encode(u);
                } else if (thumb != null) {
                    ByteArrayOutputStream bos = new ByteArrayOutputStream();
                    thumb.compress(Bitmap.CompressFormat.JPEG, 85, bos);
                    b64 = Base64.encodeToString(bos.toByteArray(), Base64.NO_WRAP);
                }
                dropCam(u);
                PetService.deliverImage(b64);
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        finish();
                    }
                });
            }
        }).start();
    }

    private InputStream open(Uri uri) throws Exception {''')
wr(p, t)

# ---------- PetService ----------
p = J + "PetService.java"
t = rd(p)

t = rep(t, "    private boolean speakOn = true;",
        "    private boolean speakOn = true;\n"
        "    private boolean convo = false;\n"
        "    private int convoMiss = 0;\n"
        "    private long quietUntil = 0;\n"
        "    private int logH = 170;\n"
        "    private View statusDot;")

# TTS: จบประโยคแล้วค่อยกลับไปฟัง (หน่วงกันไมค์ดูดเสียงตัวเอง)
t = rep(t, "                        public void onDone(String id) {\n                            setTalking(false);",
        "                        public void onDone(String id) {\n                            setTalking(false);\n"
        "                            convoAfterSpeech();")
t = rep(t, 'tts.speak(clean, TextToSpeech.QUEUE_FLUSH, null, "irin");',
        'quietUntil = System.currentTimeMillis() + 2500;\n'
        '        tts.speak(clean, TextToSpeech.QUEUE_FLUSH, null, "irin");')

# ไมค์: ผลลัพธ์เสียง ข้อผิดพลาด และป้ายปุ่ม
t = rep(t, "                        doSend(r.get(0));", "                        handleVoice(r.get(0));")
t = rep(t, r'''                        append("\n(ไมค์ใช้ไม่ได้ รหัส " + error + ")\n");
                    }''',
        r'''                        append("\n(ไมค์ใช้ไม่ได้ รหัส " + error + ")\n");
                    }
                    convoOnError(error);''')
t = rep(t, "    private void setMicText(String s) {\n        if (micBtn != null) {\n            micBtn.setText(s);\n        }\n    }",
        "    private void setMicText(String s) {\n        if (micBtn != null) {\n"
        "            micBtn.setText(convo ? (listening ? \"ฟังอยู่...\" : \"หยุดคุย\") : s);\n        }\n"
        "        refreshStatus();\n    }")

# สถานะ: กำลังคิด / เซเจค้นหา
t = rep(t, "        busy = true;\n        if (pet != null) {\n            pet.setMood(PetView.THINK, 2000);\n        }",
        "        busy = true;\n        if (pet != null) {\n            pet.setMood(PetView.THINK, 2000);\n        }\n        refreshStatus();")
t = rep(t, "                        busy = false;\n                    }\n                });",
        "                        busy = false;\n"
        "                        refreshStatus();\n"
        "                        if (convo && !(speakOn && ttsReady && askOk)) {\n"
        "                            ui.removeCallbacks(convoListenRun);\n"
        "                            ui.postDelayed(convoListenRun, 1200);\n"
        "                        }\n"
        "                    }\n                });")
t = rep(t, "        sageBusy = true;\n        append(", "        sageBusy = true;\n        refreshStatus();\n        append(")
t = rep(t, "                        sageBusy = false;\n                        if (pet != null) {",
        "                        sageBusy = false;\n                        refreshStatus();\n                        if (pet != null) {")

# ปิดแชทแล้วหยุดโหมดคุย
t = rep(t, "    private void closeChat() {\n",
        "    private void closeChat() {\n        convo = false;\n        ui.removeCallbacks(convoListenRun);\n")
t = rep(t, "        micBtn = null;\n        speakBtn = null;",
        "        micBtn = null;\n        statusDot = null;\n        speakBtn = null;")

# วาดข้อความแชทแบบมีสี
t = rep(t, "        if (log != null) {\n            log.setText(logBuf.toString());\n            scrollDown();",
        "        if (log != null) {\n            renderLog();\n            scrollDown();")

# แทนที่ toggleChat ทั้งก้อนด้วยหน้าต่าง HUD
START = "    private void toggleChat() {"
END = "    private void closeChat() {"
if t.count(START) != 1 or t.count(END) != 1:
    raise SystemExit("patch6: หาขอบเขต toggleChat ไม่เจอ")
i = t.index(START)
j = t.index(END)

NEWCHAT = r'''    // ---------------- หน้าต่างแชทสไตล์ HUD ----------------

    private static final int C_BLUE = 0xFF38BDF8;
    private static final int C_GREEN = 0xFF34D399;
    private static final int C_ORANGE = 0xFFFB923C;
    private static final int C_PURPLE = 0xFFA78BFA;

    private int dpf(float v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    private GradientDrawable capsuleBg(int fill, int stroke) {
        GradientDrawable g = new GradientDrawable();
        g.setColor(fill);
        g.setCornerRadius(dp(100));
        g.setStroke(dpf(1.2f), stroke);
        return g;
    }

    private Button hudBtn(String text, View.OnClickListener l) {
        Button b = smallBtn(text, l);
        b.setTextColor(0xFFE2E8F0);
        b.setBackground(capsuleBg(0xFF1E293B, C_BLUE));
        b.setStateListAnimator(null);
        return b;
    }

    private void paintToggle(Button b, boolean on) {
        if (b == null) {
            return;
        }
        if (on) {
            b.setBackground(capsuleBg(0xFF0B3B4A, 0xFF22D3EE));
            b.setTextColor(0xFFA5F3FC);
        } else {
            b.setBackground(capsuleBg(0xFF1F2937, 0xFF374151));
            b.setTextColor(0xFF9CA3AF);
        }
    }

    private void watchToggle(final Button b) {
        b.addTextChangedListener(new android.text.TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int a, int c, int d) {
            }

            @Override
            public void onTextChanged(CharSequence s, int a, int c, int d) {
            }

            @Override
            public void afterTextChanged(android.text.Editable e) {
                paintToggle(b, e.toString().endsWith("เปิด"));
            }
        });
        paintToggle(b, b.getText().toString().endsWith("เปิด"));
    }

    private LinearLayout hudRow(LinearLayout box) {
        LinearLayout r = new LinearLayout(this);
        r.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        p.topMargin = dp(5);
        box.addView(r, p);
        return r;
    }

    private void chip(LinearLayout row, Button b) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        p.leftMargin = dp(2);
        p.rightMargin = dp(2);
        row.addView(b, p);
    }

    private void renderLog() {
        if (log == null) {
            return;
        }
        String s = logBuf.toString();
        android.text.SpannableString sp = new android.text.SpannableString(s);
        int cur = 0xFFF8FAFC;
        int pos = 0;
        while (pos < s.length()) {
            int nl = s.indexOf('\n', pos);
            int end = nl < 0 ? s.length() : nl;
            if (s.startsWith("Q:", pos)) {
                cur = 0xFF38BDF8;
            } else if (s.startsWith("ไอริน", pos)) {
                cur = 0xFFF8FAFC;
            } else if (s.startsWith("เซจ", pos)) {
                cur = 0xFF34D399;
            } else if (s.startsWith("(", pos)) {
                cur = 0xFF94A3B8;
            }
            if (end > pos) {
                sp.setSpan(new android.text.style.ForegroundColorSpan(cur), pos, end,
                        android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
            pos = end + 1;
        }
        log.setText(sp);
    }

    private void refreshStatus() {
        if (statusDot != null) {
            int c = listening ? C_GREEN : busy ? C_ORANGE : sageBusy ? C_PURPLE : C_BLUE;
            GradientDrawable g = new GradientDrawable();
            g.setShape(GradientDrawable.OVAL);
            g.setColor(c);
            g.setStroke(dp(3), (c & 0x00FFFFFF) | 0x55000000);
            statusDot.setBackground(g);
        }
        if (micBtn != null) {
            if (convo) {
                micBtn.setBackground(capsuleBg(0xFF064E3B, C_GREEN));
                micBtn.setTextColor(0xFFA7F3D0);
            } else {
                micBtn.setBackground(capsuleBg(0xFF1E293B, C_BLUE));
                micBtn.setTextColor(0xFFE2E8F0);
            }
        }
    }

    private void copyText(String s) {
        try {
            android.content.ClipboardManager cm =
                    (android.content.ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            cm.setPrimaryClip(android.content.ClipData.newPlainText("irin", s));
            android.widget.Toast.makeText(this, "คัดลอกแล้ว", android.widget.Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            append("\n(คัดลอกไม่สำเร็จ)\n");
        }
    }

    private void copyLast() {
        String s = logBuf.toString();
        int a = Math.max(s.lastIndexOf("\nไอริน:"), s.lastIndexOf("\nเซจ:"));
        if (a < 0) {
            copyText(s.trim());
            return;
        }
        int b = s.indexOf("\nQ:", a + 1);
        String piece = b < 0 ? s.substring(a + 1) : s.substring(a + 1, b);
        copyText(piece.trim());
    }

    private void resizeLog(int deltaDp) {
        logH = Math.max(100, Math.min(430, logH + deltaDp));
        getSharedPreferences("pet", Context.MODE_PRIVATE).edit().putInt("logh", logH).apply();
        if (logScroll != null) {
            LinearLayout.LayoutParams p = (LinearLayout.LayoutParams) logScroll.getLayoutParams();
            p.height = dp(logH);
            logScroll.setLayoutParams(p);
            scrollDown();
        }
    }

    // ---------------- โหมดคุยต่อเนื่อง ----------------

    private final Runnable convoListenRun = new Runnable() {
        @Override
        public void run() {
            if (!convo || chat == null || listening) {
                return;
            }
            if (busy || sageBusy || (tts != null && tts.isSpeaking())
                    || System.currentTimeMillis() < quietUntil) {
                ui.postDelayed(this, 700);
                return;
            }
            toggleMic();
            if (!listening) {
                stopConvo("เปิดไมค์ไม่สำเร็จ ปิดโหมดคุยต่อเนื่องแล้ว");
            }
        }
    };

    private void convoAfterSpeech() {
        ui.post(new Runnable() {
            @Override
            public void run() {
                if (!convo) {
                    return;
                }
                quietUntil = System.currentTimeMillis() + 900;
                ui.removeCallbacks(convoListenRun);
                ui.postDelayed(convoListenRun, 950);
            }
        });
    }

    private void toggleConvo() {
        if (convo) {
            stopConvo("หยุดโหมดคุยต่อเนื่องแล้วค่ะ");
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            append("\n(ยังไม่ได้อนุญาตไมโครโฟน เปิดแอป Origin Pet แล้วกด อนุญาตไมโครโฟน)\n");
            return;
        }
        convo = true;
        convoMiss = 0;
        if (!speakOn) {
            speakOn = true;
            getSharedPreferences("pet", Context.MODE_PRIVATE).edit().putBoolean("speak", true).apply();
            if (speakBtn != null) {
                speakBtn.setText("เสียง: เปิด");
            }
        }
        append("\n(โหมดคุยต่อเนื่อง: พูดได้เลย พูดว่า หยุดคุย หรือกดปุ่มอีกครั้งเพื่อหยุด)\n");
        setMicText("ไมค์");
        ui.removeCallbacks(convoListenRun);
        ui.postDelayed(convoListenRun, 300);
    }

    private void stopConvo(String why) {
        convo = false;
        ui.removeCallbacks(convoListenRun);
        if (listening && sr != null) {
            sr.cancel();
            listening = false;
        }
        setMicText("ไมค์");
        if (why != null) {
            append("\n(" + why + ")\n");
        }
    }

    private void handleVoice(String raw) {
        String t = raw == null ? "" : raw.trim();
        String n = t.replace(" ", "");
        if (convo && (n.contains("หยุดคุย") || n.contains("พอแค่นี้") || n.contains("เลิกคุย")
                || n.equals("พอแล้ว"))) {
            stopConvo("ปิดโหมดคุยต่อเนื่องตามคำสั่งแล้วค่ะ");
            return;
        }
        convoMiss = 0;
        doSend(t);
        if (convo) {
            ui.removeCallbacks(convoListenRun);
            ui.postDelayed(convoListenRun, 1500);
        }
    }

    private void convoOnError(int error) {
        if (!convo) {
            return;
        }
        if (error == SpeechRecognizer.ERROR_NO_MATCH || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT) {
            convoMiss++;
            if (convoMiss >= 3) {
                stopConvo("ไม่ได้ยินเสียงสักพัก ปิดโหมดคุยต่อเนื่องให้แล้วนะคะ");
                return;
            }
            ui.removeCallbacks(convoListenRun);
            ui.postDelayed(convoListenRun, 700);
        } else {
            stopConvo(null);
        }
    }

    private void toggleChat() {
        if (pet != null) {
            pet.setMood(rnd.nextInt(3) == 0 ? PetView.LAUGH : PetView.SMILE, 50);
        }
        if (chat != null) {
            closeChat();
            return;
        }
        logH = getSharedPreferences("pet", Context.MODE_PRIVATE).getInt("logh", 170);

        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(12), dp(10), dp(12), dp(10));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(0xE60B0F19);
        bg.setCornerRadius(dp(20));
        bg.setStroke(dpf(1.5f), C_BLUE);
        box.setBackground(bg);

        LinearLayout head = new LinearLayout(this);
        head.setOrientation(LinearLayout.HORIZONTAL);
        head.setGravity(Gravity.CENTER_VERTICAL);
        statusDot = new View(this);
        LinearLayout.LayoutParams dotLp = new LinearLayout.LayoutParams(dp(12), dp(12));
        dotLp.rightMargin = dp(8);
        head.addView(statusDot, dotLp);
        TextView title = new TextView(this);
        title.setText("ไอริน x Origin AI");
        title.setTextColor(0xFFF8FAFC);
        title.setTextSize(16);
        head.addView(title, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        speakBtn = hudBtn(speakOn ? "เสียง: เปิด" : "เสียง: ปิด", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                speakOn = !speakOn;
                getSharedPreferences("pet", Context.MODE_PRIVATE).edit().putBoolean("speak", speakOn).apply();
                speakBtn.setText(speakOn ? "เสียง: เปิด" : "เสียง: ปิด");
                if (!speakOn && tts != null) {
                    tts.stop();
                    setTalking(false);
                }
            }
        });
        watchToggle(speakBtn);
        LinearLayout.LayoutParams sLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        sLp.rightMargin = dp(6);
        head.addView(speakBtn, sLp);
        head.addView(hudBtn("X", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                closeChat();
            }
        }));
        box.addView(head);

        log = new TextView(this);
        log.setTextColor(0xFFF8FAFC);
        log.setTextSize(15);
        log.setPadding(dp(4), dp(6), dp(4), dp(4));
        logScroll = new ScrollView(this);
        logScroll.addView(log);
        box.addView(logScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(logH)));
        renderLog();
        scrollDown();

        pendImg = new TextView(this);
        pendImg.setText("แนบรูปแล้ว 1 รูป (แตะเพื่อยกเลิก)");
        pendImg.setTextColor(C_BLUE);
        pendImg.setTextSize(13);
        pendImg.setVisibility(pendingImage != null ? View.VISIBLE : View.GONE);
        pendImg.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pendingImage = null;
                pendImg.setVisibility(View.GONE);
            }
        });
        box.addView(pendImg);

        LinearLayout row2 = hudRow(box);
        chip(row2, hudBtn("⚡ ลูกพลัง", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                castSkill(0);
            }
        }));
        chip(row2, hudBtn("🔮 วงเวท", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                castSkill(1);
            }
        }));
        chip(row2, hudBtn("✨ ดาว", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                castSkill(2);
            }
        }));

        LinearLayout row3 = hudRow(box);
        awareBtn = hudBtn(aware ? "รับรู้หน้าจอ: เปิด" : "รับรู้หน้าจอ: ปิด", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleAware();
            }
        });
        watchToggle(awareBtn);
        chip(row3, awareBtn);
        controlBtn = hudBtn(control ? "ควบคุมแอป: เปิด" : "ควบคุมแอป: ปิด", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleControl();
            }
        });
        watchToggle(controlBtn);
        chip(row3, controlBtn);

        LinearLayout row4 = hudRow(box);
        Button b1 = hudBtn("📋 ล่าสุด", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                copyLast();
            }
        });
        b1.setTextSize(11);
        chip(row4, b1);
        Button b2 = hudBtn("📋 ทั้งหมด", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                copyText(logBuf.toString().trim());
            }
        });
        b2.setTextSize(11);
        chip(row4, b2);
        Button b3 = hudBtn("➖ ย่อ", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resizeLog(-50);
            }
        });
        b3.setTextSize(11);
        chip(row4, b3);
        Button b4 = hudBtn("➕ ขยาย", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resizeLog(50);
            }
        });
        b4.setTextSize(11);
        chip(row4, b4);

        LinearLayout row = hudRow(box);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.addView(hudBtn("รูป", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(PetService.this, PickActivity.class);
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
            }
        }));
        Button cam = hudBtn("📷", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(PetService.this, PickActivity.class);
                i.putExtra("cam", true);
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
            }
        });
        LinearLayout.LayoutParams camLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        camLp.leftMargin = dp(4);
        row.addView(cam, camLp);
        micBtn = hudBtn(convo ? "หยุดคุย" : "ไมค์", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleConvo();
            }
        });
        LinearLayout.LayoutParams micLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        micLp.leftMargin = dp(4);
        row.addView(micBtn, micLp);
        input = new EditText(this);
        input.setHint("พิมพ์ข้อความ...");
        input.setHintTextColor(0xFF64748B);
        input.setTextColor(0xFFFFFFFF);
        input.setTextSize(14);
        input.setMaxLines(3);
        GradientDrawable ib = new GradientDrawable();
        ib.setColor(0xFF1E293B);
        ib.setCornerRadius(dp(14));
        ib.setStroke(dpf(1f), 0xFF334155);
        input.setBackground(ib);
        input.setPadding(dp(10), dp(8), dp(10), dp(8));
        LinearLayout.LayoutParams inLp = new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        inLp.leftMargin = dp(6);
        inLp.rightMargin = dp(6);
        row.addView(input, inLp);
        Button send = hudBtn("ส่ง", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (input != null) {
                    doSend(input.getText().toString().trim());
                }
            }
        });
        send.setBackground(capsuleBg(0xFF0369A1, C_BLUE));
        row.addView(send);

        refreshStatus();

        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                screenW - dp(24),
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT);
        lp.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
        lp.y = dp(50);
        lp.softInputMode = WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE;
        chat = box;
        wm.addView(chat, lp);
    }

'''
t = t[:i] + NEWCHAT + t[j:]
wr(p, t)

print("patch6 สำเร็จ: HUD, คัดลอก, ปรับขนาด, คุยต่อเนื่อง, กล้อง, กุญแจเซ็นชื่อคงที่")
