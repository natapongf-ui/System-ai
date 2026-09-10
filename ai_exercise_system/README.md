# 🏋️ ระบบออกกำลังกายอัจฉริยะด้วย AI และ Image Processing

ระบบตรวจจับท่าทางการออกกำลังกายแบบ Real-time ผ่านกล้อง Webcam พัฒนาด้วย Python ทั้งระบบ

---

## 📋 สารบัญ

- [คุณสมบัติ](#คุณสมบัติ)
- [เทคโนโลยีที่ใช้](#เทคโนโลยีที่ใช้)
- [โครงสร้างโปรเจกต์](#โครงสร้างโปรเจกต์)
- [การติดตั้ง](#การติดตั้ง)
- [การใช้งาน](#การใช้งาน)
- [API Documentation](#api-documentation)
- [Google Colab](#google-colab)
- [การทำงานของระบบ](#การทำงานของระบบ)

---

## ✨ คุณสมบัติ

| คุณสมบัติ | รายละเอียด |
|-----------|-----------|
| **Real-time Pose Detection** | ตรวจจับท่าทางผ่าน Webcam แบบ Real-time ด้วย MediaPipe |
| **Pose Comparison** | เปรียบเทียบท่าของผู้ใช้กับท่าต้นแบบด้วย Cosine Similarity |
| **Rep Counter** | นับจำนวนรอบอัตโนมัติด้วย Joint Angle + State Machine |
| **Voice Alert** | แจ้งเตือนเสียงภาษาไทยเมื่อทำท่าผิด |
| **Dashboard** | แสดงสถิติรายวัน/สัปดาห์/เดือนด้วย Plotly |
| **Exercise History** | บันทึกและ Export ประวัติการออกกำลังกาย |
| **JWT Authentication** | ระบบ Login/Register ปลอดภัยด้วย JWT |
| **BMI Calculator** | คำนวณ BMI อัตโนมัติจากข้อมูลผู้ใช้ |

---

## 🛠️ เทคโนโลยีที่ใช้

| ประเภท | เทคโนโลยี |
|--------|-----------|
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **Computer Vision** | OpenCV, MediaPipe Pose |
| **AI/ML** | NumPy, Scikit-learn |
| **Database** | SQLite + SQLAlchemy |
| **Authentication** | JWT (python-jose), SHA256 (passlib) |
| **Charts** | Plotly |
| **Voice** | pyttsx3 |
| **Export** | Pandas, OpenPyXL |

---

## 📁 โครงสร้างโปรเจกต์

```
ai_exercise_system/
├── app/
│   ├── api/                    # FastAPI route handlers
│   ├── audio/
│   │   └── voice_alert.py      # ระบบแจ้งเตือนเสียง
│   ├── database/
│   │   └── database.py         # SQLAlchemy connection
│   ├── models/
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic schemas
│   ├── pose/
│   │   ├── detector.py         # MediaPipe Pose detection
│   │   └── comparator.py       # Pose comparison & rep counting
│   ├── services/               # Business logic services
│   ├── utils/
│   │   └── auth.py             # JWT authentication utilities
│   └── main.py                 # FastAPI application
├── reference_pose/             # Reference pose JSON files
│   ├── squat/
│   │   ├── front.json
│   │   └── side.json
│   ├── pushup/
│   ├── situp/
│   ├── plank/
│   ├── lunge/
│   ├── jumping_jack/
│   ├── bicep_curl/
│   ├── shoulder_press/
│   ├── mountain_climber/
│   └── burpee/
├── static/images/              # Static images
├── logs/                       # Application logs
├── streamlit_app.py            # Streamlit frontend
├── main.py                     # Entry point
├── requirements.txt
├── Dockerfile
├── google_colab_pose_generator.ipynb
└── README.md
```

---

## 🚀 การติดตั้ง

### วิธีที่ 1: ติดตั้งแบบปกติ

```bash
# 1. Clone หรือดาวน์โหลดโปรเจกต์
cd ai_exercise_system

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. รัน FastAPI Backend
python main.py

# 4. รัน Streamlit Frontend (Terminal ใหม่)
python -m streamlit run streamlit_app.py
```

### วิธีที่ 2: Docker

```bash
# Build image
docker build -t ai-exercise-system .

# Run container
docker run -p 8000:8000 -p 8501:8501 ai-exercise-system
```

---

## 💻 การใช้งาน

1. เปิดเบราว์เซอร์ไปที่ `http://localhost:8501`
2. **สมัครสมาชิก** หรือ **เข้าสู่ระบบ**
3. เลือกท่าออกกำลังกายที่ต้องการ
4. อนุญาตให้เบราว์เซอร์เข้าถึงกล้อง Webcam
5. เริ่มออกกำลังกาย ระบบจะตรวจจับและนับรอบอัตโนมัติ

---

## 📡 API Documentation

FastAPI Swagger UI: `http://localhost:8000/docs`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register` | POST | สมัครสมาชิก |
| `/api/login` | POST | เข้าสู่ระบบ (OAuth2) |
| `/api/profile` | GET | ดูข้อมูลโปรไฟล์ |
| `/api/exercises` | GET | รายการท่าออกกำลังกาย |
| `/api/history` | GET/POST | ประวัติการออกกำลังกาย |
| `/api/statistics` | GET | สถิติรวม |
| `/api/reference/{name}` | GET | ดึงข้อมูล Reference Pose |

---

## 🔬 Google Colab

ใช้ไฟล์ `google_colab_pose_generator.ipynb` เพื่อ:

1. อัพโหลดรูปภาพท่าออกกำลังกาย
2. ระบบจะดึง Landmark จาก MediaPipe อัตโนมัติ
3. บันทึกข้อมูล JSON พร้อม Landmark + Joint Angles
4. ดาวน์โหลด `reference_pose.zip` มาใส่ในโปรเจกต์

**รูปแบบชื่อไฟล์:** `{exercise}_{view}.jpg`

ตัวอย่าง: `squat_front.jpg`, `pushup_side.jpg`

---

## ⚙️ การทำงานของระบบ

### Pose Detection Pipeline

```
Webcam Frame
    ↓
OpenCV (BGR → RGB)
    ↓
MediaPipe Pose
    ↓
33 Landmarks (x, y, z, visibility)
    ↓
Joint Angle Calculation
    ↓
Pose Comparison (vs Reference)
    ↓
Accuracy Score (0-100%)
    ↓
Rep Counter (State Machine: UP/DOWN)
    ↓
Voice Alert (ถ้าผิด)
    ↓
Display Result
```

### Pose Comparison Algorithm

ระบบใช้ **Joint Angle Difference** เปรียบเทียบมุมข้อต่อของผู้ใช้กับ Reference Pose:

- ถ้า Accuracy > 90% → ท่าถูกต้อง (Skeleton สีเขียว)
- ถ้า Accuracy ≤ 90% → ท่าผิด (Skeleton สีแดง + แจ้งเตือน)

### Rep Counting Logic

ใช้ **State Machine** ตรวจจับการเปลี่ยนสถานะ:

| ท่า | State UP | State DOWN | เงื่อนไขนับ |
|-----|----------|------------|------------|
| Squat | เข่า > 160° | เข่า < 100° | DOWN → UP |
| Push Up | ข้อศอก > 160° | ข้อศอก < 90° | DOWN → UP |
| Bicep Curl | ข้อศอก < 45° | ข้อศอก > 160° | DOWN → UP |

---

## 👤 บัญชีทดสอบ

```
Username: demo
Password: demo1234
```

---

## 📝 License

MIT License - สำหรับโปรเจกต์จบการศึกษา
