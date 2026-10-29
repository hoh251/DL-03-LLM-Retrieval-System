# DL-03-LLM Retrieval System

อ่านเอกสาร แบ่งข้อความเป็น chunk สร้าง embeddings และค้นด้วย FAISS รวมโหมด PDF ที่เก็บชื่อไฟล์และเลขหน้า

## ติดตั้งและรันบน Windows

1. ติดตั้ง Python 3.12 แล้วเปิด `SETUP.cmd`
2. เปิด `RUN.cmd` เพื่อรันแล็ปและสร้างไฟล์ที่จำเป็น

เปิด `RUN-PDF.cmd` เพื่อค้นข้อมูลจาก PDF หรือ `RUN.cmd -Chat` สำหรับฐาน Q&A
PDF ใน `data/pdf/` เป็นเอกสารสาธิตที่จัดทำขึ้น รองรับ PDF ที่มี text layer; ไฟล์สแกนต้องทำ OCR ก่อน

แต่ละ repository ทำงานแยกกัน ใช้ `.venv` และ `.cache` ภายในโฟลเดอร์ตัวเอง
การดาวน์โหลดโมเดลครั้งแรกต้องใช้อินเทอร์เน็ต ผู้ที่มี dependencies อยู่แล้วรัน `python run_assignment.py` ได้โดยตรง
ผลลัพธ์ index และ log จะสร้างในเครื่องเมื่อรัน และถูกกันออกจาก Git ด้วย `.gitignore`

## แหล่งที่มา

โค้ดและข้อมูลตั้งต้นจาก [repository รายวิชา](https://github.com/aproot-en/Advanced-Topic-in-Computer-Software-Course), commit `c0db2ac52be9646e68b25d90ce87ac2526dc9a3d`
มีการปรับให้รันบน Windows และเพิ่มตัวเปิดงาน รายละเอียด pipeline อยู่ใน source code และ labs ของแต่ละงาน
