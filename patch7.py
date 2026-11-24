#!/usr/bin/env python3
# เวอร์ชัน 7: เซจมีตัวตนบนหน้าจอ (สาวนักแฮกเกอร์สไตล์ไซเบอร์ วาดเงาแสงให้ดูมีมิติ) เดินเล่นเป็นเพื่อนไอริน
# ตอนค้นหาจะยืนนิ่ง สวมแว่นโฮโลแกรม มีแผงข้อมูลลอยรอบตัว  (รันต่อจาก patch4.py หรือ patch6.py)
import os
import re

ROOT = "app-project"
J = ROOT + "/app/src/main/java/com/origin/pet/"

SAGEVIEW = r'''package com.origin.pet;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import android.view.View;

public class SageView extends View {

    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path path = new Path();
    private final RectF r = new RectF();

    private boolean walking = false;
    private boolean talking = false;
    private boolean busy = false;
    private int dir = -1;
    private float t = 0f;
    private float idle = 0f;
    private int blink = 0;
    private int tk = 0;

    static final int SKIN_L = 0xFFFFEDE2;
    static final int SKIN_M = 0xFFF9D2BE;
    static final int SKIN_D = 0xFFD99F8C;
    static final int HAIR_T = 0xFF1B2A63;
    static final int HAIR_B = 0xFF0C8EA6;
    static final int PINK = 0xFFFF4FB8;
    static final int CYAN = 0xFF22E6F2;
    static final int JK_L = 0xFF43307A;
    static final int JK_D = 0xFF150F2D;
    static final int INK = 0xFF1A1440;
    static final int LIP = 0xFFC2406E;

    public SageView(Context c) {
        super(c);
    }

    public void setTalking(boolean b) {
        talking = b;
    }

    public void setBusy(boolean b) {
        busy = b;
    }

    public void tick(boolean isWalking, int direction) {
        walking = isWalking;
        dir = direction;
        if (walking) {
            t += 1f;
        } else {
            idle += 1f;
        }
        tk++;
        if (blink > 0) {
            blink--;
        } else if (Math.random() < 0.012) {
            blink = 5;
        }
        invalidate();
    }

    private void fill(int color) {
        p.setShader(null);
        p.setStyle(Paint.Style.FILL);
        p.setColor(color);
    }

    private void line(int color, float w) {
        p.setShader(null);
        p.setStyle(Paint.Style.STROKE);
        p.setColor(color);
        p.setStrokeWidth(w);
        p.setStrokeCap(Paint.Cap.ROUND);
    }

    private void lin(float x0, float y0, float x1, float y1, int c0, int c1) {
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFFFFFFF);
        p.setShader(new LinearGradient(x0, y0, x1, y1, c0, c1, Shader.TileMode.CLAMP));
    }

    private void rad(float cx, float cy, float rr, int[] cols, float[] pos) {
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFFFFFFF);
        p.setShader(new RadialGradient(cx, cy, rr, cols, pos, Shader.TileMode.CLAMP));
    }

    @Override
    protected void onDraw(Canvas c) {
        float s = getWidth() / 120f;
        c.save();
        c.scale(s, s);
        if (dir < 0) {
            c.scale(-1f, 1f, 60f, 75f);
        }

        float swing = walking ? (float) Math.sin(t * 0.4f) : 0f;
        float bob = walking ? Math.abs((float) Math.sin(t * 0.4f)) * -3f
                : (float) Math.sin(idle * 0.12f) * 1.2f;
        float sway = (float) Math.sin(t * 0.25f + 1f) * (walking ? 4f : 0.8f);
        float legA = swing * 10f;
        float armA = swing * 9f;

        // เงาพื้น
        c.save();
        c.scale(1f, 0.2f, 60f, 142f);
        rad(60f, 142f, 30f, new int[]{0x77000000, 0x00000000}, new float[]{0.2f, 1f});
        c.drawCircle(60f, 142f, 30f, p);
        c.restore();

        // วงโฮโลแกรมใต้เท้าตอนกำลังค้นหา
        if (busy) {
            float pulse = 0.5f + 0.5f * (float) Math.sin(tk * 0.2f);
            line(((int) (80 + 100 * pulse) << 24) | 0x0022E6F2, 1.6f);
            r.set(32f, 135f, 88f, 149f);
            c.drawOval(r, p);
            line(0x5522E6F2, 1f);
            r.set(24f, 132f, 96f, 152f);
            c.drawOval(r, p);
        }

        // ผมยาวด้านหลัง
        path.reset();
        path.moveTo(32f, 40f + bob);
        path.cubicTo(16f + sway, 70f + bob, 20f + sway * 1.6f, 112f + bob, 38f + sway * 2f, 126f + bob);
        path.lineTo(82f + sway * 2f, 126f + bob);
        path.cubicTo(100f + sway * 1.6f, 112f + bob, 104f + sway, 70f + bob, 88f, 40f + bob);
        path.close();
        lin(0f, 20f + bob, 0f, 126f + bob, HAIR_T, HAIR_B);
        c.drawPath(path, p);
        line(PINK, 3f);
        path.reset();
        path.moveTo(30f, 56f + bob);
        path.quadTo(20f + sway, 90f + bob, 32f + sway * 1.6f, 120f + bob);
        c.drawPath(path, p);

        // ขา
        float[] hx = {52f, 68f};
        float[] fx = {52f + legA, 68f - legA};
        for (int i = 0; i < 2; i++) {
            lin(hx[i] - 4f, 0f, hx[i] + 4f, 0f, SKIN_L, SKIN_D);
            line(SKIN_M, 7f);
            c.drawLine(hx[i], 102f + bob, fx[i], 124f, p);
            line(0x66FFFFFF, 1.6f);
            c.drawLine(hx[i] - 1.5f, 104f + bob, fx[i] - 1.5f, 122f, p);
            lin(fx[i] - 8f, 0f, fx[i] + 8f, 0f, JK_L, JK_D);
            r.set(fx[i] - 8f, 119f, fx[i] + 9f, 134f);
            c.drawRoundRect(r, 5f, 5f, p);
            line(CYAN, 1.6f);
            c.drawLine(fx[i] - 6f, 122f, fx[i] + 6f, 122f, p);
            line(PINK, 1.4f);
            c.drawLine(fx[i] - 8f, 131f, fx[i] + 8f, 131f, p);
        }

        // กางเกงขาสั้นเอวสูง
        lin(0f, 92f + bob, 0f, 110f + bob, 0xFF2A2352, 0xFF120E28);
        r.set(43f, 92f + bob, 77f, 110f + bob);
        c.drawRoundRect(r, 6f, 6f, p);
        line(PINK, 1.6f);
        c.drawLine(44f, 94f + bob, 76f, 94f + bob, p);

        // แขน (แขนเสื้อแจ็คเก็ต)
        float[] shx = {44f, 76f};
        float[] hdx;
        float[] hdy;
        if (busy) {
            hdx = new float[]{30f, 90f};
            hdy = new float[]{66f + bob, 62f + bob};
        } else {
            hdx = new float[]{38f - armA, 82f + armA};
            hdy = new float[]{98f + bob, 98f + bob};
        }
        for (int i = 0; i < 2; i++) {
            line(JK_D, 9f);
            c.drawLine(shx[i], 78f + bob, hdx[i], hdy[i], p);
            line(JK_L, 6f);
            c.drawLine(shx[i], 78f + bob, hdx[i], hdy[i], p);
            line(CYAN, 1.2f);
            c.drawLine(shx[i], 80f + bob, hdx[i], hdy[i] - 1f, p);
            fill(SKIN_M);
            c.drawCircle(hdx[i], hdy[i] + (i == 0 ? 1f : 1f), 3.6f, p);
        }

        // ลำตัว: แจ็คเก็ตครอปเรืองแสง + ท็อปด้านใน
        lin(0f, 66f + bob, 0f, 98f + bob, JK_L, JK_D);
        r.set(41f, 66f + bob, 79f, 98f + bob);
        c.drawRoundRect(r, 9f, 9f, p);
        lin(48f, 0f, 72f, 0f, 0xFFF4FDFF, 0xFFBFEFF7);
        r.set(50f, 68f + bob, 70f, 94f + bob);
        c.drawRoundRect(r, 5f, 5f, p);
        line(CYAN, 1.4f);
        c.drawLine(50f, 68f + bob, 50f, 96f + bob, p);
        c.drawLine(70f, 68f + bob, 70f, 96f + bob, p);
        line(PINK, 1.6f);
        c.drawLine(56f, 80f + bob, 64f, 80f + bob, p);
        c.drawLine(60f, 76f + bob, 60f, 84f + bob, p);
        fill(PINK);
        r.set(41f, 94f + bob, 79f, 98f + bob);
        c.drawRoundRect(r, 2f, 2f, p);
        lin(41f, 0f, 79f, 0f, 0x44FFFFFF, 0x00FFFFFF);
        r.set(41f, 66f + bob, 79f, 98f + bob);
        c.drawRoundRect(r, 9f, 9f, p);

        // คอ
        lin(0f, 60f + bob, 0f, 72f + bob, SKIN_D, SKIN_M);
        r.set(54f, 60f + bob, 66f, 71f + bob);
        c.drawRect(r, p);

        // หัว (ไล่เฉดให้ดูมีมิติ)
        rad(52f, 33f + bob, 34f, new int[]{SKIN_L, SKIN_M, SKIN_D}, new float[]{0f, 0.62f, 1f});
        c.drawCircle(60f, 42f + bob, 26f, p);
        fill(0x44FF7FA8);
        c.drawCircle(46f, 56f + bob, 5f, p);
        c.drawCircle(74f, 56f + bob, 5f, p);

        // ผมหน้าม้า + ปอยข้าง
        path.reset();
        path.moveTo(32f, 46f + bob);
        path.quadTo(60f, -22f + bob, 88f, 46f + bob);
        path.quadTo(82f, 30f + bob, 71f, 35f + bob);
        path.quadTo(62f, 20f + bob, 53f, 35f + bob);
        path.quadTo(41f, 29f + bob, 32f, 46f + bob);
        path.close();
        lin(0f, 8f + bob, 0f, 46f + bob, HAIR_T, 0xFF1D5C96);
        c.drawPath(path, p);
        line(HAIR_B, 5f);
        c.drawLine(34f, 46f + bob, 31f + sway * 0.5f, 78f + bob, p);
        c.drawLine(86f, 46f + bob, 89f + sway * 0.5f, 78f + bob, p);
        line(PINK, 2.4f);
        path.reset();
        path.moveTo(50f, 18f + bob);
        path.quadTo(60f, 14f + bob, 70f, 22f + bob);
        c.drawPath(path, p);

        // หูแมวของหูฟังเรืองแสง
        for (int i = 0; i < 2; i++) {
            float sx = i == 0 ? 1f : -1f;
            float ox = i == 0 ? 36f : 84f;
            path.reset();
            path.moveTo(ox - 9f * sx, 24f + bob);
            path.lineTo(ox - 3f * sx, 5f + bob);
            path.lineTo(ox + 10f * sx, 19f + bob);
            path.close();
            lin(0f, 5f + bob, 0f, 24f + bob, JK_L, JK_D);
            c.drawPath(path, p);
            line(CYAN, 1.6f);
            c.drawPath(path, p);
            fill(PINK);
            c.drawCircle(ox - 1f * sx, 17f + bob, 1.8f, p);
        }

        // ตาโต สไตล์สาวมั่นใจ
        boolean up = busy;
        float py = up ? -2f : 0f;
        if (blink > 0) {
            line(INK, 2.4f);
            c.drawLine(43f, 46f + bob, 55f, 46f + bob, p);
            c.drawLine(65f, 46f + bob, 77f, 46f + bob, p);
        } else {
            fill(0xFFFFFFFF);
            r.set(43f, 38f + bob, 56f, 54f + bob);
            c.drawOval(r, p);
            r.set(64f, 38f + bob, 77f, 54f + bob);
            c.drawOval(r, p);
            for (int i = 0; i < 2; i++) {
                float cx = i == 0 ? 50f : 70f;
                rad(cx, 46f + bob + py, 7f, new int[]{0xFF7DF5FF, 0xFF3B7BE8, 0xFF2A1F8F},
                        new float[]{0f, 0.55f, 1f});
                r.set(cx - 5f, 40f + bob + py, cx + 5f, 53f + bob + py);
                c.drawOval(r, p);
                fill(0xFF120C38);
                c.drawCircle(cx, 47f + bob + py, 2.8f, p);
                fill(0xFFFFFFFF);
                c.drawCircle(cx - 1.8f, 43f + bob + py, 1.7f, p);
                c.drawCircle(cx + 2f, 50f + bob + py, 0.9f, p);
            }
        }
        line(INK, 2.6f);
        path.reset();
        path.moveTo(41f, 44f + bob);
        path.quadTo(49f, 35f + bob, 57f, 42f + bob);
        c.drawPath(path, p);
        path.reset();
        path.moveTo(63f, 42f + bob);
        path.quadTo(71f, 35f + bob, 79f, 44f + bob);
        c.drawPath(path, p);
        line(INK, 1.6f);
        c.drawLine(41f, 44f + bob, 38.5f, 41f + bob, p);
        c.drawLine(79f, 44f + bob, 81.5f, 41f + bob, p);

        // แว่นโฮโลแกรม
        fill(busy ? 0x3322E6F2 : 0x1422E6F2);
        r.set(40f, 37f + bob, 80f, 55f + bob);
        c.drawRoundRect(r, 8f, 8f, p);
        line(busy ? 0xFF22E6F2 : 0x9922E6F2, 1.3f);
        c.drawRoundRect(r, 8f, 8f, p);
        if (busy) {
            float sx = 42f + (tk % 36);
            line(0xCCFFFFFF, 1.2f);
            c.drawLine(sx, 38f + bob, sx, 54f + bob, p);
        }

        // ปากยิ้มมุมปาก
        if (talking && (tk % 8) < 4) {
            fill(0xFF7A1F45);
            r.set(55f, 58f + bob, 65f, 65f + bob);
            c.drawOval(r, p);
            fill(0xFFFF8FB0);
            r.set(57f, 62f + bob, 63f, 65f + bob);
            c.drawOval(r, p);
        } else {
            line(LIP, 2.2f);
            path.reset();
            path.moveTo(53f, 60f + bob);
            path.quadTo(61f, 66f + bob, 69f, 58f + bob);
            c.drawPath(path, p);
        }

        // แสงขอบ (rim light) ให้ดูเป็นสามมิติ
        line(0x9922E6F2, 1.8f);
        r.set(34f, 16f + bob, 86f, 68f + bob);
        c.drawArc(r, -70f, 60f, false, p);
        line(0x77FF4FB8, 1.4f);
        r.set(33f, 15f + bob, 87f, 69f + bob);
        c.drawArc(r, 110f, 50f, false, p);

        // แผงโฮโลแกรมโคจรรอบตัวตอนกำลังค้นหา
        if (busy) {
            for (int i = 0; i < 2; i++) {
                float a = tk * 0.07f + i * 3.14159f;
                float px = 60f + (float) Math.cos(a) * 40f;
                float py2 = 40f + (float) Math.sin(a) * 9f + bob;
                float depth = 0.75f + 0.25f * (float) Math.sin(a);
                fill(0x3322E6F2);
                r.set(px - 8f * depth, py2 - 6f * depth, px + 8f * depth, py2 + 6f * depth);
                c.drawRoundRect(r, 2f, 2f, p);
                line(CYAN, 1f);
                c.drawRoundRect(r, 2f, 2f, p);
                line(0xAAFFFFFF, 0.9f);
                c.drawLine(px - 5f * depth, py2 - 2f * depth, px + 5f * depth, py2 - 2f * depth, p);
                c.drawLine(px - 5f * depth, py2 + 1f * depth, px + 2f * depth, py2 + 1f * depth, p);
            }
        }

        p.setShader(null);
        c.restore();
    }
}
'''


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rep(text, old, new):
    if text.count(old) != 1:
        raise SystemExit("patch7: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


wr(J + "SageView.java", SAGEVIEW)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 7", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "7.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch7: แก้เวอร์ชันใน build.gradle ไม่ได้")
wr(p, t)

p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v7"', t)
if n != 1:
    raise SystemExit("patch7: หาชื่อหัวแอปใน MainActivity ไม่เจอ")
wr(p, t)

p = J + "PetService.java"
t = rd(p)

t = rep(t, "    private FxView fx;",
        "    private FxView fx;\n"
        "    private SageView sage;\n"
        "    private WindowManager.LayoutParams sageLp;\n"
        "    private int sageDir = -1;\n"
        "    private int sagePause = 0;\n"
        "    private boolean sageDragging = false;\n"
        "    private int sageW;\n"
        "    private int sageH;\n"
        "    private float speakPitch = 1.0f;")

t = rep(t, "        wm.addView(pet, petLp);\n        ui.post(loop);",
        "        wm.addView(pet, petLp);\n        createSage();\n        ui.post(loop);\n        ui.post(sageLoop);")

# เสียงของเซจทุ้มกว่าไอรินเล็กน้อย
t = rep(t, 'tts.speak(clean, TextToSpeech.QUEUE_FLUSH, null, "irin");',
        'tts.setPitch(speakPitch);\n        tts.speak(clean, TextToSpeech.QUEUE_FLUSH, null, "irin");')
t = rep(t, "                        speak(clean);",
        "                        speakPitch = 0.85f;\n"
        "                        speak(clean);\n"
        "                        speakPitch = 1.0f;")
t = rep(t, '                        append("เซจ: " + clean + "\\n");',
        '                        append("เซจ: " + clean + "\\n");\n'
        '                        sageTalk(clean.length());')

t = rep(t, "        if (pet != null) {\n            try {\n                wm.removeView(pet);\n            } catch (Exception ignored) {\n            }\n            pet = null;\n        }\n        super.onDestroy();",
        "        if (sage != null) {\n            try {\n                wm.removeView(sage);\n            } catch (Exception ignored) {\n            }\n            sage = null;\n        }\n"
        "        if (pet != null) {\n            try {\n                wm.removeView(pet);\n            } catch (Exception ignored) {\n            }\n            pet = null;\n        }\n        super.onDestroy();")

NEW = r'''private void createSage() {
        sageW = dp(100);
        sageH = dp(125);
        sage = new SageView(this);
        sageLp = new WindowManager.LayoutParams(
                sageW, sageH,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT);
        sageLp.gravity = Gravity.TOP | Gravity.START;
        sageLp.x = Math.max(0, screenW - sageW - dp(24));
        sageLp.y = screenH - sageH - dp(90);
        sage.setOnTouchListener(new View.OnTouchListener() {
            float downX, downY;
            int startX, startY;

            @Override
            public boolean onTouch(View v, MotionEvent e) {
                switch (e.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        lastTouch = System.currentTimeMillis();
                        downX = e.getRawX();
                        downY = e.getRawY();
                        startX = sageLp.x;
                        startY = sageLp.y;
                        sageDragging = false;
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        float dx = e.getRawX() - downX;
                        float dy = e.getRawY() - downY;
                        if (Math.abs(dx) > dp(8) || Math.abs(dy) > dp(8)) {
                            sageDragging = true;
                        }
                        if (sageDragging) {
                            sageLp.x = (int) (startX + dx);
                            sageLp.y = (int) (startY + dy);
                            try {
                                wm.updateViewLayout(sage, sageLp);
                            } catch (Exception ignored) {
                            }
                        }
                        return true;
                    case MotionEvent.ACTION_UP:
                        if (!sageDragging) {
                            onSageTap();
                        }
                        sageDragging = false;
                        return true;
                    default:
                        return true;
                }
            }
        });
        try {
            wm.addView(sage, sageLp);
        } catch (Exception e) {
            sage = null;
        }
    }

    private void onSageTap() {
        if (chat == null) {
            toggleChat();
        }
        if (input != null) {
            input.setText("เซจ ");
            input.setSelection(input.getText().length());
            input.requestFocus();
        }
    }

    private final Runnable sageStopTalk = new Runnable() {
        @Override
        public void run() {
            if (sage != null) {
                sage.setTalking(false);
            }
        }
    };

    private void sageTalk(int len) {
        if (sage == null) {
            return;
        }
        sage.setTalking(true);
        ui.removeCallbacks(sageStopTalk);
        ui.postDelayed(sageStopTalk, Math.min(9000L, 1500L + len * 55L));
    }

    private final Runnable sageLoop = new Runnable() {
        @Override
        public void run() {
            if (sage != null) {
                boolean walking = false;
                if (!sageDragging && chat == null && !sageBusy && !sleeping) {
                    if (sagePause > 0) {
                        sagePause--;
                    } else {
                        walking = true;
                        sageLp.x += sageDir * dp(2);
                        if (sageLp.x < 0) {
                            sageLp.x = 0;
                            sageDir = 1;
                        } else if (sageLp.x > screenW - sageW) {
                            sageLp.x = screenW - sageW;
                            sageDir = -1;
                        }
                        if (rnd.nextInt(170) == 0) {
                            sageDir = -sageDir;
                        }
                        if (rnd.nextInt(200) == 0) {
                            sagePause = 40 + rnd.nextInt(90);
                        }
                        try {
                            wm.updateViewLayout(sage, sageLp);
                        } catch (Exception ignored) {
                        }
                    }
                }
                sage.setBusy(sageBusy);
                sage.tick(walking, sageDir);
            }
            ui.postDelayed(this, 33);
        }
    };

    private String systemText() {'''
t = rep(t, "private String systemText() {", NEW)
wr(p, t)

print("patch7 สำเร็จ: เซจมีตัวตนบนหน้าจอ")
