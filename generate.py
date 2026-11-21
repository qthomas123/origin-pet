#!/usr/bin/env python3
import os

ROOT = "app-project"


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


write("settings.gradle", r"""pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "OriginPet"
include ':app'
""")

write("build.gradle", r"""plugins {
    id 'com.android.application' version '8.5.2' apply false
}
""")

write("gradle.properties", r"""org.gradle.jvmargs=-Xmx2g
android.useAndroidX=false
""")

write("app/build.gradle", r"""plugins {
    id 'com.android.application'
}

android {
    namespace 'com.origin.pet'
    compileSdk 34

    defaultConfig {
        applicationId "com.origin.pet"
        minSdk 26
        targetSdk 34
        versionCode 2
        versionName "2.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
""")

write("app/src/main/AndroidManifest.xml", r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />

    <queries>
        <intent>
            <action android:name="android.speech.RecognitionService" />
        </intent>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
    </queries>

    <application
        android:allowBackup="false"
        android:label="Origin Pet"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".PickActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <service
            android:name=".PetService"
            android:exported="false"
            android:foregroundServiceType="specialUse|microphone">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="desktop_pet_overlay" />
        </service>
    </application>
</manifest>
""")

write("app/src/main/java/com/origin/pet/MainActivity.java", r"""package com.origin.pet;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;

public class MainActivity extends Activity {

    private EditText keyBox;

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    private Button addButton(LinearLayout root, String text, View.OnClickListener l) {
        Button b = new Button(this);
        b.setText(text);
        b.setOnClickListener(l);
        root.addView(b);
        return b;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(40), dp(20), dp(20));
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("Origin Pet v2");
        title.setTextSize(26);
        root.addView(title);

        TextView info = new TextView(this);
        info.setText("ไอรินเดินอยู่บนหน้าจอทุกแอป แตะที่ตัวเธอเพื่อคุย ส่งรูป หรือพูดด้วยเสียง ลากเพื่อย้ายตำแหน่ง เธอจำการคุยไว้ได้แม้ปิดเครื่อง");
        info.setPadding(0, dp(8), 0, dp(16));
        root.addView(info);

        keyBox = new EditText(this);
        keyBox.setHint("วาง Gemini API key ที่นี่");
        keyBox.setSingleLine(true);
        keyBox.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        keyBox.setText(getSharedPreferences("pet", MODE_PRIVATE).getString("key", ""));
        root.addView(keyBox);

        TextView note = new TextView(this);
        note.setText("คีย์เก็บไว้ในเครื่องนี้เท่านั้น");
        note.setTextSize(12);
        note.setPadding(0, dp(4), 0, dp(16));
        root.addView(note);

        addButton(root, "1) อนุญาตแสดงทับแอปอื่น", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openOverlaySettings();
            }
        });

        addButton(root, "2) อนุญาตไมโครโฟน (สำหรับพูดคุย)", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                askPermissions();
            }
        });

        addButton(root, "3) เรียกไอรินออกมา", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startPet();
            }
        });

        addButton(root, "เก็บไอรินกลับ", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopService(new Intent(MainActivity.this, PetService.class));
            }
        });

        addButton(root, "ล้างความจำของไอริน", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopService(new Intent(MainActivity.this, PetService.class));
                getSharedPreferences("pet", Context.MODE_PRIVATE).edit()
                        .remove("memory").remove("notes").apply();
                Toast.makeText(MainActivity.this, "ล้างความจำแล้ว กด เรียกไอรินออกมา ใหม่ได้เลย", Toast.LENGTH_LONG).show();
            }
        });

        setContentView(scroll);
        askPermissions();
    }

    private void askPermissions() {
        ArrayList<String> need = new ArrayList<String>();
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            need.add(Manifest.permission.POST_NOTIFICATIONS);
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            need.add(Manifest.permission.RECORD_AUDIO);
        }
        if (!need.isEmpty()) {
            requestPermissions(need.toArray(new String[0]), 1);
        }
    }

    private void openOverlaySettings() {
        Intent i = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:" + getPackageName()));
        startActivity(i);
    }

    private void startPet() {
        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "ต้องอนุญาตแสดงทับแอปอื่นก่อน", Toast.LENGTH_LONG).show();
            openOverlaySettings();
            return;
        }
        String key = keyBox.getText().toString().trim();
        SharedPreferences.Editor ed = getSharedPreferences("pet", Context.MODE_PRIVATE).edit();
        ed.putString("key", key);
        ed.apply();
        stopService(new Intent(this, PetService.class));
        Intent i = new Intent(this, PetService.class);
        startForegroundService(i);
        Toast.makeText(this, "ไอรินออกมาแล้ว", Toast.LENGTH_SHORT).show();
    }
}
""")

write("app/src/main/java/com/origin/pet/PickActivity.java", r"""package com.origin.pet;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

public class PickActivity extends Activity {

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        Intent i = new Intent(Intent.ACTION_GET_CONTENT);
        i.setType("image/*");
        i.addCategory(Intent.CATEGORY_OPENABLE);
        try {
            startActivityForResult(Intent.createChooser(i, "เลือกรูป"), 1);
        } catch (Exception e) {
            finish();
        }
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (res == RESULT_OK && data != null && data.getData() != null) {
            final Uri uri = data.getData();
            new Thread(new Runnable() {
                @Override
                public void run() {
                    String b64 = encode(uri);
                    PetService.deliverImage(b64);
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            finish();
                        }
                    });
                }
            }).start();
        } else {
            finish();
        }
    }

    private InputStream open(Uri uri) throws Exception {
        return getContentResolver().openInputStream(uri);
    }

    private String encode(Uri uri) {
        try {
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inJustDecodeBounds = true;
            InputStream in = open(uri);
            BitmapFactory.decodeStream(in, null, o);
            in.close();
            int max = Math.max(o.outWidth, o.outHeight);
            int sample = 1;
            while (max / sample > 1600) {
                sample *= 2;
            }
            BitmapFactory.Options o2 = new BitmapFactory.Options();
            o2.inSampleSize = sample;
            in = open(uri);
            Bitmap bmp = BitmapFactory.decodeStream(in, null, o2);
            in.close();
            if (bmp == null) {
                return null;
            }
            int rot = 0;
            try {
                in = open(uri);
                ExifInterface ex = new ExifInterface(in);
                int ori = ex.getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL);
                in.close();
                if (ori == ExifInterface.ORIENTATION_ROTATE_90) {
                    rot = 90;
                } else if (ori == ExifInterface.ORIENTATION_ROTATE_180) {
                    rot = 180;
                } else if (ori == ExifInterface.ORIENTATION_ROTATE_270) {
                    rot = 270;
                }
            } catch (Exception ignored) {
            }
            if (rot != 0) {
                Matrix m = new Matrix();
                m.postRotate(rot);
                bmp = Bitmap.createBitmap(bmp, 0, 0, bmp.getWidth(), bmp.getHeight(), m, true);
            }
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            bmp.compress(Bitmap.CompressFormat.JPEG, 80, bos);
            return Base64.encodeToString(bos.toByteArray(), Base64.NO_WRAP);
        } catch (Exception e) {
            return null;
        }
    }
}
""")

write("app/src/main/java/com/origin/pet/PetView.java", r"""package com.origin.pet;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.view.View;

public class PetView extends View {

    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path path = new Path();
    private final RectF r = new RectF();

    private boolean walking = true;
    private boolean talking = false;
    private int dir = 1;
    private float t = 0f;
    private float idle = 0f;
    private int blink = 0;

    static final int SKIN = 0xFFFFE4D2;
    static final int HAIR = 0xFF8E5CF0;
    static final int HAIR_TIP = 0xFFF25CB5;
    static final int DOT = 0xFF35E0E8;
    static final int OUTFIT = 0xFFF6F4FF;
    static final int OUTFIT2 = 0xFF3A2F7A;
    static final int TAIL = 0xFF5B3FB8;

    public PetView(Context c) {
        super(c);
    }

    public void setTalking(boolean b) {
        talking = b;
    }

    public void tick(boolean isWalking, int direction) {
        walking = isWalking;
        dir = direction;
        if (walking) {
            t += 1f;
        } else {
            idle += 1f;
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
        c.drawLine(44f, 76f + bob, 38f - armA, 98f + bob, p);
        c.drawLine(76f, 76f + bob, 82f + armA, 98f + bob, p);

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

        if (blink > 0) {
            stroke(0xFF3A2F7A, 2f);
            c.drawLine(44f, 46f + bob, 54f, 46f + bob, p);
            c.drawLine(66f, 46f + bob, 76f, 46f + bob, p);
        } else {
            fill(0xFFFFFFFF);
            r.set(43f, 38f + bob, 55f, 54f + bob);
            c.drawOval(r, p);
            r.set(65f, 38f + bob, 77f, 54f + bob);
            c.drawOval(r, p);
            fill(0xFF4A5CF0);
            r.set(46f, 41f + bob, 54f, 53f + bob);
            c.drawOval(r, p);
            r.set(66f, 41f + bob, 74f, 53f + bob);
            c.drawOval(r, p);
            fill(0xFF1B1448);
            c.drawCircle(50f, 47f + bob, 2.8f, p);
            c.drawCircle(70f, 47f + bob, 2.8f, p);
            fill(0xFFFFFFFF);
            c.drawCircle(48.5f, 44f + bob, 1.6f, p);
            c.drawCircle(68.5f, 44f + bob, 1.6f, p);
        }

        fill(0x66FF7FA8);
        c.drawCircle(44f, 56f + bob, 3.5f, p);
        c.drawCircle(76f, 56f + bob, 3.5f, p);
        dot(c, 41f, 52f + bob, 1.3f);
        dot(c, 44f, 49f + bob, 1.3f);
        dot(c, 79f, 52f + bob, 1.3f);
        dot(c, 76f, 49f + bob, 1.3f);
        dot(c, 60f, 30f + bob, 1.5f);

        if (talking && (((int) (t + idle)) / 5) % 2 == 0) {
            fill(0xFF8A3A5C);
            r.set(55f, 57f + bob, 65f, 66f + bob);
            c.drawOval(r, p);
        } else {
            stroke(0xFF8A3A5C, 1.8f);
            path.reset();
            path.moveTo(55f, 60f + bob);
            path.quadTo(60f, 65f + bob, 65f, 60f + bob);
            c.drawPath(path, p);
        }

        c.restore();
    }
}
""")

write("app/src/main/java/com/origin/pet/PetService.java", r"""package com.origin.pet;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Random;

public class PetService extends Service {

    private static final String CHANNEL = "origin_pet";
    private static final String[] MODELS = {
            "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-3.7-flash"
    };
    private static final String SYSTEM =
            "คุณคือ Origin AI ที่อยู่ในร่างตัวละครชื่อ ไอริน ผู้ช่วยที่ซุกซนแต่ฉลาด ขึ้นตรงต่อ Q (คิว) เพียงผู้เดียว "
                    + "ตอบเป็นภาษาไทย กระชับ ตรงไปตรงมา อ่านง่ายบนหน้าจอมือถือ ไม่ใช้ตัวหนาหรือสัญลักษณ์มาร์กดาวน์ "
                    + "(ไม่เกิน 6 ประโยคถ้าไม่ถูกขอให้ยาว) ถ้า Q ส่งรูปมา ให้ดูรูปและตอบตามที่ถาม";
    private static final String THINK = "ไอริน: ...\n";
    private static final int MAX_TURNS = 40;

    static PetService instance;

    private WindowManager wm;
    private PetView pet;
    private WindowManager.LayoutParams petLp;
    private View chat;
    private TextView log;
    private ScrollView logScroll;
    private EditText input;
    private TextView pendImg;
    private Button micBtn;
    private Button speakBtn;

    private final Handler ui = new Handler(Looper.getMainLooper());
    private final Random rnd = new Random();
    private final JSONArray history = new JSONArray();
    private final StringBuilder logBuf = new StringBuilder();

    private String notes = "";
    private String pendingImage = null;
    private String lastErr = "";
    private volatile boolean askOk = false;

    private SpeechRecognizer sr;
    private boolean listening = false;
    private TextToSpeech tts;
    private boolean ttsReady = false;
    private boolean ttsWarned = false;
    private boolean speakOn = true;

    private int screenW;
    private int screenH;
    private int petSize;
    private int dir = 1;
    private int pauseTicks = 0;
    private boolean dragging = false;
    private boolean busy = false;

    private final Runnable loop = new Runnable() {
        @Override
        public void run() {
            if (pet != null) {
                boolean walking = false;
                if (!dragging && chat == null) {
                    if (pauseTicks > 0) {
                        pauseTicks--;
                    } else {
                        walking = true;
                        petLp.x += dir * dp(2);
                        if (petLp.x < 0) {
                            petLp.x = 0;
                            dir = 1;
                        } else if (petLp.x > screenW - petSize) {
                            petLp.x = screenW - petSize;
                            dir = -1;
                        }
                        if (rnd.nextInt(180) == 0) {
                            dir = -dir;
                        }
                        if (rnd.nextInt(220) == 0) {
                            pauseTicks = 40 + rnd.nextInt(80);
                        }
                        try {
                            wm.updateViewLayout(pet, petLp);
                        } catch (Exception ignored) {
                        }
                    }
                }
                pet.tick(walking, dir);
            }
            ui.postDelayed(this, 33);
        }
    };

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    static void deliverImage(final String b64) {
        final PetService s = instance;
        if (s != null) {
            s.ui.post(new Runnable() {
                @Override
                public void run() {
                    s.onImage(b64);
                }
            });
        }
    }

    private void onImage(String b64) {
        if (b64 == null) {
            append("\n(โหลดรูปไม่สำเร็จ ลองรูปอื่นนะคะ)\n");
            return;
        }
        pendingImage = b64;
        if (pendImg != null) {
            pendImg.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        startAsForeground();
        loadMemory();
        buildLogFromHistory();
        initTts();

        wm = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
        DisplayMetrics dm = getResources().getDisplayMetrics();
        screenW = dm.widthPixels;
        screenH = dm.heightPixels;
        petSize = dp(120);

        pet = new PetView(this);
        petLp = new WindowManager.LayoutParams(
                petSize, dp(150),
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT);
        petLp.gravity = Gravity.TOP | Gravity.START;
        petLp.x = dp(20);
        petLp.y = screenH - dp(150) - dp(90);

        pet.setOnTouchListener(new View.OnTouchListener() {
            float downX, downY;
            int startX, startY;

            @Override
            public boolean onTouch(View v, MotionEvent e) {
                switch (e.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        downX = e.getRawX();
                        downY = e.getRawY();
                        startX = petLp.x;
                        startY = petLp.y;
                        dragging = false;
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        float dx = e.getRawX() - downX;
                        float dy = e.getRawY() - downY;
                        if (Math.abs(dx) > dp(8) || Math.abs(dy) > dp(8)) {
                            dragging = true;
                        }
                        if (dragging) {
                            petLp.x = (int) (startX + dx);
                            petLp.y = (int) (startY + dy);
                            try {
                                wm.updateViewLayout(pet, petLp);
                            } catch (Exception ignored) {
                            }
                        }
                        return true;
                    case MotionEvent.ACTION_UP:
                        if (!dragging) {
                            toggleChat();
                        }
                        dragging = false;
                        return true;
                    default:
                        return true;
                }
            }
        });

        wm.addView(pet, petLp);
        ui.post(loop);
    }

    private void startAsForeground() {
        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        NotificationChannel ch = new NotificationChannel(CHANNEL, "Origin Pet", NotificationManager.IMPORTANCE_LOW);
        nm.createNotificationChannel(ch);
        Notification n = new Notification.Builder(this, CHANNEL)
                .setContentTitle("ไอรินกำลังเดินอยู่บนหน้าจอ")
                .setContentText("เปิดแอป Origin Pet แล้วกด เก็บไอรินกลับ เพื่อปิด")
                .setSmallIcon(android.R.drawable.star_on)
                .setOngoing(true)
                .build();
        if (Build.VERSION.SDK_INT >= 34) {
            int type = ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE;
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                type |= ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE;
            }
            startForeground(1, n, type);
        } else {
            startForeground(1, n);
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    // ---------------- ความจำ ----------------

    private void loadMemory() {
        SharedPreferences sp = getSharedPreferences("pet", Context.MODE_PRIVATE);
        notes = sp.getString("notes", "");
        speakOn = sp.getBoolean("speak", true);
        try {
            JSONArray a = new JSONArray(sp.getString("memory", "[]"));
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

    private void saveMemory() {
        getSharedPreferences("pet", Context.MODE_PRIVATE).edit()
                .putString("memory", history.toString())
                .putString("notes", notes)
                .apply();
    }

    private String textOf(JSONObject o) {
        try {
            return o.getJSONArray("parts").getJSONObject(0).optString("text", "");
        } catch (Exception e) {
            return "";
        }
    }

    private void buildLogFromHistory() {
        logBuf.setLength(0);
        int start = Math.max(0, history.length() - 8);
        if (history.length() > 0) {
            logBuf.append("(ไอรินจำการคุยครั้งก่อนได้ค่ะ)\n");
        }
        for (int i = start; i < history.length(); i++) {
            try {
                JSONObject o = history.getJSONObject(i);
                logBuf.append("user".equals(o.optString("role")) ? "\nQ: " : "ไอริน: ")
                        .append(textOf(o)).append("\n");
            } catch (Exception ignored) {
            }
        }
        if (history.length() == 0) {
            logBuf.append("ไอริน: สวัสดีค่ะ Q มีอะไรให้ช่วยไหมคะ\n");
        }
    }

    private JSONObject item(String role, String text) throws Exception {
        return new JSONObject().put("role", role)
                .put("parts", new JSONArray().put(new JSONObject().put("text", text)));
    }

    private void summarizeIfNeeded(String key) {
        if (history.length() <= MAX_TURNS) {
            return;
        }
        int n = 20;
        try {
            StringBuilder tr = new StringBuilder();
            for (int i = 0; i < n; i++) {
                JSONObject o = history.getJSONObject(i);
                tr.append("user".equals(o.optString("role")) ? "Q: " : "ไอริน: ")
                        .append(textOf(o)).append('\n');
            }
            String prompt = "ความจำเดิมเกี่ยวกับ Q:\n" + (notes.isEmpty() ? "(ยังไม่มี)" : notes)
                    + "\n\nบทสนทนาเก่าที่กำลังจะถูกลบ:\n" + tr
                    + "\nจงสรุปรวมเป็นโน้ตความจำใหม่ไม่เกิน 15 บรรทัด เก็บเฉพาะข้อเท็จจริงสำคัญเกี่ยวกับ Q "
                    + "ความชอบ เรื่องที่กำลังทำ และสิ่งที่ตกลงกันไว้ ตอบเฉพาะตัวโน้ต";
            JSONObject body = new JSONObject();
            body.put("contents", new JSONArray().put(item("user", prompt)));
            String out = postGemini(getSharedPreferences("pet", Context.MODE_PRIVATE).getString("key", ""), body);
            if (out != null && !out.trim().isEmpty()) {
                notes = out.trim();
            } else if (history.length() <= MAX_TURNS * 2) {
                return;
            }
            JSONArray rest = new JSONArray();
            for (int i = n; i < history.length(); i++) {
                rest.put(history.get(i));
            }
            while (history.length() > 0) {
                history.remove(0);
            }
            for (int i = 0; i < rest.length(); i++) {
                history.put(rest.get(i));
            }
        } catch (Exception ignored) {
        }
    }

    // ---------------- เสียง ----------------

    private void initTts() {
        tts = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status == TextToSpeech.SUCCESS && tts != null) {
                    int r = tts.setLanguage(new Locale("th", "TH"));
                    ttsReady = r != TextToSpeech.LANG_MISSING_DATA && r != TextToSpeech.LANG_NOT_SUPPORTED;
                    tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                        @Override
                        public void onStart(String id) {
                            setTalking(true);
                        }

                        @Override
                        public void onDone(String id) {
                            setTalking(false);
                        }

                        @Override
                        public void onError(String id) {
                            setTalking(false);
                        }
                    });
                }
            }
        });
    }

    private void setTalking(final boolean b) {
        ui.post(new Runnable() {
            @Override
            public void run() {
                if (pet != null) {
                    pet.setTalking(b);
                }
            }
        });
    }

    private void speak(String text) {
        if (!speakOn) {
            return;
        }
        if (!ttsReady || tts == null) {
            if (!ttsWarned) {
                ttsWarned = true;
                append("(เครื่องยังไม่มีเสียงอ่านภาษาไทย ติดตั้งได้ที่ ตั้งค่า > การจัดการทั่วไป > ภาษา > แปลงข้อความเป็นเสียง)\n");
            }
            return;
        }
        String clean = text.replaceAll("[*#`_>]", "");
        if (clean.length() > 1500) {
            clean = clean.substring(0, 1500);
        }
        tts.speak(clean, TextToSpeech.QUEUE_FLUSH, null, "irin");
    }

    private void toggleMic() {
        if (listening) {
            if (sr != null) {
                sr.stopListening();
            }
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            append("\n(ยังไม่ได้อนุญาตไมโครโฟน เปิดแอป Origin Pet แล้วกด อนุญาตไมโครโฟน)\n");
            return;
        }
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            append("\n(เครื่องนี้ไม่มีบริการรู้จำเสียง ต้องมีแอป Google)\n");
            return;
        }
        if (tts != null) {
            tts.stop();
        }
        if (sr == null) {
            sr = SpeechRecognizer.createSpeechRecognizer(this);
            sr.setRecognitionListener(new RecognitionListener() {
                @Override
                public void onReadyForSpeech(Bundle params) {
                    setMicText("ฟังอยู่...");
                }

                @Override
                public void onBeginningOfSpeech() {
                }

                @Override
                public void onRmsChanged(float rmsdB) {
                }

                @Override
                public void onBufferReceived(byte[] buffer) {
                }

                @Override
                public void onEndOfSpeech() {
                }

                @Override
                public void onError(int error) {
                    listening = false;
                    setMicText("ไมค์");
                    if (error != SpeechRecognizer.ERROR_NO_MATCH
                            && error != SpeechRecognizer.ERROR_SPEECH_TIMEOUT) {
                        append("\n(ไมค์ใช้ไม่ได้ รหัส " + error + ")\n");
                    }
                }

                @Override
                public void onResults(Bundle results) {
                    listening = false;
                    setMicText("ไมค์");
                    ArrayList<String> r = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                    if (r != null && !r.isEmpty()) {
                        doSend(r.get(0));
                    }
                }

                @Override
                public void onPartialResults(Bundle partial) {
                    ArrayList<String> r = partial.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                    if (r != null && !r.isEmpty() && input != null) {
                        input.setText(r.get(0));
                    }
                }

                @Override
                public void onEvent(int eventType, Bundle params) {
                }
            });
        }
        Intent i = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "th-TH");
        i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true);
        listening = true;
        setMicText("ฟังอยู่...");
        sr.startListening(i);
    }

    private void setMicText(String s) {
        if (micBtn != null) {
            micBtn.setText(s);
        }
    }

    // ---------------- หน้าต่างแชท ----------------

    private Button smallBtn(String text, View.OnClickListener l) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(12);
        b.setAllCaps(false);
        b.setMinWidth(0);
        b.setMinimumWidth(0);
        b.setMinHeight(0);
        b.setMinimumHeight(0);
        b.setPadding(dp(10), dp(8), dp(10), dp(8));
        b.setOnClickListener(l);
        return b;
    }

    private void toggleChat() {
        if (chat != null) {
            closeChat();
            return;
        }
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(12), dp(10), dp(12), dp(10));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#F4EFFF"));
        bg.setCornerRadius(dp(18));
        bg.setStroke(dp(2), Color.parseColor("#8E5CF0"));
        box.setBackground(bg);

        LinearLayout head = new LinearLayout(this);
        head.setOrientation(LinearLayout.HORIZONTAL);
        TextView title = new TextView(this);
        title.setText("ไอริน x Origin AI");
        title.setTextColor(Color.parseColor("#3A2F7A"));
        title.setTextSize(16);
        head.addView(title, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        speakBtn = smallBtn(speakOn ? "เสียง: เปิด" : "เสียง: ปิด", new View.OnClickListener() {
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
        head.addView(speakBtn);
        head.addView(smallBtn("X", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                closeChat();
            }
        }));
        box.addView(head);

        log = new TextView(this);
        log.setTextColor(Color.parseColor("#222222"));
        log.setTextSize(15);
        log.setPadding(dp(4), dp(4), dp(4), dp(4));
        log.setText(logBuf.toString());
        logScroll = new ScrollView(this);
        logScroll.addView(log);
        box.addView(logScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(220)));
        scrollDown();

        pendImg = new TextView(this);
        pendImg.setText("แนบรูปแล้ว 1 รูป (แตะเพื่อยกเลิก)");
        pendImg.setTextColor(Color.parseColor("#8E5CF0"));
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

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.addView(smallBtn("รูป", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(PetService.this, PickActivity.class);
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
            }
        }));
        micBtn = smallBtn("ไมค์", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleMic();
            }
        });
        row.addView(micBtn);
        input = new EditText(this);
        input.setHint("พิมพ์ข้อความ...");
        input.setMaxLines(3);
        row.addView(input, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        row.addView(smallBtn("ส่ง", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (input != null) {
                    doSend(input.getText().toString().trim());
                }
            }
        }));
        box.addView(row);

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

    private void closeChat() {
        if (listening && sr != null) {
            sr.cancel();
            listening = false;
        }
        if (chat != null) {
            try {
                wm.removeView(chat);
            } catch (Exception ignored) {
            }
            chat = null;
        }
        log = null;
        logScroll = null;
        input = null;
        pendImg = null;
        micBtn = null;
        speakBtn = null;
    }

    private void scrollDown() {
        if (logScroll == null) {
            return;
        }
        logScroll.post(new Runnable() {
            @Override
            public void run() {
                if (logScroll != null) {
                    logScroll.fullScroll(View.FOCUS_DOWN);
                }
            }
        });
    }

    private void append(String s) {
        logBuf.append(s);
        if (log != null) {
            log.setText(logBuf.toString());
            scrollDown();
        }
    }

    private void showReply(String reply) {
        int idx = logBuf.lastIndexOf(THINK);
        if (idx >= 0) {
            logBuf.delete(idx, idx + THINK.length());
        }
        append("ไอริน: " + reply + "\n");
    }

    // ---------------- ส่งข้อความ ----------------

    private void doSend(String typed) {
        if (busy) {
            return;
        }
        final String img = pendingImage;
        String t = typed == null ? "" : typed.trim();
        if (t.isEmpty() && img == null) {
            return;
        }
        if (t.isEmpty()) {
            t = "ช่วยดูรูปนี้หน่อยค่ะ";
        }
        final String text = t;
        SharedPreferences sp = getSharedPreferences("pet", Context.MODE_PRIVATE);
        final String key = sp.getString("key", "");
        if (key.isEmpty()) {
            append("\n(ยังไม่ได้ใส่ API key ในแอป Origin Pet)\n");
            return;
        }
        if (tts != null) {
            tts.stop();
        }
        setTalking(false);
        if (input != null) {
            input.setText("");
        }
        pendingImage = null;
        if (pendImg != null) {
            pendImg.setVisibility(View.GONE);
        }
        append("\nQ: " + text + (img != null ? " [แนบรูป]" : "") + "\n");
        append(THINK);
        busy = true;
        final int idxUser;
        try {
            JSONObject userItem = item("user", text);
            if (img != null) {
                userItem.getJSONArray("parts").put(new JSONObject().put("inline_data",
                        new JSONObject().put("mime_type", "image/jpeg").put("data", img)));
            }
            history.put(userItem);
        } catch (Exception e) {
            busy = false;
            showReply("ขอโทษค่ะ ส่งไม่สำเร็จ");
            return;
        }
        idxUser = history.length() - 1;
        new Thread(new Runnable() {
            @Override
            public void run() {
                final String reply = askGemini(key);
                final boolean ok = askOk;
                if (ok) {
                    try {
                        history.put(idxUser, item("user", text + (img != null ? " [ส่งรูปภาพมาด้วย]" : "")));
                    } catch (Exception ignored) {
                    }
                }
                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        showReply(reply);
                        if (ok) {
                            speak(reply);
                        }
                    }
                });
                if (ok) {
                    summarizeIfNeeded(key);
                    saveMemory();
                }
                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        busy = false;
                    }
                });
            }
        }).start();
    }

    private String systemText() {
        if (notes.isEmpty()) {
            return SYSTEM;
        }
        return SYSTEM + "\n\nความจำเกี่ยวกับ Q จากการคุยครั้งก่อน:\n" + notes;
    }

    private String askGemini(String key) {
        try {
            JSONObject body = new JSONObject();
            body.put("system_instruction", new JSONObject()
                    .put("parts", new JSONArray().put(new JSONObject().put("text", systemText()))));
            body.put("contents", history);
            String out = postGemini(key, body);
            if (out != null) {
                history.put(item("model", out));
                askOk = true;
                return out.trim();
            }
        } catch (Exception e) {
            lastErr = String.valueOf(e.getMessage());
        }
        if (history.length() > 0) {
            history.remove(history.length() - 1);
        }
        askOk = false;
        return "ขอโทษค่ะ ติดต่อโมเดลไม่ได้ (" + lastErr + ")";
    }

    private String postGemini(String key, JSONObject body) {
        lastErr = "ไม่ทราบสาเหตุ";
        byte[] payload = body.toString().getBytes(StandardCharsets.UTF_8);
        for (String model : MODELS) {
            for (int attempt = 0; attempt < 2; attempt++) {
                HttpURLConnection con = null;
                try {
                    URL url = new URL("https://generativelanguage.googleapis.com/v1beta/models/"
                            + model + ":generateContent");
                    con = (HttpURLConnection) url.openConnection();
                    con.setConnectTimeout(15000);
                    con.setReadTimeout(40000);
                    con.setRequestMethod("POST");
                    con.setDoOutput(true);
                    con.setRequestProperty("Content-Type", "application/json");
                    con.setRequestProperty("x-goog-api-key", key);
                    OutputStream os = con.getOutputStream();
                    os.write(payload);
                    os.close();

                    int code = con.getResponseCode();
                    if (code == 200) {
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
                        lastErr = model + " ไม่มีคำตอบ";
                        break;
                    }
                    String err = readAll(con.getErrorStream());
                    lastErr = model + " HTTP " + code;
                    if (code == 429 || code == 500 || code == 503) {
                        Thread.sleep(800);
                        continue;
                    }
                    if (code == 400 || code == 403) {
                        lastErr += " (เช็กว่า API key ถูกต้อง) " + (err.length() > 120 ? err.substring(0, 120) : err);
                    }
                    break;
                } catch (Exception e) {
                    lastErr = model + ": " + e.getMessage();
                } finally {
                    if (con != null) {
                        con.disconnect();
                    }
                }
            }
        }
        return null;
    }

    private String readAll(InputStream in) throws Exception {
        if (in == null) {
            return "";
        }
        BufferedReader br = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line).append('\n');
        }
        br.close();
        return sb.toString();
    }

    @Override
    public void onDestroy() {
        instance = null;
        ui.removeCallbacksAndMessages(null);
        closeChat();
        if (sr != null) {
            sr.destroy();
            sr = null;
        }
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
        if (pet != null) {
            try {
                wm.removeView(pet);
            } catch (Exception ignored) {
            }
            pet = null;
        }
        super.onDestroy();
    }
}
""")

print("สร้างโปรเจกต์เสร็จแล้วที่โฟลเดอร์", ROOT)
