#!/usr/bin/env python3
# เวอร์ชัน 9 ก้อนที่ 1: ตัววาดตัวละครอนิเมะ AnimeGirl (รันต่อจาก patch8.py)
import os
import re

ROOT = "app-project"
J = ROOT + "/app/src/main/java/com/origin/pet/"


def wr(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


ANIME = r'''package com.origin.pet;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import android.view.View;

public class AnimeGirl extends View {

    static final int NONE = 0;
    static final int SMILE = 1;
    static final int LAUGH = 2;
    static final int HAPPY = 3;
    static final int SAD = 4;
    static final int SLEEP = 5;
    static final int THINK = 6;
    static final int CAST = 7;

    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path path = new Path();
    private final RectF r = new RectF();

    protected boolean twin = true;
    protected boolean tail = true;
    protected boolean headset = false;
    protected boolean cyber = false;
    protected boolean xian = false;
    protected int lipCol = 0xFF8A3A5C;
    protected int skinL = 0xFFFFEEE3;
    protected int skinD = 0xFFF2C4B0;
    protected int hairA = 0xFF8E5CF0;
    protected int hairB = 0xFFF25CB5;
    protected int eyeA = 0xFF35E0E8;
    protected int eyeB = 0xFF4A3FB8;
    protected int topA = 0xFFF6F4FF;
    protected int topB = 0xFFB9A8F5;
    protected int skirtA = 0xFF3A2F7A;
    protected int skirtB = 0xFF241B55;
    protected int accent = 0xFFF25CB5;
    protected int accent2 = 0xFF35E0E8;
    protected int ink = 0xFF3A2F7A;
    protected int tailCol = 0xFF5B3FB8;

    private boolean walking = false;
    private boolean talking = false;
    private boolean busy = false;
    private int dir = 1;
    private float t = 0f;
    private float idle = 0f;
    private int blink = 0;
    private int mood = NONE;
    private int moodTicks = 0;
    private int mt = 0;
    private int tk = 0;

    public AnimeGirl(Context c) {
        super(c);
    }

    public void setTalking(boolean b) {
        talking = b;
    }

    public void setBusy(boolean b) {
        busy = b;
    }

    public void setMood(int m, int ticks) {
        mood = m;
        moodTicks = ticks;
        mt = 0;
    }

    public boolean isNeutral() {
        return mood == NONE;
    }

    public boolean still() {
        return mood == SAD || mood == SLEEP || mood == THINK;
    }

    public void tick(boolean isWalking, int direction) {
        walking = isWalking;
        dir = direction;
        if (walking) {
            t += 1f;
        } else {
            idle += 1f;
        }
        mt++;
        tk++;
        if (moodTicks > 0) {
            moodTicks--;
            if (moodTicks == 0) {
                mood = NONE;
            }
        }
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

    private void rad(float cx, float cy, float rr, int c0, int c1) {
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFFFFFFF);
        p.setShader(new RadialGradient(cx, cy, rr, new int[]{c0, c1}, new float[]{0f, 1f},
                Shader.TileMode.CLAMP));
    }

    private void oval(float cx, float cy, float rx, float ry) {
        r.set(cx - rx, cy - ry, cx + rx, cy + ry);
    }

    private void star(Canvas c, float x, float y, float s, int col) {
        fill(col);
        path.reset();
        path.moveTo(x, y - s);
        path.quadTo(x, y, x + s, y);
        path.quadTo(x, y, x, y + s);
        path.quadTo(x, y, x - s, y);
        path.quadTo(x, y, x, y - s);
        path.close();
        c.drawPath(path, p);
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
        float bob = walking ? Math.abs((float) Math.sin(t * 0.4f)) * -2.5f
                : (float) Math.sin(idle * 0.12f) * 1.0f;
        float sway = (float) Math.sin(t * 0.25f + 1f) * (walking ? 3.5f : 0.8f);
        float wag = (float) Math.sin(walking ? t * 0.3f : idle * 0.15f) * 7f;
        if (mood == HAPPY) {
            bob -= Math.abs((float) Math.sin(mt * 0.3f)) * 14f;
            wag = (float) Math.sin(mt * 0.9f) * 12f;
        } else if (mood == SAD) {
            bob += 4f;
            wag = 1f;
        } else if (mood == SLEEP) {
            bob += 5f + (float) Math.sin(mt * 0.08f) * 1.2f;
            wag = 0f;
        }
        if (mood == LAUGH) {
            c.translate((float) Math.sin(mt * 1.1f) * 1.6f, 0f);
        }

        // เงาพื้น
        rad(60f, 145f, 26f, 0x55000000, 0x00000000);
        oval(60f, 145f, 26f, 4f);
        c.drawOval(r, p);

        c.save();
        c.translate(0f, bob * 0.4f);
        drawBackHair(c, sway, bob);
        if (tail) {
            drawTail(c, wag);
        }
        drawLegs(c, swing);
        c.restore();

        c.save();
        c.translate(0f, bob);
        drawBody(c);
        drawArms(c, swing);
        drawHead(c, sway);
        c.restore();
        c.restore();
    }

    private void drawBackHair(Canvas c, float sway, float bob) {
        lin(60f, 14f, 60f, 112f, hairA, hairB);
        if (twin) {
            for (int sd = -1; sd <= 1; sd += 2) {
                float x0 = 60f + sd * 17f;
                float sw = sd * sway * 0.7f;
                path.reset();
                path.moveTo(x0, 24f);
                path.cubicTo(x0 + sd * 12f, 34f, x0 + sd * 22f + sw, 62f, x0 + sd * 16f + sw * 1.6f, 100f + bob * 0.3f);
                path.quadTo(x0 + sd * 8f + sw, 90f, x0 + sd * 2f + sw * 0.6f, 62f);
                path.quadTo(x0 - sd * 2f, 40f, x0, 24f);
                path.close();
                lin(x0, 24f, x0, 100f, hairA, hairB);
                c.drawPath(path, p);
            }
        } else {
            if (cyber) {
                lin(60f, 4f, 60f, 18f, hairA, hairB);
                oval(60f, 11f, 7.5f, 6.5f);
                c.drawOval(r, p);
                line(0xFFB04CFF, 2f);
                c.drawLine(53f, 16f, 67f, 16f, p);
            }
            lin(60f, 14f, 60f, 112f, hairA, hairB);
            path.reset();
            path.moveTo(42f, 22f);
            path.cubicTo(30f, 40f, 34f + sway, 84f, 38f + sway * 1.5f, 112f);
            path.quadTo(60f, 104f, 82f + sway * 1.5f, 112f);
            path.cubicTo(86f + sway, 84f, 90f, 40f, 78f, 22f);
            path.close();
            c.drawPath(path, p);
        }
    }

    private void drawTail(Canvas c, float wag) {
        lin(70f, 96f, 100f, 80f, tailCol, accent);
        path.reset();
        path.moveTo(70f, 98f);
        path.cubicTo(86f, 104f, 98f + wag, 92f, 100f + wag, 72f);
        path.cubicTo(92f + wag * 0.6f, 86f, 84f, 90f, 72f, 90f);
        path.close();
        c.drawPath(path, p);
    }

    private void drawLegs(Canvas c, float swing) {
        for (int sd = -1; sd <= 1; sd += 2) {
            float off = sd * swing * 4f;
            float cx = 60f + sd * 7.5f;
            path.reset();
            path.moveTo(cx - 6.5f, 100f);
            path.cubicTo(cx - 8f + off * 0.3f, 114f, cx - 5f + off, 126f, cx - 4f + off, 139f);
            path.lineTo(cx + 3.5f + off, 139f);
            path.cubicTo(cx + 5f + off, 126f, cx + 8f + off * 0.3f, 114f, cx + 6.5f, 100f);
            path.close();
            lin(cx - 7f, 100f, cx + 7f, 100f, skinD, skinL);
            c.drawPath(path, p);
            if (xian) {
                // รองเท้าส้นสูงลายทอง
                fill(accent2);
                path.reset();
                path.moveTo(cx - 4.6f + off, 137f);
                path.lineTo(cx + 3.8f + off, 137f);
                path.lineTo(cx + 6.8f + off, 142f);
                path.lineTo(cx - 5.6f + off, 142f);
                path.close();
                c.drawPath(path, p);
                line(accent, 1.6f);
                c.drawLine(cx - 4.8f + off, 142.5f, cx - 4.8f + off, 146.5f, p);
                line(accent, 1.0f);
                c.drawLine(cx - 4.2f + off, 134f, cx + 3.4f + off, 134f, p);
                continue;
            }
            // ถุงเท้ายาว
            path.reset();
            path.moveTo(cx - 5.6f + off * 0.8f, 119f);
            path.lineTo(cx - 4.3f + off, 139f);
            path.lineTo(cx + 3.6f + off, 139f);
            path.lineTo(cx + 5.6f + off * 0.8f, 119f);
            path.close();
            fill(topA);
            c.drawPath(path, p);
            oval(cx + off, 141f, 6.5f, 3.4f);
            fill(accent);
            c.drawOval(r, p);
        }
    }

    private void drawBody(Canvas c) {
        // ลำตัวเว้าโค้ง: อก เอว สะโพก
        path.reset();
        path.moveTo(50f, 54f);
        path.cubicTo(43f, 58f, 41f, 70f, 47f, 74f);
        path.cubicTo(51f, 77f, 51f, 79f, 50.5f, 82f);
        path.cubicTo(50f, 88f, 43f, 90f, 42.5f, 97f);
        path.lineTo(39f, 108f);
        path.quadTo(60f, 114f, 81f, 108f);
        path.lineTo(77.5f, 97f);
        path.cubicTo(77f, 90f, 70f, 88f, 69.5f, 82f);
        path.cubicTo(69f, 79f, 69f, 77f, 73f, 74f);
        path.cubicTo(79f, 70f, 77f, 58f, 70f, 54f);
        path.close();
        lin(60f, 54f, 60f, 100f, topA, topB);
        c.drawPath(path, p);

        // กระโปรง
        path.reset();
        path.moveTo(43f, 93f);
        path.cubicTo(42f, 97f, 40f, 102f, 38.5f, 109f);
        path.quadTo(60f, 116f, 81.5f, 109f);
        path.cubicTo(80f, 102f, 78f, 97f, 77f, 93f);
        path.quadTo(60f, 99f, 43f, 93f);
        path.close();
        lin(60f, 93f, 60f, 114f, skirtA, skirtB);
        c.drawPath(path, p);
        line(accent, 1.4f);
        path.reset();
        path.moveTo(38.8f, 108f);
        path.quadTo(60f, 114.5f, 81.2f, 108f);
        c.drawPath(path, p);

        // เข็มขัดที่เอว
        line(accent, 2.6f);
        path.reset();
        path.moveTo(50.2f, 83f);
        path.quadTo(60f, 86f, 69.8f, 83f);
        c.drawPath(path, p);

        // เงาและไฮไลต์หน้าอก
        fill(0x14000000);
        oval(53f, 76f, 5.5f, 2.6f);
        c.drawOval(r, p);
        oval(67f, 76f, 5.5f, 2.6f);
        c.drawOval(r, p);
        fill(0x44FFFFFF);
        oval(51f, 65f, 2.4f, 3.4f);
        c.drawOval(r, p);
        oval(69f, 65f, 2.4f, 3.4f);
        c.drawOval(r, p);

        // คอปกวี และโบว์/โลโก้
        path.reset();
        path.moveTo(53f, 54f);
        path.lineTo(60f, 63f);
        path.lineTo(67f, 54f);
        path.close();
        fill(skinL);
        c.drawPath(path, p);
        line(accent, 1.6f);
        path.reset();
        path.moveTo(53f, 54.5f);
        path.lineTo(60f, 63f);
        path.lineTo(67f, 54.5f);
        c.drawPath(path, p);
        fill(accent2);
        c.drawCircle(60f, 66f, 2f, p);
    }

    private void drawArms(Canvas c, float swing) {
        for (int sd = -1; sd <= 1; sd += 2) {
            float sx = 60f + sd * 11.5f;
            float hx = sx + sd * 4f - sd * swing * 2f;
            float hy = 88f + swing * sd * 2f;
            float ex = sx + sd * 5.5f;
            float ey = 72f;
            boolean up = false;
            if (sd == 1 && mood == CAST) {
                hx = sx + 22f;
                hy = 44f;
                ex = sx + 12f;
                ey = 62f;
                up = true;
            } else if (sd == 1 && mood == THINK) {
                hx = 66f;
                hy = 48f;
                ex = sx + 6f;
                ey = 66f;
            } else if (mood == HAPPY) {
                hx = sx + sd * 12f;
                hy = 46f - (float) Math.abs(Math.sin(mt * 0.3f)) * 4f;
                ex = sx + sd * 9f;
                ey = 62f;
            }
            if (xian) {
                float fl = (float) Math.sin((walking ? t : idle) * 0.2f + sd) * 3f;
                fill(0x88CFF5EE);
                path.reset();
                path.moveTo(sx, 56f);
                path.quadTo(sx + sd * 15f + fl, 70f, sx + sd * 13f + fl * 1.6f, 100f);
                path.quadTo(sx + sd * 5f, 88f, sx + sd * 2f, 64f);
                path.close();
                c.drawPath(path, p);
                line(0xAAFFFFFF, 0.8f);
                path.reset();
                path.moveTo(sx + sd * 3f, 66f);
                path.quadTo(sx + sd * 9f + fl, 82f, sx + sd * 12f + fl * 1.5f, 98f);
                c.drawPath(path, p);
            }
            line(0xFFFFFFFF, 0f);
            line(skinL, 4.4f);
            path.reset();
            path.moveTo(sx, 58f);
            path.quadTo(ex, ey, hx, hy);
            c.drawPath(path, p);
            line(topA, 5.6f);
            path.reset();
            path.moveTo(sx, 58f);
            path.lineTo(sx + (ex - sx) * 0.45f, 58f + (ey - 58f) * 0.45f);
            c.drawPath(path, p);
            if (cyber) {
                line(0xFF22222E, 6.4f);
                path.reset();
                path.moveTo(sx, 58f);
                path.lineTo(sx + (ex - sx) * 0.85f, 58f + (ey - 58f) * 0.85f);
                c.drawPath(path, p);
                rad(sx, 58f, 6f, 0xFFFF4FA8, 0x00FF4FA8);
                oval(sx, 58f, 6f, 6f);
                c.drawOval(r, p);
                fill(0xFFFFFFFF);
                c.drawCircle(sx, 58f, 1.3f, p);
                fill(0xFFB04CFF);
                c.drawCircle(hx, hy + 0.5f, 3.9f, p);
            }
            fill(skinL);
            c.drawCircle(hx, hy, 2.8f, p);
            if (up) {
                float g = 5f + (float) Math.sin(mt * 0.5f) * 1.5f;
                rad(hx, hy - 6f, 12f, 0xAAFFFFFF, 0x00FFFFFF);
                oval(hx, hy - 6f, 12f, 12f);
                c.drawOval(r, p);
                star(c, hx, hy - 7f, g + 3f, accent2);
            }
        }
    }

    private void drawHead(Canvas c, float sway) {
        // คอ
        fill(skinD);
        r.set(56f, 47f, 64f, 56f);
        c.drawRect(r, p);

        if (cyber) {
            line(0xFF1B1B26, 2.4f);
            path.reset();
            path.moveTo(55.5f, 52f);
            path.quadTo(60f, 55f, 64.5f, 52f);
            c.drawPath(path, p);
            fill(0xFFB04CFF);
            c.drawCircle(60f, 54f, 1.3f, p);
        }

        // หูแมว/ที่คาดผม (หลังหัว)
        if (headset) {
            fill(accent);
            path.reset();
            path.moveTo(44f, 26f);
            path.lineTo(40f, 8f);
            path.lineTo(54f, 17f);
            path.close();
            c.drawPath(path, p);
            path.reset();
            path.moveTo(76f, 26f);
            path.lineTo(80f, 8f);
            path.lineTo(66f, 17f);
            path.close();
            c.drawPath(path, p);
            fill(0xFF3B1740);
            path.reset();
            path.moveTo(45f, 23f);
            path.lineTo(43f, 13f);
            path.lineTo(51f, 18f);
            path.close();
            c.drawPath(path, p);
            path.reset();
            path.moveTo(75f, 23f);
            path.lineTo(77f, 13f);
            path.lineTo(69f, 18f);
            path.close();
            c.drawPath(path, p);
        }

        // ใบหน้า
        path.reset();
        path.moveTo(44f, 30f);
        path.cubicTo(44f, 20f, 52f, 16f, 60f, 16f);
        path.cubicTo(68f, 16f, 76f, 20f, 76f, 30f);
        path.cubicTo(76f, 40f, 70f, 49f, 60f, 51f);
        path.cubicTo(50f, 49f, 44f, 40f, 44f, 30f);
        path.close();
        lin(60f, 16f, 60f, 51f, skinL, skinD);
        c.drawPath(path, p);

        // ผมด้านหน้า
        lin(60f, 8f, 60f, 34f, hairA, hairB);
        path.reset();
        path.moveTo(42f, 34f);
        path.cubicTo(38f, 8f, 82f, 8f, 78f, 34f);
        if (xian) {
            path.quadTo(72f, 22f, 60f, 18f);
            path.quadTo(48f, 22f, 42f, 34f);
        } else {
            path.lineTo(74f, 26f);
            path.quadTo(70f, 33f, 64f, 22f);
            path.quadTo(59f, 32f, 54f, 22f);
            path.quadTo(49f, 31f, 46f, 24f);
        }
        path.close();
        c.drawPath(path, p);
        for (int sd = -1; sd <= 1; sd += 2) {
            float x0 = 60f + sd * 16.5f;
            path.reset();
            path.moveTo(x0, 22f);
            path.quadTo(x0 + sd * 5f + sd * sway * 0.5f, 40f, x0 + sd * 3f + sd * sway, 60f);
            path.quadTo(x0 - sd * 2f, 44f, x0 - sd * 3f, 28f);
            path.close();
            lin(x0, 22f, x0, 60f, hairA, hairB);
            c.drawPath(path, p);
        }
        // ไฮไลต์ผม
        line(0x66FFFFFF, 1.4f);
        path.reset();
        path.moveTo(48f, 18f);
        path.quadTo(60f, 11f, 72f, 18f);
        c.drawPath(path, p);

        // ที่คาดผมแมว (headset)
        if (headset) {
            line(accent, 2.2f);
            path.reset();
            path.moveTo(43f, 30f);
            path.quadTo(60f, 5f, 77f, 30f);
            c.drawPath(path, p);
            fill(accent2);
            c.drawCircle(43f, 32f, 3.4f, p);
            c.drawCircle(77f, 32f, 3.4f, p);
        } else if (xian) {
            // มงกุฎทอง หยก ปิ่นปักผม ต่างหู
            fill(accent);
            path.reset();
            path.moveTo(52f, 14f);
            path.lineTo(54f, 6f);
            path.lineTo(57f, 11f);
            path.lineTo(60f, 3f);
            path.lineTo(63f, 11f);
            path.lineTo(66f, 6f);
            path.lineTo(68f, 14f);
            path.close();
            c.drawPath(path, p);
            fill(accent2);
            c.drawCircle(60f, 10f, 2.3f, p);
            fill(0xFFFFFFFF);
            c.drawCircle(59.3f, 9.3f, 0.7f, p);
            line(accent, 1.0f);
            c.drawLine(43.5f, 40f, 43.5f, 47f, p);
            c.drawLine(76.5f, 40f, 76.5f, 47f, p);
            fill(accent2);
            oval(43.5f, 49f, 1.4f, 2.2f);
            c.drawOval(r, p);
            oval(76.5f, 49f, 1.4f, 2.2f);
            c.drawOval(r, p);
        } else {
            // ริบบิ้น + จุดไฟสีฟ้า
            fill(accent);
            c.drawCircle(44f, 24f, 3.2f, p);
            c.drawCircle(76f, 24f, 3.2f, p);
            fill(accent2);
            c.drawCircle(44f, 24f, 1.3f, p);
            c.drawCircle(76f, 24f, 1.3f, p);
        }

        drawFace(c);
    }

    private void eye(Canvas c, float cx, boolean right) {
        float cy = 36f;
        boolean happy = mood == SMILE || mood == LAUGH || mood == HAPPY;
        if (happy || mood == SLEEP || blink > 0) {
            line(ink, 1.9f);
            path.reset();
            if (mood == SLEEP || (blink > 0 && !happy)) {
                path.moveTo(cx - 4.5f, cy);
                path.quadTo(cx, cy + 3f, cx + 4.5f, cy);
            } else {
                path.moveTo(cx - 4.5f, cy + 1.5f);
                path.quadTo(cx, cy - 4f, cx + 4.5f, cy + 1.5f);
            }
            c.drawPath(path, p);
            return;
        }
        float lx = 0f;
        float ly = 0f;
        if (mood == THINK) {
            lx = 1.4f;
            ly = -1.8f;
        }
        fill(0xFFFFFFFF);
        oval(cx, cy, 4.7f, 5.6f);
        c.drawOval(r, p);
        lin(cx, cy - 5f, cx, cy + 5f, eyeB, eyeA);
        oval(cx + lx, cy + 0.6f + ly, 3.7f, 4.6f);
        c.drawOval(r, p);
        fill(0xFF1B1238);
        oval(cx + lx, cy + 0.8f + ly, 1.7f, 2.4f);
        c.drawOval(r, p);
        fill(0xFFFFFFFF);
        c.drawCircle(cx + lx - 1.4f, cy - 1.6f + ly, 1.5f, p);
        c.drawCircle(cx + lx + 1.4f, cy + 2.4f + ly, 0.7f, p);
        // ขนตาบน
        line(ink, 2.1f);
        path.reset();
        path.moveTo(cx - 5.2f, cy - 1.5f);
        path.quadTo(cx, cy - 7.2f, cx + 5.2f, cy - 1.5f);
        c.drawPath(path, p);
        line(ink, 1.2f);
        float ox = right ? 5.2f : -5.2f;
        c.drawLine(cx + ox, cy - 1.5f, cx + ox * 1.25f, cy - 3.2f, p);
        if (mood == SAD) {
            line(ink, 1.3f);
            path.reset();
            path.moveTo(cx - 4.8f, right ? cy - 11f : cy - 8f);
            path.lineTo(cx + 4.8f, right ? cy - 8f : cy - 11f);
            c.drawPath(path, p);
        }
    }

    private void drawFace(Canvas c) {
        eye(c, 52f, false);
        eye(c, 68f, true);
        // บลัช
        fill(0x55FF7A9C);
        oval(47.5f, 42f, 3.6f, 2f);
        c.drawOval(r, p);
        oval(72.5f, 42f, 3.6f, 2f);
        c.drawOval(r, p);
        // จมูก
        line(0x99C98A78, 1f);
        c.drawLine(60f, 41f, 59.4f, 42.4f, p);
        // ปาก
        boolean open = talking && ((tk / 3) % 2 == 0);
        if (mood == LAUGH || open) {
            fill(0xFF7A2E4A);
            path.reset();
            path.moveTo(55.5f, 44.5f);
            path.quadTo(60f, 44f, 64.5f, 44.5f);
            path.quadTo(60f, 52.5f, 55.5f, 44.5f);
            path.close();
            c.drawPath(path, p);
            fill(0xFFFF8FA8);
            oval(60f, 48.4f, 2.4f, 1.3f);
            c.drawOval(r, p);
        } else {
            line(lipCol, 1.5f);
            path.reset();
            if (mood == SAD) {
                path.moveTo(56.5f, 47.5f);
                path.quadTo(60f, 44.5f, 63.5f, 47.5f);
            } else if (mood == SMILE || mood == HAPPY) {
                path.moveTo(55.5f, 44.5f);
                path.quadTo(60f, 49.5f, 64.5f, 44.5f);
            } else {
                path.moveTo(57f, 45.5f);
                path.quadTo(60f, 47.2f, 63f, 45.5f);
            }
            c.drawPath(path, p);
        }
        if (mood == SAD) {
            fill(0xAA7FD3FF);
            oval(72f, 44f + (mt % 20) * 0.35f, 1.3f, 2f);
            c.drawOval(r, p);
        }
        if (mood == HAPPY) {
            star(c, 38f, 24f, 3.5f, accent2);
            star(c, 83f, 30f, 3f, accent);
            star(c, 34f, 50f, 2.2f, accent);
        }
        if (mood == SLEEP) {
            fill(0xFF6B7BC9);
            float zy = 22f - (mt % 40) * 0.25f;
            r.set(80f, zy, 87f, zy + 6f);
            c.drawRoundRect(r, 1.5f, 1.5f, p);
            fill(0xFFFFFFFF);
            r.set(81.5f, zy + 1.5f, 85.5f, zy + 4.5f);
            c.drawRoundRect(r, 1f, 1f, p);
        }
        if (mood == THINK) {
            fill(0xFFFFFFFF);
            float ph = mt * 0.2f;
            for (int i = 0; i < 3; i++) {
                float rr = 1.5f + (float) Math.max(0f, Math.sin(ph - i * 0.9f)) * 1.3f;
                c.drawCircle(78f + i * 6f, 20f - i * 3f, rr, p);
            }
        }
        if (headset && busy) {
            lin(40f, 30f, 80f, 42f, 0x8835E0E8, 0x88F25CB5);
            r.set(43f, 30.5f, 77f, 41.5f);
            c.drawRoundRect(r, 4f, 4f, p);
            line(0xFFFFFFFF, 0.8f);
            c.drawRoundRect(r, 4f, 4f, p);
        }
        if (headset && busy) {
            float a = tk * 0.08f;
            for (int i = 0; i < 3; i++) {
                float ang = a + i * 2.1f;
                float px = 60f + (float) Math.cos(ang) * 30f;
                float py = 30f + (float) Math.sin(ang) * 8f;
                fill(0xAA35E0E8);
                r.set(px - 4f, py - 3f, px + 4f, py + 3f);
                c.drawRoundRect(r, 1f, 1f, p);
            }
        }
    }
}
'''

wr(J + "AnimeGirl.java", ANIME)
print("patch9 สำเร็จ: เพิ่มตัววาดอนิเมะ")
