#!/usr/bin/env python3
# เวอร์ชัน 3: ท่าทางอารมณ์ สกิลพิเศษ และการรับรู้หน้าจอ  (รันต่อจาก generate.py)
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
        raise SystemExit("patch3: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


# ---------- gradle / manifest / res ----------
p = ROOT + "/app/build.gradle"
t = rd(p)
t = rep(t, 'versionCode 2', 'versionCode 3')
t = rep(t, 'versionName "2.0"', 'versionName "3.0"')
wr(p, t)

p = ROOT + "/app/src/main/AndroidManifest.xml"
t = rd(p)
t = rep(t, "<queries>", '''<queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>''')
t = rep(t, '<uses-permission android:name="android.permission.RECORD_AUDIO" />',
        '<uses-permission android:name="android.permission.RECORD_AUDIO" />\n'
        '    <uses-permission android:name="android.permission.USE_BIOMETRIC" />')
t = rep(t, "    </application>", r'''        <activity
            android:name=".AuthActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <service
            android:name=".PetAccess"
            android:exported="true"
            android:label="Origin Pet รับรู้หน้าจอ"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/access_config" />
        </service>
    </application>''')
wr(p, t)

wr(ROOT + "/app/src/main/res/values/strings.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="access_desc">ให้ไอรินรู้ว่า Q เปิดแอปอะไรและอ่านข้อความบนหน้าจอ เพื่อคุยและให้ความคิดเสริม ข้อความจะถูกส่งให้ Gemini เฉพาะตอนที่เปิดการรับรู้ไว้ ช่องรหัสผ่านและแอปธนาคารจะไม่ถูกอ่าน</string>
</resources>
''')

wr(ROOT + "/app/src/main/res/xml/access_config.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:description="@string/access_desc"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagIncludeNotImportantViews"
    android:canRetrieveWindowContent="true"
    android:notificationTimeout="500" />
''')

# ---------- PetAccess ----------
wr(J + "PetAccess.java", r'''package com.origin.pet;

import android.accessibilityservice.AccessibilityService;
import android.os.Bundle;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.List;

public class PetAccess extends AccessibilityService {

    static PetAccess inst = null;
    static final java.util.concurrent.ConcurrentHashMap<String, Long> grants =
            new java.util.concurrent.ConcurrentHashMap<String, Long>();
    static volatile boolean connected = false;
    static volatile String pkg = "";
    static volatile String screen = "";
    static volatile long stamp = 0;

    private long last = 0;

    private static final String[] BLOCK = {
            "bank", "kbank", "scb", "ktb", "bbl", "krungsri", "krungthai", "ttb", "gsb", "baac",
            "paotang", "truemoney", "wallet", "authenticator", "keepass", "lastpass", "1password",
            "bitwarden", "bitkub", "binance", "okx", "spay", "payment", "settings"
    };

    static boolean blocked(String p) {
        Long g = grants.get(p);
        if (g != null && g > System.currentTimeMillis()) {
            return false;
        }
        String l = p.toLowerCase();
        for (String b : BLOCK) {
            if (l.contains(b)) {
                return true;
            }
        }
        return false;
    }

    private static AccessibilityNodeInfo findNode(AccessibilityNodeInfo n, int mode, int depth) {
        if (n == null || depth > 25) {
            return null;
        }
        if (mode == 0 && n.isEditable() && !n.isPassword()) {
            return n;
        }
        if (mode == 1 && n.isScrollable()) {
            return n;
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            AccessibilityNodeInfo r = findNode(n.getChild(i), mode, depth + 1);
            if (r != null) {
                return r;
            }
        }
        return null;
    }

    static boolean doClick(String text) {
        PetAccess s = inst;
        if (s == null) {
            return false;
        }
        AccessibilityNodeInfo root = s.getRootInActiveWindow();
        if (root == null) {
            return false;
        }
        List<AccessibilityNodeInfo> l = root.findAccessibilityNodeInfosByText(text);
        if (l == null) {
            return false;
        }
        for (AccessibilityNodeInfo n : l) {
            if (n.isPassword()) {
                continue;
            }
            AccessibilityNodeInfo x = n;
            int up = 0;
            while (x != null && !x.isClickable() && up < 6) {
                x = x.getParent();
                up++;
            }
            if (x != null && x.isClickable() && x.performAction(AccessibilityNodeInfo.ACTION_CLICK)) {
                return true;
            }
        }
        return false;
    }

    static boolean doType(String text) {
        PetAccess s = inst;
        if (s == null) {
            return false;
        }
        AccessibilityNodeInfo root = s.getRootInActiveWindow();
        if (root == null) {
            return false;
        }
        AccessibilityNodeInfo f = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
        if (f == null || !f.isEditable()) {
            f = findNode(root, 0, 0);
        }
        if (f == null || f.isPassword()) {
            return false;
        }
        f.performAction(AccessibilityNodeInfo.ACTION_FOCUS);
        Bundle b = new Bundle();
        b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text);
        return f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
    }

    static boolean doScroll(boolean down) {
        PetAccess s = inst;
        if (s == null) {
            return false;
        }
        AccessibilityNodeInfo root = s.getRootInActiveWindow();
        AccessibilityNodeInfo n = findNode(root, 1, 0);
        if (n == null) {
            return false;
        }
        return n.performAction(down ? AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
                : AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD);
    }

    static boolean doGlobal(boolean back) {
        PetAccess s = inst;
        if (s == null) {
            return false;
        }
        return s.performGlobalAction(back ? GLOBAL_ACTION_BACK : GLOBAL_ACTION_HOME);
    }

    static String snapshot() {
        if (!connected || pkg.isEmpty()) {
            return "";
        }
        return "แอปที่เปิดอยู่: " + pkg + "\nข้อความบนหน้าจอ: " + screen;
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        inst = this;
        connected = true;
    }

    @Override
    public boolean onUnbind(android.content.Intent intent) {
        connected = false;
        inst = null;
        return super.onUnbind(intent);
    }

    @Override
    public void onInterrupt() {
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent e) {
        if (e == null || e.getPackageName() == null) {
            return;
        }
        String p = e.getPackageName().toString();
        if (p.equals(getPackageName()) || p.equals("com.android.systemui")
                || p.contains("inputmethod") || p.contains("keyboard")) {
            return;
        }
        long now = System.currentTimeMillis();
        boolean changed = !p.equals(pkg);
        if (!changed && now - last < 2500) {
            return;
        }
        last = now;
        if (blocked(p)) {
            pkg = p;
            screen = "(แอปนี้ถูกกันไว้ ไอรินไม่ดูเนื้อหา)";
            stamp = now;
            return;
        }
        try {
            AccessibilityNodeInfo root = getRootInActiveWindow();
            if (root == null) {
                return;
            }
            CharSequence rp = root.getPackageName();
            if (rp == null || rp.toString().equals(getPackageName())) {
                return;
            }
            StringBuilder sb = new StringBuilder();
            collect(root, sb, 0);
            pkg = rp.toString();
            screen = sb.toString();
            stamp = now;
        } catch (Exception ignored) {
        }
    }

    private void collect(AccessibilityNodeInfo n, StringBuilder sb, int depth) {
        if (n == null || sb.length() > 1800 || depth > 25) {
            return;
        }
        if (n.isPassword()) {
            return;
        }
        if (n.isVisibleToUser()) {
            CharSequence t = n.getText();
            if (t == null || t.length() == 0) {
                t = n.getContentDescription();
            }
            if (t != null && t.length() > 0) {
                String s = t.toString().replace('\n', ' ').trim();
                if (s.length() > 200) {
                    s = s.substring(0, 200);
                }
                if (!s.isEmpty() && !s.matches("[0-9 ]{4,8}")) {
                    sb.append(s).append(" | ");
                }
            }
        }
        int c = n.getChildCount();
        for (int i = 0; i < c; i++) {
            AccessibilityNodeInfo ch = n.getChild(i);
            if (ch != null) {
                collect(ch, sb, depth + 1);
            }
        }
    }
}
''')

# ---------- AuthActivity (สแกนนิ้ว) ----------
wr(J + "AuthActivity.java", r'''package com.origin.pet;

import android.app.Activity;
import android.content.DialogInterface;
import android.hardware.biometrics.BiometricPrompt;
import android.os.Build;
import android.os.Bundle;
import android.os.CancellationSignal;

public class AuthActivity extends Activity {

    private boolean done = false;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        if (Build.VERSION.SDK_INT < 28) {
            finishWith(false);
            return;
        }
        String label = getIntent().getStringExtra("label");
        if (label == null) {
            label = "";
        }
        try {
            BiometricPrompt bp = new BiometricPrompt.Builder(this)
                    .setTitle("ไอรินขออนุญาตใช้แอป")
                    .setSubtitle(label)
                    .setDescription("สแกนนิ้วเพื่ออนุญาตให้ไอรินดูและควบคุมแอปนี้ 5 นาที")
                    .setNegativeButton("ไม่อนุญาต", getMainExecutor(), new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface d, int w) {
                            finishWith(false);
                        }
                    })
                    .build();
            bp.authenticate(new CancellationSignal(), getMainExecutor(),
                    new BiometricPrompt.AuthenticationCallback() {
                        @Override
                        public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult r) {
                            finishWith(true);
                        }

                        @Override
                        public void onAuthenticationError(int code, CharSequence msg) {
                            finishWith(false);
                        }
                    });
        } catch (Exception e) {
            finishWith(false);
        }
    }

    private void finishWith(boolean ok) {
        if (done) {
            return;
        }
        done = true;
        PetService.deliverAuth(ok);
        finish();
    }

    @Override
    protected void onDestroy() {
        if (!done) {
            done = true;
            PetService.deliverAuth(false);
        }
        super.onDestroy();
    }
}
''')

# ---------- MemStore (ที่เก็บความจำถาวรบนเมมการ์ด/โฟลเดอร์ที่เลือก) ----------
wr(J + "MemStore.java", r'''package com.origin.pet;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.DocumentsContract;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

public class MemStore {

    private static Uri tree(Context c) {
        String s = c.getSharedPreferences("pet", Context.MODE_PRIVATE).getString("memtree", "");
        return s.isEmpty() ? null : Uri.parse(s);
    }

    private static Uri find(Context c, Uri tree, String name) {
        try {
            String id = DocumentsContract.getTreeDocumentId(tree);
            Uri kids = DocumentsContract.buildChildDocumentsUriUsingTree(tree, id);
            Cursor cur = c.getContentResolver().query(kids,
                    new String[]{DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                            DocumentsContract.Document.COLUMN_DISPLAY_NAME}, null, null, null);
            if (cur == null) {
                return null;
            }
            try {
                while (cur.moveToNext()) {
                    if (name.equals(cur.getString(1))) {
                        return DocumentsContract.buildDocumentUriUsingTree(tree, cur.getString(0));
                    }
                }
            } finally {
                cur.close();
            }
        } catch (Exception ignored) {
        }
        return null;
    }

    static String read(Context c, String name) {
        Uri t = tree(c);
        if (t == null) {
            return null;
        }
        Uri f = find(c, t, name);
        if (f == null) {
            return null;
        }
        try {
            InputStream in = c.getContentResolver().openInputStream(f);
            if (in == null) {
                return null;
            }
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0) {
                bos.write(buf, 0, n);
            }
            in.close();
            return bos.toString("UTF-8");
        } catch (Exception e) {
            return null;
        }
    }

    static boolean write(Context c, String name, String text) {
        Uri t = tree(c);
        if (t == null) {
            return false;
        }
        try {
            Uri f = find(c, t, name);
            if (f == null) {
                String id = DocumentsContract.getTreeDocumentId(t);
                Uri dir = DocumentsContract.buildDocumentUriUsingTree(t, id);
                f = DocumentsContract.createDocument(c.getContentResolver(), dir, "text/plain", name);
            }
            if (f == null) {
                return false;
            }
            OutputStream os = c.getContentResolver().openOutputStream(f, "wt");
            if (os == null) {
                return false;
            }
            os.write(text.getBytes("UTF-8"));
            os.close();
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    static void clearAll(Context c) {
        write(c, "q_profile.txt", "");
        write(c, "important.txt", "");
        write(c, "history.txt", "[]");
    }
}
''')

# ---------- FxView (เอฟเฟกต์สกิล) ----------
wr(J + "FxView.java", r'''package com.origin.pet;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.view.View;

public class FxView extends View {

    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private int kind = 0;
    private int dir = 1;
    private int t = 0;
    private float cx = 0f;
    private float cy = 0f;
    private Runnable end;
    private boolean running = false;

    public FxView(Context c) {
        super(c);
    }

    public void play(int k, float x, float y, int d, Runnable onEnd) {
        kind = k;
        cx = x;
        cy = y;
        dir = d;
        end = onEnd;
        t = 0;
        running = true;
        invalidate();
    }

    private void glow(Canvas c, float x, float y, float r, int core, int mid) {
        p.setStyle(Paint.Style.FILL);
        p.setShader(new RadialGradient(x, y, r,
                new int[]{core, mid, 0x008E5CF0}, new float[]{0f, 0.45f, 1f}, Shader.TileMode.CLAMP));
        c.drawCircle(x, y, r, p);
        p.setShader(null);
    }

    private void star(Canvas c, float x, float y, float r, int color) {
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeCap(Paint.Cap.ROUND);
        p.setStrokeWidth(r * 0.35f);
        p.setColor(color);
        c.drawLine(x - r, y, x + r, y, p);
        c.drawLine(x, y - r, x, y + r, p);
        c.drawLine(x - r * 0.6f, y - r * 0.6f, x + r * 0.6f, y + r * 0.6f, p);
        c.drawLine(x - r * 0.6f, y + r * 0.6f, x + r * 0.6f, y - r * 0.6f, p);
    }

    @Override
    protected void onDraw(Canvas c) {
        if (!running) {
            return;
        }
        float d = getResources().getDisplayMetrics().density;
        int w = getWidth();
        t++;
        boolean over = false;
        if (kind == 0) {
            float r = 26f * d;
            float x = cx + dir * (40f * d + t * (w / 40f));
            for (int i = 5; i >= 0; i--) {
                float xi = x - dir * i * r * 0.7f;
                float ri = r * (1f - i * 0.13f);
                int a = 255 - i * 38;
                glow(c, xi, cy, ri, (a << 24) | 0xFFFFFF, (a << 24) | 0xF25CB5);
            }
            if (x < -r * 2 || x > w + r * 2) {
                over = true;
            }
        } else if (kind == 1) {
            float rad = (18f + t * 1.7f) * d;
            int a = Math.max(0, 255 - t * 4);
            p.setStyle(Paint.Style.STROKE);
            p.setStrokeWidth(3f * d);
            p.setColor((a << 24) | 0x35E0E8);
            c.drawCircle(cx, cy, rad, p);
            p.setColor((a << 24) | 0x8E5CF0);
            c.drawCircle(cx, cy, rad * 0.7f, p);
            p.setStyle(Paint.Style.FILL);
            p.setColor((a << 24) | 0xF25CB5);
            for (int i = 0; i < 8; i++) {
                double ang = t * 0.12 + i * Math.PI / 4;
                c.drawCircle(cx + (float) Math.cos(ang) * rad, cy + (float) Math.sin(ang) * rad, 3.5f * d, p);
            }
            if (t > 62) {
                over = true;
            }
        } else {
            int a = Math.max(0, 255 - t * 4);
            int[] cols = {0xFFE066, 0xF25CB5, 0x35E0E8};
            for (int i = 0; i < 12; i++) {
                double ang = i * 0.52 + t * 0.02;
                float dist = t * 2.2f * d * (0.5f + (i % 3) * 0.3f);
                star(c, cx + (float) Math.cos(ang) * dist, cy + (float) Math.sin(ang) * dist,
                        (4f + (i % 3) * 2f) * d, (a << 24) | cols[i % 3]);
            }
            if (t > 62) {
                over = true;
            }
        }
        if (over) {
            running = false;
            if (end != null) {
                post(end);
            }
        } else {
            postInvalidateOnAnimation();
        }
    }
}
''')

# ---------- PetView (เขียนใหม่ทั้งไฟล์: เพิ่มอารมณ์) ----------
wr(J + "PetView.java", r'''package com.origin.pet;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.view.View;

public class PetView extends View {

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

    private boolean walking = true;
    private boolean talking = false;
    private int dir = 1;
    private float t = 0f;
    private float idle = 0f;
    private int blink = 0;
    private int mood = NONE;
    private int moodTicks = 0;
    private int mt = 0;

    static final int SKIN = 0xFFFFE4D2;
    static final int HAIR = 0xFF8E5CF0;
    static final int HAIR_TIP = 0xFFF25CB5;
    static final int DOT = 0xFF35E0E8;
    static final int OUTFIT = 0xFFF6F4FF;
    static final int OUTFIT2 = 0xFF3A2F7A;
    static final int TAIL = 0xFF5B3FB8;
    static final int INK = 0xFF3A2F7A;
    static final int LIP = 0xFF8A3A5C;

    public PetView(Context c) {
        super(c);
    }

    public void setTalking(boolean b) {
        talking = b;
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
        p.setStyle(Paint.Style.FILL);
        p.setColor(color);
    }

    private void stroke(int color, float w) {
        p.setStyle(Paint.Style.STROKE);
        p.setColor(color);
        p.setStrokeWidth(w);
        p.setStrokeCap(Paint.Cap.ROUND);
    }

    private void dot(Canvas c, float x, float y, float rad) {
        fill(DOT);
        c.drawCircle(x, y, rad, p);
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
        float wag = (float) Math.sin((walking ? t * 0.3f : idle * 0.15f)) * 9f;
        float hairSway = (float) Math.sin(t * 0.25f + 1f) * (walking ? 4f : 0.8f);

        if (mood == HAPPY) {
            bob -= Math.abs((float) Math.sin(mt * 0.3f)) * 16f;
            wag = (float) Math.sin(mt * 0.9f) * 14f;
        } else if (mood == SAD) {
            bob += 5f;
            wag = 2f;
        } else if (mood == SLEEP) {
            bob += 6f + (float) Math.sin(mt * 0.08f) * 1.5f;
            wag = 0f;
        }
        if (mood == LAUGH) {
            c.translate((float) Math.sin(mt * 1.1f) * 2f, 0f);
        }
        if (mood == SLEEP) {
            c.rotate(7f, 60f, 130f);
        }

        path.reset();
        path.moveTo(48f, 98f + bob);
        path.quadTo(20f, 100f + wag, 10f, 72f + wag);
        stroke(TAIL, 7f);
        c.drawPath(path, p);
        path.reset();
        path.moveTo(5f, 76f + wag);
        path.lineTo(14f, 62f + wag);
        path.lineTo(16f, 78f + wag);
        path.close();
        fill(HAIR_TIP);
        c.drawPath(path, p);
        dot(c, 30f, 94f + wag * 0.4f, 1.8f);
        dot(c, 20f, 86f + wag * 0.7f, 1.8f);

        r.set(28f + hairSway * 0.3f, 14f + bob, 92f + hairSway * 0.3f, 112f + bob);
        fill(HAIR);
        c.drawOval(r, p);
        r.set(32f + hairSway, 90f + bob, 88f + hairSway, 126f + bob);
        fill(HAIR_TIP);
        c.drawOval(r, p);

        stroke(SKIN, 9f);
        float legA = swing * 10f;
        c.drawLine(52f, 102f + bob, 52f + legA, 128f, p);
        c.drawLine(68f, 102f + bob, 68f - legA, 128f, p);
        fill(OUTFIT2);
        r.set(46f + legA, 124f, 62f + legA, 134f);
        c.drawOval(r, p);
        r.set(62f - legA, 124f, 78f - legA, 134f);
        c.drawOval(r, p);

        fill(OUTFIT2);
        r.set(44f, 92f + bob, 76f, 108f + bob);
        c.drawRoundRect(r, 6f, 6f, p);

        stroke(SKIN, 7f);
        float armA = swing * 9f;
        if (mood == CAST) {
            c.drawLine(44f, 76f + bob, 98f, 66f + bob, p);
            c.drawLine(76f, 76f + bob, 98f, 66f + bob, p);
            float gr = 5f + (mt % 12);
            fill(0xCCF25CB5);
            c.drawCircle(102f, 66f + bob, gr, p);
            fill(0xFFFFFFFF);
            c.drawCircle(102f, 66f + bob, gr * 0.5f, p);
        } else if (mood == HAPPY) {
            c.drawLine(44f, 76f + bob, 32f, 50f + bob, p);
            c.drawLine(76f, 76f + bob, 88f, 50f + bob, p);
        } else {
            c.drawLine(44f, 76f + bob, 38f - armA, 98f + bob, p);
            c.drawLine(76f, 76f + bob, 82f + armA, 98f + bob, p);
        }

        fill(OUTFIT);
        r.set(42f, 66f + bob, 78f, 98f + bob);
        c.drawRoundRect(r, 9f, 9f, p);
        fill(HAIR_TIP);
        r.set(42f, 88f + bob, 78f, 93f + bob);
        c.drawRect(r, p);
        dot(c, 50f, 76f + bob, 1.6f);
        dot(c, 58f, 82f + bob, 1.6f);
        dot(c, 66f, 75f + bob, 1.6f);
        dot(c, 70f, 84f + bob, 1.6f);

        fill(SKIN);
        c.drawCircle(60f, 42f + bob, 26f, p);

        path.reset();
        path.moveTo(33f, 42f + bob);
        path.quadTo(60f, 0f + bob, 87f, 42f + bob);
        path.quadTo(80f, 28f + bob, 68f, 32f + bob);
        path.quadTo(60f, 20f + bob, 52f, 32f + bob);
        path.quadTo(40f, 28f + bob, 33f, 42f + bob);
        path.close();
        fill(HAIR);
        c.drawPath(path, p);
        fill(HAIR_TIP);
        c.drawCircle(80f, 26f + bob, 3f, p);

        boolean happyEyes = mood == SMILE || mood == LAUGH || mood == HAPPY;
        if (happyEyes) {
            stroke(INK, 2.6f);
            path.reset();
            path.moveTo(44f, 50f + bob);
            path.quadTo(49f, 41f + bob, 54f, 50f + bob);
            c.drawPath(path, p);
            path.reset();
            path.moveTo(66f, 50f + bob);
            path.quadTo(71f, 41f + bob, 76f, 50f + bob);
            c.drawPath(path, p);
        } else if (blink > 0 || mood == SLEEP) {
            stroke(INK, 2f);
            c.drawLine(44f, 46f + bob, 54f, 46f + bob, p);
            c.drawLine(66f, 46f + bob, 76f, 46f + bob, p);
        } else {
            float py = mood == THINK ? -3f : 0f;
            fill(0xFFFFFFFF);
            r.set(43f, 38f + bob, 55f, 54f + bob);
            c.drawOval(r, p);
            r.set(65f, 38f + bob, 77f, 54f + bob);
            c.drawOval(r, p);
            fill(0xFF4A5CF0);
            r.set(46f, 41f + bob + py, 54f, 53f + bob + py);
            c.drawOval(r, p);
            r.set(66f, 41f + bob + py, 74f, 53f + bob + py);
            c.drawOval(r, p);
            fill(0xFF1B1448);
            c.drawCircle(50f, 47f + bob + py, 2.8f, p);
            c.drawCircle(70f, 47f + bob + py, 2.8f, p);
            fill(0xFFFFFFFF);
            c.drawCircle(48.5f, 44f + bob + py, 1.6f, p);
            c.drawCircle(68.5f, 44f + bob + py, 1.6f, p);
        }
        if (mood == SAD) {
            stroke(INK, 2f);
            c.drawLine(43f, 36f + bob, 54f, 32f + bob, p);
            c.drawLine(66f, 32f + bob, 77f, 36f + bob, p);
            fill(0xFF7FD8FF);
            c.drawCircle(46f, 57f + bob + (mt % 20) * 0.5f, 2f, p);
        }

        fill(0x66FF7FA8);
        c.drawCircle(44f, 56f + bob, 3.5f, p);
        c.drawCircle(76f, 56f + bob, 3.5f, p);
        dot(c, 41f, 52f + bob, 1.3f);
        dot(c, 44f, 49f + bob, 1.3f);
        dot(c, 79f, 52f + bob, 1.3f);
        dot(c, 76f, 49f + bob, 1.3f);
        dot(c, 60f, 30f + bob, 1.5f);

        if (mood == LAUGH) {
            fill(LIP);
            float h = (mt % 8 < 4) ? 14f : 10f;
            r.set(51f, 56f + bob, 69f, 56f + h + bob);
            c.drawOval(r, p);
            fill(0xFFFF8FB0);
            r.set(55f, 56f + h - 5f + bob, 65f, 56f + h + bob);
            c.drawOval(r, p);
        } else if (mood == SMILE || mood == HAPPY) {
            stroke(LIP, 2.2f);
            path.reset();
            path.moveTo(52f, 59f + bob);
            path.quadTo(60f, 70f + bob, 68f, 59f + bob);
            c.drawPath(path, p);
        } else if (mood == SAD) {
            stroke(LIP, 2f);
            path.reset();
            path.moveTo(54f, 65f + bob);
            path.quadTo(60f, 58f + bob, 66f, 65f + bob);
            c.drawPath(path, p);
        } else if (mood == SLEEP) {
            fill(LIP);
            r.set(57f, 60f + bob, 63f, 66f + bob);
            c.drawOval(r, p);
        } else if (mood == CAST) {
            fill(LIP);
            r.set(56f, 58f + bob, 64f, 66f + bob);
            c.drawOval(r, p);
        } else if (talking && (((int) (t + idle)) / 5) % 2 == 0) {
            fill(LIP);
            r.set(55f, 57f + bob, 65f, 66f + bob);
            c.drawOval(r, p);
        } else {
            stroke(LIP, 1.8f);
            path.reset();
            path.moveTo(55f, 60f + bob);
            path.quadTo(60f, 65f + bob, 65f, 60f + bob);
            c.drawPath(path, p);
        }

        c.restore();

        c.save();
        c.scale(s, s);
        if (mood == SLEEP) {
            p.setTextSize(16f);
            for (int k = 0; k < 3; k++) {
                float ph = ((mt * 0.6f) + k * 20f) % 60f;
                fill(HAIR);
                p.setAlpha(Math.max(0, 255 - (int) (ph * 4f)));
                c.drawText("Z", 80f + ph * 0.3f, 40f - ph * 0.6f, p);
            }
            p.setAlpha(255);
        }
        if (mood == THINK) {
            fill(HAIR);
            for (int k = 0; k < 3; k++) {
                if ((mt / 10) % 4 > k) {
                    c.drawCircle(88f + k * 8f, 20f - k * 6f, 2f + k, p);
                }
            }
        }
        if (mood == HAPPY || mood == LAUGH) {
            stroke(0xFFFFC94D, 2f);
            float f = (mt / 4) % 3;
            c.drawLine(22f, 20f + f, 22f, 28f + f, p);
            c.drawLine(18f + f, 24f, 26f + f, 24f, p);
            c.drawLine(98f, 14f - f, 98f, 22f - f, p);
            c.drawLine(94f - f, 18f, 102f - f, 18f, p);
        }
        c.restore();
    }
}
''')

# ---------- MainActivity ----------
p = J + "MainActivity.java"
t = rd(p)
t = rep(t, '"Origin Pet v2"', '"Origin Pet v3"')
t = rep(t, 'addButton(root, "3) เรียกไอรินออกมา", new View.OnClickListener() {',
        r'''addButton(root, "เลือกที่เก็บความจำถาวร (เมมการ์ด/โฟลเดอร์)", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this,
                        "สร้างโฟลเดอร์ใหม่ (เช่น IrinMemory) บนเมมการ์ดแล้วกด ใช้โฟลเดอร์นี้",
                        Toast.LENGTH_LONG).show();
                Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
                i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION
                        | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                        | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
                startActivityForResult(i, 77);
            }
        });

        addButton(root, "เลือกแอปที่ไอรินใช้ได้เลย", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pickApps("app_ok", "แอปที่ไอรินใช้ได้เลย");
            }
        });

        addButton(root, "เลือกแอปที่ต้องสแกนนิ้วก่อน", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pickApps("app_fp", "แอปที่ต้องสแกนนิ้วก่อนใช้");
            }
        });

        addButton(root, "3) เปิดให้ไอรินรับรู้หน้าจอ (ไม่บังคับ)", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this,
                        "ถ้าสวิตช์เทา: ตั้งค่า > แอป > Origin Pet > จุดสามจุดมุมขวา > อนุญาตการตั้งค่าที่จำกัด แล้วกลับมาเปิดใหม่",
                        Toast.LENGTH_LONG).show();
                startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
            }
        });

        addButton(root, "4) เรียกไอรินออกมา", new View.OnClickListener() {''')
t = rep(t, "import android.app.Activity;",
        "import android.app.Activity;\nimport android.app.AlertDialog;\nimport android.content.DialogInterface;\n"
        "import android.content.pm.ResolveInfo;")
t = rep(t, "import java.util.ArrayList;",
        "import java.util.ArrayList;\nimport java.util.Collections;\nimport java.util.Comparator;\n"
        "import java.util.HashSet;\nimport java.util.List;\nimport java.util.Set;")
t = rep(t, ".remove(\"memory\").remove(\"notes\").apply();",
        ".remove(\"memory\").remove(\"notes\").remove(\"important\").apply();\n"
        "                new Thread(new Runnable() {\n"
        "                    @Override\n"
        "                    public void run() {\n"
        "                        MemStore.clearAll(MainActivity.this);\n"
        "                    }\n"
        "                }).start();")
t = rep(t, "    private void askPermissions() {", r'''    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == 77 && res == RESULT_OK && data != null && data.getData() != null) {
            Uri u = data.getData();
            try {
                getContentResolver().takePersistableUriPermission(u,
                        Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            } catch (Exception ignored) {
            }
            getSharedPreferences("pet", MODE_PRIVATE).edit().putString("memtree", u.toString()).apply();
            Toast.makeText(this, "ตั้งที่เก็บความจำถาวรแล้ว ไอรินจะบันทึกลงโฟลเดอร์นี้", Toast.LENGTH_LONG).show();
        }
    }

    private void pickApps(final String key, String title) {
        PackageManager pm = getPackageManager();
        Intent q = new Intent(Intent.ACTION_MAIN);
        q.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> list = pm.queryIntentActivities(q, 0);
        final ArrayList<String[]> items = new ArrayList<String[]>();
        for (ResolveInfo ri : list) {
            String pk = ri.activityInfo.packageName;
            if (pk.equals(getPackageName())) {
                continue;
            }
            items.add(new String[]{String.valueOf(ri.loadLabel(pm)), pk});
        }
        Collections.sort(items, new Comparator<String[]>() {
            @Override
            public int compare(String[] a, String[] b) {
                return a[0].compareToIgnoreCase(b[0]);
            }
        });
        Set<String> cur = getSharedPreferences("pet", MODE_PRIVATE).getStringSet(key, new HashSet<String>());
        String[] labels = new String[items.size()];
        final boolean[] chk = new boolean[items.size()];
        for (int i = 0; i < items.size(); i++) {
            labels[i] = items.get(i)[0];
            chk[i] = cur.contains(items.get(i)[1]);
        }
        new AlertDialog.Builder(this)
                .setTitle(title)
                .setMultiChoiceItems(labels, chk, new DialogInterface.OnMultiChoiceClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which, boolean checked) {
                        chk[which] = checked;
                    }
                })
                .setPositiveButton("บันทึก", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int w) {
                        HashSet<String> out = new HashSet<String>();
                        for (int i = 0; i < chk.length; i++) {
                            if (chk[i]) {
                                out.add(items.get(i)[1]);
                            }
                        }
                        getSharedPreferences("pet", MODE_PRIVATE).edit().putStringSet(key, out).apply();
                        Toast.makeText(MainActivity.this, "บันทึกแล้ว " + out.size() + " แอป", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("ยกเลิก", null)
                .show();
    }

    private void askPermissions() {''')
wr(p, t)
