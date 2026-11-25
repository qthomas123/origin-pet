#!/usr/bin/env python3
# เวอร์ชัน 11: เคลื่อนไหวอิสระและเป็นธรรมชาติ
#  - เดินไปทั่วจอ (ทั้งซ้ายขวาและขึ้นลง) ด้วยการเร่ง/ผ่อนความเร็ว ไม่เดินเป็นเส้นตรงตลอด
#  - หยุดพัก มองรอบ และเลี่ยงไม่ให้สองตัวเดินทับกัน
#  - สไปรต์: ไม่สลับเฟรมกระตุก ใช้เด้งตามจังหวะก้าว เอียงตัว หายใจ เงาพื้น หันหน้าแบบพลิกนุ่ม
#  - ตัวที่อยู่ไกล (สูงบนจอ) เล็กลงเล็กน้อยให้ดูมีมิติ
# รันต่อจาก patch10.py
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
        raise SystemExit("patch11: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


def between(text, a, b):
    i = text.index(a)
    j = text.index(b, i)
    return i, j


ROAM = r'''package com.origin.pet;

import java.util.Random;

class Roam {
    float x = 0f;
    float y = 0f;
    float vx = 0f;
    float vy = 0f;
    float tx = 0f;
    float ty = 0f;
    float maxSp = 2f;
    float speed = 0f;
    int pause = 0;
    int dir = 1;

    void sync(float px, float py) {
        x = px;
        y = py;
        tx = px;
        ty = py;
        vx = 0f;
        vy = 0f;
        speed = 0f;
    }

    private void pick(Random rnd, float minX, float maxX, float minY, float maxY) {
        tx = minX + rnd.nextFloat() * (maxX - minX);
        ty = minY + rnd.nextFloat() * (maxY - minY);
        maxSp = 1.1f + rnd.nextFloat() * 1.5f;
    }

    boolean step(Random rnd, float minX, float maxX, float minY, float maxY,
                 float ox, float oy, float gap) {
        if (pause > 0) {
            pause--;
            vx *= 0.7f;
            vy *= 0.7f;
            speed = 0f;
            return false;
        }
        float dx = tx - x;
        float dy = ty - y;
        float dist = (float) Math.sqrt(dx * dx + dy * dy);
        if (dist < 8f) {
            pause = 40 + rnd.nextInt(120);
            vx = 0f;
            vy = 0f;
            speed = 0f;
            pick(rnd, minX, maxX, minY, maxY);
            return false;
        }
        if (rnd.nextInt(500) == 0) {
            pause = 30 + rnd.nextInt(80);
            return false;
        }
        float sp = Math.min(maxSp, 0.35f + dist * 0.04f);
        float dvx = dx / dist * sp;
        float dvy = dy / dist * sp * 0.55f;
        vx += (dvx - vx) * 0.07f;
        vy += (dvy - vy) * 0.07f;
        float ex = x - ox;
        float ey = y - oy;
        float ed = (float) Math.sqrt(ex * ex + ey * ey);
        if (ed < gap && ed > 1f) {
            vx += ex / ed * 0.18f;
            vy += ey / ed * 0.10f;
        }
        x += vx;
        y += vy;
        if (x < minX) {
            x = minX;
            vx = Math.abs(vx);
            tx = Math.max(tx, minX + 20f);
        }
        if (x > maxX) {
            x = maxX;
            vx = -Math.abs(vx);
            tx = Math.min(tx, maxX - 20f);
        }
        if (y < minY) {
            y = minY;
            vy = Math.abs(vy);
        }
        if (y > maxY) {
            y = maxY;
            vy = -Math.abs(vy);
        }
        speed = (float) Math.sqrt(vx * vx + vy * vy);
        if (Math.abs(vx) > 0.3f) {
            dir = vx > 0f ? 1 : -1;
        }
        return speed > 0.3f;
    }
}
'''
wr(J + "Roam.java", ROAM)

# ---------- AnimeGirl ----------
p = J + "AnimeGirl.java"
t = rd(p)
t = rep(t, "    private Bitmap idleFr = null;\n", '''    private Bitmap idleFr = null;
    private float facing = 1f;
    private float phase = 0f;
    private float spd = 0f;
    private float depth = 1f;
    private float moveBlend = 0f;

    public void setMotion(float speed, float d) {
        spd = speed;
        depth = d;
    }
''')
t = rep(t, "        mt++;\n        tk++;\n", '''        mt++;
        tk++;
        facing += (dir - facing) * 0.28f;
        if (Math.abs(dir - facing) < 0.03f) {
            facing = dir;
        }
        moveBlend += ((walking ? 1f : 0f) - moveBlend) * 0.18f;
        if (walking) {
            phase += Math.max(0.12f, spd * 0.11f);
        }
''')

i, j = between(t, "    private void drawSprite(Canvas c) {", "        // เอฟเฟกต์อารมณ์\n")
NEWSPRITE = '''    private void drawBmp(Canvas c, Bitmap b, float alpha, float lift, float rot, float sy, int w, int h) {
        if (b == null || alpha <= 0.02f) {
            return;
        }
        float sc = Math.min(w / (float) b.getWidth(), (h * 0.97f) / b.getHeight());
        float dw = b.getWidth() * sc;
        float dh = b.getHeight() * sc;
        c.save();
        c.translate(w / 2f, h - 0.02f * h);
        c.scale(facing * depth, depth * sy);
        c.rotate(rot);
        r.set(-dw / 2f, -dh - lift, dw / 2f, -lift);
        p.setShader(null);
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFFFFFFF);
        p.setAlpha((int) (255f * alpha * (mood == SLEEP ? 0.67f : 1f)));
        c.drawBitmap(b, null, r, p);
        p.setAlpha(255);
        c.restore();
    }

    private void drawSprite(Canvas c) {
        int w = getWidth();
        int h = getHeight();
        Bitmap wb = walkFr.length > 2 ? walkFr[2] : walkFr[walkFr.length - 1];
        float mb = moveBlend;
        float step = Math.abs((float) Math.sin(phase));
        float lift = mb * step * 0.04f * h;
        float rot = mb * ((float) Math.sin(phase) * 2.2f + 3.0f * Math.min(1f, spd / 2.4f))
                + (1f - mb) * (float) Math.sin(idle * 0.05f) * 0.8f;
        float sy = 1f + mb * 0.02f * (float) Math.cos(phase * 2f)
                + (1f - mb) * 0.012f * (float) Math.sin(idle * 0.1f);
        if (mood == HAPPY) {
            lift += Math.abs((float) Math.sin(mt * 0.3f)) * 0.08f * h;
        } else if (mood == SAD || mood == SLEEP) {
            lift -= 0.03f * h;
        }
        // เงาพื้น
        float shw = w * 0.30f * depth;
        rad(w / 2f, h * 0.975f, shw, 0x66000000, 0x00000000);
        oval(w / 2f, h * 0.975f, shw, shw * 0.22f);
        c.drawOval(r, p);
        drawBmp(c, idleFr, 1f - mb, lift, rot, sy, w, h);
        drawBmp(c, wb, mb, lift, rot, sy, w, h);
'''
t = t[:i] + NEWSPRITE + t[j:]
wr(p, t)

# ---------- PetService: ลูปเคลื่อนที่ใหม่ ----------
p = J + "PetService.java"
t = rd(p)

i, j = between(t, "    private final Runnable loop = new Runnable() {", "    private int dp(int v) {")
NEWLOOP = '''    private final Roam roamP = new Roam();
    private final Roam roamS = new Roam();

    private final Runnable loop = new Runnable() {
        @Override
        public void run() {
            if (pet != null) {
                boolean walking = false;
                idleCheck();
                int ph = petLp.height > 0 ? petLp.height : petSize;
                float minX = 0f;
                float maxX = screenW - petSize;
                float minY = screenH * 0.28f;
                float maxY = Math.max(minY, screenH - ph - dp(60));
                if (!dragging && chat == null && !sleeping && !pet.still()) {
                    walking = roamP.step(rnd, minX, maxX, minY, maxY,
                            sageLp != null ? sageLp.x : -9999f, sageLp != null ? sageLp.y : -9999f, dp(80));
                    dir = roamP.dir;
                    int nx = Math.round(roamP.x);
                    int ny = Math.round(roamP.y);
                    if (nx != petLp.x || ny != petLp.y) {
                        petLp.x = nx;
                        petLp.y = ny;
                        try {
                            wm.updateViewLayout(pet, petLp);
                        } catch (Exception ignored) {
                        }
                    }
                } else {
                    roamP.sync(petLp.x, petLp.y);
                }
                float depth = 0.8f + 0.2f * Math.max(0f, Math.min(1f, (petLp.y - minY) / Math.max(1f, maxY - minY)));
                pet.setMotion(walking ? roamP.speed : 0f, depth);
                pet.tick(walking, dir);
            }
            ui.postDelayed(this, 33);
        }
    };

'''
t = t[:i] + NEWLOOP + t[j:]

i, j = between(t, "    private final Runnable sageLoop = new Runnable() {", "    private String charName() {")
NEWSAGE = '''    private final Runnable sageLoop = new Runnable() {
        @Override
        public void run() {
            if (sage != null) {
                boolean walking = false;
                float minX = 0f;
                float maxX = screenW - sageW;
                float minY = screenH * 0.28f;
                float maxY = Math.max(minY, screenH - sageH - dp(60));
                if (!sageDragging && chat == null && !sageBusy && !sleeping) {
                    walking = roamS.step(rnd, minX, maxX, minY, maxY,
                            petLp != null ? petLp.x : -9999f, petLp != null ? petLp.y : -9999f, dp(80));
                    sageDir = roamS.dir;
                    int nx = Math.round(roamS.x);
                    int ny = Math.round(roamS.y);
                    if (nx != sageLp.x || ny != sageLp.y) {
                        sageLp.x = nx;
                        sageLp.y = ny;
                        try {
                            wm.updateViewLayout(sage, sageLp);
                        } catch (Exception ignored) {
                        }
                    }
                } else {
                    roamS.sync(sageLp.x, sageLp.y);
                }
                float depth = 0.8f + 0.2f * Math.max(0f, Math.min(1f, (sageLp.y - minY) / Math.max(1f, maxY - minY)));
                sage.setMotion(walking ? roamS.speed : 0f, depth);
                sage.setBusy(sageBusy);
                sage.tick(walking, sageDir);
            }
            ui.postDelayed(this, 33);
        }
    };

'''
t = t[:i] + NEWSAGE + t[j:]
wr(p, t)

# ---------- เวอร์ชัน ----------
p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 11", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "11.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch11: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v11"', t)
if n != 1:
    raise SystemExit("patch11: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch11 สำเร็จ: เคลื่อนไหวอิสระและเป็นธรรมชาติ")
