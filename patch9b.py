#!/usr/bin/env python3
# เวอร์ชัน 9 ก้อนที่ 2: ไอริน/อารินใช้โมเดลอนิเมะ + อัปเวอร์ชัน (รันต่อจาก patch9.py)
import os
import re

ROOT = "app-project"
J = ROOT + "/app/src/main/java/com/origin/pet/"


def wr(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


PETVIEW = r'''package com.origin.pet;

import android.content.Context;

public class PetView extends AnimeGirl {

    public PetView(Context c) {
        super(c);
        twin = false;
        tail = false;
        headset = false;
        xian = true;
        skinL = 0xFFFFF1EA;
        skinD = 0xFFF3CDBD;
        hairA = 0xFF2B1B4D;
        hairB = 0xFF7A4BC2;
        eyeA = 0xFFE87BC8;
        eyeB = 0xFF5B2FA0;
        topA = 0xFFC9F2EA;
        topB = 0xFF7FCFC4;
        skirtA = 0xFFF1FBF9;
        skirtB = 0xFFA9DCD6;
        accent = 0xFFE6B84A;
        accent2 = 0xFF2FC9B0;
        ink = 0xFF2B1B4D;
        lipCol = 0xFFC2294B;
        tailCol = 0xFF2B1B4D;
    }
}
'''

SAGEVIEW = r'''package com.origin.pet;

import android.content.Context;

public class SageView extends AnimeGirl {

    public SageView(Context c) {
        super(c);
        twin = false;
        tail = false;
        headset = true;
        cyber = true;
        skinL = 0xFFFFEDE2;
        skinD = 0xFFF0C2AE;
        hairA = 0xFF1B2A63;
        hairB = 0xFF2BC6E8;
        eyeA = 0xFFFF7AC8;
        eyeB = 0xFF7A2CC0;
        topA = 0xFF2A3350;
        topB = 0xFF121A33;
        skirtA = 0xFF1B2540;
        skirtB = 0xFF0C1226;
        accent = 0xFFFF4FA8;
        accent2 = 0xFF35E0E8;
        ink = 0xFF14193A;
        tailCol = 0xFF1B2A63;
    }
}
'''

wr(J + "PetView.java", PETVIEW)
wr(J + "SageView.java", SAGEVIEW)

p = ROOT + "/app/build.gradle"
with open(p, encoding="utf-8") as f:
    t = f.read()
t, n1 = re.subn(r"versionCode \d+", "versionCode 9", t)
t, n2 = re.subn(r'versionName "[^"]*"', 'versionName "9.0"', t)
if n1 != 1 or n2 != 1:
    raise SystemExit("patch9b: แก้เวอร์ชันไม่ได้")
wr(p, t)

p = J + "MainActivity.java"
with open(p, encoding="utf-8") as f:
    t = f.read()
t, n = re.subn(r'"Origin Pet v\d+"', '"Origin Pet v9"', t)
if n != 1:
    raise SystemExit("patch9b: หาชื่อหัวแอปไม่เจอ")
wr(p, t)
print("patch9b สำเร็จ: โมเดลอนิเมะพร้อมใช้")
