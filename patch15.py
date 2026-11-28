# เวอร์ชัน 15: หน้าทดสอบ AI ออฟไลน์ (LiteRT-LM, CPU)
# แยก process จากตัวสัตว์เลี้ยง และไม่อ่าน/เขียนความจำของไอริน
# ต้องรันหลัง patch14.py
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
        raise SystemExit("patch15: หาจุดแก้ไม่เจอหรือเจอซ้ำ: " + old[:70])
    return text.replace(old, new)


wr(J + "OfflineActivity.java", r'''package com.origin.pet;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import com.google.ai.edge.litertlm.Backend;
import com.google.ai.edge.litertlm.Conversation;
import com.google.ai.edge.litertlm.ConversationConfig;
import com.google.ai.edge.litertlm.Engine;
import com.google.ai.edge.litertlm.EngineConfig;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class OfflineActivity extends Activity {
    private static final int PICK = 15;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private Engine engine; // ใช้เฉพาะใน worker
    private TextView status;
    private EditText input;
    private Button pickBtn;
    private Button askBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(48, 96, 48, 48);
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("ทดสอบ AI ออฟไลน์ (CPU)\nหน้านี้ยังไม่ใช้ความจำของไอริน");
        title.setTextSize(18);
        root.addView(title);

        pickBtn = new Button(this);
        pickBtn.setText("1) เลือกไฟล์โมเดล");
        root.addView(pickBtn);

        input = new EditText(this);
        input.setText("IP address คืออะไร ตอบเป็นภาษาไทยง่าย ๆ 3 ประโยค");
        root.addView(input);

        askBtn = new Button(this);
        askBtn.setText("2) ถาม");
        root.addView(askBtn);

        status = new TextView(this);
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        root.addView(status);
        setContentView(scroll);

        status.setText(model().exists() ? "มีไฟล์โมเดลในแอปแล้ว" : "ยังไม่ได้เลือกไฟล์โมเดล");

        pickBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("*/*");
                startActivityForResult(i, PICK);
            }
        });
        askBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ask(input.getText().toString().trim());
            }
        });
    }

    private File model() {
        return new File(getNoBackupFilesDir(), "model.litertlm");
    }

    private void show(final String text) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                status.setText(text);
            }
        });
    }

    private void busy(final boolean b) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                pickBtn.setEnabled(!b);
                askBtn.setEnabled(!b);
                if (b) {
                    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                } else {
                    getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                }
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != PICK || resultCode != RESULT_OK || data == null || data.getData() == null) {
            return;
        }
        final Uri uri = data.getData();
        busy(true);
        worker.execute(new Runnable() {
            @Override
            public void run() {
                importModel(uri);
                busy(false);
            }
        });
    }

    private void importModel(Uri uri) {
        File part = new File(getNoBackupFilesDir(), "model.part");
        try {
            String name = "";
            long size = -1;
            try (Cursor c = getContentResolver().query(uri, null, null, null, null)) {
                if (c != null && c.moveToFirst()) {
                    int n = c.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                    int s = c.getColumnIndex(OpenableColumns.SIZE);
                    if (n >= 0) name = String.valueOf(c.getString(n));
                    if (s >= 0 && !c.isNull(s)) size = c.getLong(s);
                }
            }
            if (!name.endsWith(".litertlm")) {
                show("ไฟล์นี้ไม่ใช่ .litertlm: " + name);
                return;
            }
            part.delete();
            long free = getNoBackupFilesDir().getUsableSpace();
            if (size > 0 && free < size + 1000000000L) {
                show("ที่ว่างไม่พอ ต้องการประมาณ " + gb(size + 1000000000L) + " แต่ว่าง " + gb(free));
                return;
            }
            if (engine != null) {
                engine.close();
                engine = null;
            }
            long done = 0;
            long last = 0;
            try (InputStream in = getContentResolver().openInputStream(uri);
                 OutputStream out = new FileOutputStream(part)) {
                byte[] buf = new byte[1 << 20];
                int len;
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                    done += len;
                    if (done - last >= 100000000L) {
                        last = done;
                        show("กำลังคัดลอก " + gb(done) + (size > 0 ? " / " + gb(size) : "")
                                + "\nอย่าออกจากหน้านี้");
                    }
                }
            }
            if (size > 0 && done != size) {
                part.delete();
                show("คัดลอกไม่ครบ ลองใหม่อีกครั้ง");
                return;
            }
            if (!part.renameTo(model())) {
                show("บันทึกไฟล์โมเดลไม่สำเร็จ");
                return;
            }
            show("คัดลอกเสร็จ " + gb(done) + "\nกดปุ่ม 2) ถาม ได้เลย");
        } catch (Throwable e) {
            part.delete();
            show("ผิดพลาดตอนคัดลอก: " + e);
        }
    }

    private static String gb(long bytes) {
        return String.format(java.util.Locale.US, "%.2f GB", bytes / 1e9);
    }

    private void ask(final String question) {
        if (question.isEmpty()) return;
        if (!model().exists()) {
            show("กดปุ่ม 1) เลือกไฟล์โมเดล ก่อน");
            return;
        }
        busy(true);
        show("กำลังคิด... ครั้งแรกต้องโหลดโมเดลก่อน");
        worker.execute(new Runnable() {
            @Override
            public void run() {
                long start = System.currentTimeMillis();
                try {
                    if (engine == null) {
                        Engine e = new Engine(new EngineConfig(model().getAbsolutePath(),
                                new Backend.CPU(), null, null, null, null,
                                getCacheDir().getAbsolutePath()));
                        e.initialize();
                        engine = e;
                    }
                    try (Conversation chat = engine.createConversation(new ConversationConfig())) {
                        String answer = String.valueOf(chat.sendMessage(question));
                        long sec = (System.currentTimeMillis() - start) / 1000;
                        show(answer + "\n\n(ใช้เวลา " + sec + " วินาที)");
                    }
                } catch (Throwable e) {
                    show("ผิดพลาด: " + e);
                }
                busy(false);
            }
        });
    }

    @Override
    protected void onDestroy() {
        worker.execute(new Runnable() {
            @Override
            public void run() {
                if (engine != null) {
                    engine.close();
                    engine = null;
                }
            }
        });
        worker.shutdown();
        super.onDestroy();
    }
}
''')

p = ROOT + "/app/src/main/AndroidManifest.xml"
t = rd(p)
t = rep(t, "    </application>",
'''        <activity
            android:name=".OfflineActivity"
            android:exported="false"
            android:process=":llm"
            android:configChanges="orientation|screenSize|screenLayout|smallestScreenSize|uiMode|keyboardHidden" />
    </application>''')
wr(p, t)

p = J + "MainActivity.java"
t = rd(p)
t = rep(t, '        addButton(root, "1) อนุญาตแสดงทับแอปอื่น",',
'''        addButton(root, "ทดสอบ AI ออฟไลน์", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new android.content.Intent(MainActivity.this, OfflineActivity.class));
            }
        });

        addButton(root, "1) อนุญาตแสดงทับแอปอื่น",''')
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v15"', t)
if n != 1:
    raise SystemExit("patch15: หาชื่อหัวแอปไม่เจอ")
wr(p, t)

p = ROOT + "/gradle.properties"
t = rd(p)
t = rep(t, "android.useAndroidX=false", "android.useAndroidX=true")
wr(p, t)

p = ROOT + "/app/build.gradle"
t = rd(p)
t, n1 = re.subn(r"versionCode \d+", "versionCode 15", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "15.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch15: แก้เวอร์ชันไม่ได้")
t = rep(t, '        minSdk 26\n',
'''        minSdk 26
        ndk {
            abiFilters 'arm64-v8a'
        }
''')
t = t.rstrip("\n") + '''

dependencies {
    implementation 'com.google.ai.edge.litertlm:litertlm-android:0.16.1'
}
'''
wr(p, t)
print("patch15 สำเร็จ: เพิ่มหน้าทดสอบ AI ออฟไลน์")
