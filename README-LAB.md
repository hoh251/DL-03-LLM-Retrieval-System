# ใบงาน 3: RAG

อ่าน REPORT.md เพื่อดูวิธีทดลองและผลจริง; หลักฐานแยก Lab อยู่ใน evidence/
ส่วน PDF ที่เพิ่มให้ตรง README ต้นฉบับอยู่ใน PDF-REPORT.md และ outputs/pdf/
เปิด RUN-PDF.cmd เพื่อลองถามและค้นข้อมูลจากเอกสาร PDF พร้อมชื่อไฟล์และเลขหน้าจริง
RUN.cmd จะรันทั้ง 7 labs, PDF regression tests และ PDF pipeline ตามลำดับ

ดับเบิลคลิก RUN.cmd เพื่อรันทั้ง 7 labs หรือใช้ `RUN.cmd -Chat` เพื่อถาม–ตอบ
ถ้าใช้ Python ที่ติดตั้ง dependencies ไว้แล้ว ให้รัน `python run_assignment.py`
หรือ `python run_assignment.py --chat`

source, data และโครงสร้างตั้งต้นมาจาก DL-03-LLM Retrieval System/RAG-Project
ของ repository aproot-en/Advanced-Topic-in-Computer-Software-Course ที่ commit c0db2ac
เพิ่ม run_assignment.py สำหรับรันครบ เก็บ log ตรวจจำนวนเวกเตอร์ และสร้างรายงาน
ระบบนี้คืนข้อความจากฐานข้อมูล ไม่ได้ใช้ LLM สร้างคำตอบ
รองรับ PDF มี text layer รวมภาษาไทย; PDF สแกนล้วนต้องทำ OCR ภายนอกก่อน
ไฟล์ data/pdf/ เป็นเอกสารสาธิตที่จัดทำเพื่อทดสอบ ไม่ใช่เอกสารอาจารย์

ดู README.md สำหรับ environment, แหล่งที่มา และวิธีติดตั้งบนเครื่องอื่น
