#!/usr/bin/env python3
# เวอร์ชัน 10: โหมดสไปรต์ PNG โปร่งใส (เฟรมเดินแบบในวิดีโอ) ใช้แทนตัววาด 2D ถ้ามีไฟล์ใน repo  รันต่อจาก patch9b.py
# วางไฟล์ไว้ในโฟลเดอร์ sprites/ ของ repo:
#   irin_idle.png  irin_walk_1.png  irin_walk_2.png ... (ไอริน)
#   arin_idle.png  arin_walk_1.png  arin_walk_2.png ... (อาริน)
# ถ้าไม่มีไฟล์ ระบบใช้ตัววาดอนิเมะเดิมโดยอัตโนมัติ
import os
import re
import shutil

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
        raise SystemExit("patch10: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


# ---------- คัดลอกสไปรต์เข้า assets ----------
assets = ROOT + "/app/src/main/assets"
os.makedirs(assets, exist_ok=True)
copied = 0
if os.path.isdir("sprites"):
    for fn in sorted(os.listdir("sprites")):
        if fn.lower().endswith(".png"):
            shutil.copy(os.path.join("sprites", fn), os.path.join(assets, fn.lower()))
            copied += 1

# ---------- AnimeGirl: เพิ่มโหมดสไปรต์ ----------
p = J + "AnimeGirl.java"
t = rd(p)
t = rep(t, "import android.content.Context;\n",
        "import android.content.Context;\nimport android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;\n")

t = rep(t, "    public AnimeGirl(Context c) {\n        super(c);\n    }\n", '''    public AnimeGirl(Context c) {
        super(c);
    }

    private Bitmap[] walkFr = null;
    private Bitmap idleFr = null;

    protected void loadSprites(Context c, String prefix) {
        try {
            java.util.ArrayList<Bitmap> l = new java.util.ArrayList<Bitmap>();
            for (int i = 1; i <= 24; i++) {
                Bitmap b = loadBmp(c, prefix + "_walk_" + i + ".png");
                if (b == null) {
                    break;
                }
                l.add(b);
            }
            idleFr = loadBmp(c, prefix + "_idle.png");
            if (!l.isEmpty()) {
                walkFr = l.toArray(new Bitmap[0]);
                if (idleFr == null) {
                    idleFr = walkFr[0];
                }
            } else if (idleFr != null) {
                walkFr = new Bitmap[]{idleFr};
            }
        } catch (Throwable ignored) {
            walkFr = null;
        }
    }

    private Bitmap loadBmp(Context c, String name) {
        java.io.InputStream in = null;
        try {
            in = c.getAssets().open(name);
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inJustDecodeBounds = true;
            BitmapFactory.decodeStream(in, null, o);
            in.close();
            int ss = 1;
            while (o.outHeight / ss > 900) {
                ss *= 2;
            }
            in = c.getAssets().open(name);
            BitmapFactory.Options o2 = new BitmapFactory.Options();
            o2.inSampleSize = ss;
            Bitmap b = BitmapFactory.decodeStream(in, null, o2);
            if (b != null && b.getHeight() > 480) {
                int h = 480;
                int w = Math.max(1, b.getWidth() * h / b.getHeight());
                b = Bitmap.createScaledBitmap(b, w, h, true);
            }
            return b;
        } catch (Throwable e) {
            return null;
        } finally {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (Exception ignored) {
            }
        }
    }

    private void drawSprite(Canvas c) {
        int w = getWidth();
        int h = getHeight();
        Bitmap b = (walking && walkFr.length > 1) ? walkFr[((int) (t * 0.25f)) % walkFr.length] : idleFr;
        if (b == null) {
            return;
        }
        float bob = walking ? Math.abs((float) Math.sin(t * 0.5f)) * -0.012f * h
                : (float) Math.sin(idle * 0.12f) * 0.006f * h;
        if (mood == HAPPY) {
            bob -= Math.abs((float) Math.sin(mt * 0.3f)) * 0.08f * h;
        } else if (mood == SAD || mood == SLEEP) {
            bob += 0.03f * h;
        }
        float sc = Math.min(w / (float) b.getWidth(), (h * 0.97f) / b.getHeight());
        float dw = b.getWidth() * sc;
        float dh = b.getHeight() * sc;
        float left = (w - dw) / 2f;
        float top = h - dh - 0.01f * h + bob;
        c.save();
        if (dir < 0) {
            c.scale(-1f, 1f, w / 2f, h / 2f);
        }
        r.set(left, top, left + dw, top + dh);
        p.setShader(null);
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFFFFFFF);
        p.setAlpha(mood == SLEEP ? 170 : 255);
        c.drawBitmap(b, null, r, p);
        p.setAlpha(255);
        c.restore();
        // เอฟเฟกต์อารมณ์
        float s = w / 120f;
        c.save();
        c.scale(s, s);
        if (mood == HAPPY) {
            star(c, 22f, 26f, 4f, accent2);
            star(c, 98f, 34f, 3.4f, accent);
            star(c, 30f, 56f, 2.6f, accent);
        } else if (mood == SLEEP) {
            fill(0xFF6B7BC9);
            float zy = 20f - (mt % 40) * 0.25f;
            r.set(84f, zy, 92f, zy + 7f);
            c.drawRoundRect(r, 1.5f, 1.5f, p);
        } else if (mood == THINK) {
            fill(0xFFFFFFFF);
            float ph = mt * 0.2f;
            for (int i = 0; i < 3; i++) {
                float rr = 1.6f + (float) Math.max(0f, Math.sin(ph - i * 0.9f)) * 1.4f;
                c.drawCircle(84f + i * 6f, 18f - i * 3f, rr, p);
            }
        } else if (mood == CAST) {
            rad(92f, 50f, 14f, 0xAAFFFFFF, 0x00FFFFFF);
            oval(92f, 50f, 14f, 14f);
            c.drawOval(r, p);
            star(c, 92f, 50f, 7f, accent2);
        } else if (mood == SAD) {
            fill(0xAA7FD3FF);
            oval(70f, 32f + (mt % 20) * 0.5f, 1.4f, 2.2f);
            c.drawOval(r, p);
        }
        c.restore();
    }
''')

t = rep(t, "    protected void onDraw(Canvas c) {\n        float s = getWidth() / 120f;",
        "    protected void onDraw(Canvas c) {\n        if (walkFr != null) {\n            drawSprite(c);\n            return;\n        }\n        float s = getWidth() / 120f;")
wr(p, t)

# ---------- PetView / SageView: โหลดสไปรต์ ----------
p = J + "PetView.java"
t = rd(p)
t = rep(t, "        tailCol = 0xFF2B1B4D;\n    }", '        tailCol = 0xFF2B1B4D;\n        loadSprites(c, "irin");\n    }')
wr(p, t)
p = J + "SageView.java"
t = rd(p)
t = rep(t, "        tailCol = 0xFF1B2A63;\n    }", '        tailCol = 0xFF1B2A63;\n        loadSprites(c, "arin");\n    }')
wr(p, t)

# ---------- เวอร์ชัน ----------
p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 10", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "10.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch10: แก้เวอร์ชันไม่ได้")
wr(p, t)
p = J + "MainActivity.java"
t = rd(p)
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v10"', t)
if n != 1:
    raise SystemExit("patch10: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch10 สำเร็จ: คัดลอกสไปรต์ %d ไฟล์ (0 = ใช้ตัววาดอนิเมะเดิม)" % copied)
