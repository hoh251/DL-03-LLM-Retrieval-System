# DL-03-LLM Retrieval System

Repository นี้มีแล็ปเดียวและเปิดใช้งานได้โดยไม่ต้องมี repository แล็ปอื่น

## วิธีรันบน Windows

1. ติดตั้ง Python 3.12 แล้วเปิด `SETUP.cmd`
2. เปิด `RUN.cmd` เพื่อรันงานพื้นฐานและสร้างผลลัพธ์
3. เปิด RUN-PDF.cmd เพื่อค้นจาก PDF พร้อมชื่อไฟล์และเลขหน้า

ตัวเปิดงานใช้ `.venv` และ `.cache` ใน repository นี้ การรันโมเดลครั้งแรกต้องใช้อินเทอร์เน็ต
ไม่รวม API key, model cache และ binary index ใน Git; `RUN.cmd` สร้าง index ได้ใหม่
ผู้ที่มี environment อยู่แล้วใช้ `python run_assignment.py` ได้โดยตรง

## ผลทดสอบที่บันทึก

PDF: 2 ไฟล์ 6 หน้า ค้นผ่าน 6/6 คำถาม; PDF unit tests 8/8

อ่าน [REPORT.md](REPORT.md), [README-LAB.md](README-LAB.md) และ `evidence/` สำหรับรายละเอียด
ผลทดสอบเดิมเก็บตามจริง log บางไฟล์จึงมีชื่อโฟลเดอร์ก่อนแยก repository
ผลเรียก API สำเร็จไม่ได้ยืนยันว่าเนื้อหาทุกคำตอบถูกต้อง PDF ตัวอย่างเป็นไฟล์สาธิตที่สร้างขึ้น ไม่ใช่ไฟล์อาจารย์

## แหล่งที่มา

โค้ดและข้อมูลตั้งต้นจาก [repository รายวิชา](https://github.com/aproot-en/Advanced-Topic-in-Computer-Software-Course), commit `c0db2ac52be9646e68b25d90ce87ac2526dc9a3d`
ส่วนเพิ่มเติม: เครื่องมือรันบน Windows การแก้ปัญหา runtime และหลักฐานทดสอบ รายละเอียดเฉพาะแล็ปอยู่ในรายงาน
