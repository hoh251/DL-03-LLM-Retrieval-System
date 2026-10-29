# งาน 3: การอ่าน PDF และค้นหาพร้อมเลขหน้า

รันจริงเมื่อ UTC 2026-10-29T14:16:02.257914+00:00
อ่าน PDF 2 ไฟล์ รวม 6 หน้าที่มีข้อความ สร้าง 12 chunks
และ embeddings ขนาด [12, 384] จากโมเดลเดียวกันทั้งเอกสารและคำถาม

ขั้นตอน: pypdf อ่านข้อความแยกตามหน้าจริง → แบ่ง chunk ภายในหน้า → สร้าง embedding → FAISS → Top-3
metadata เก็บ source_file, source_sha256, page_number (เริ่มที่ 1), page_char_start และ page_char_end
ตรวจย้อนกลับว่าข้อความทุก chunk ตรงกับช่วงข้อความของหน้าเดิมแล้ว

| Question | Expected PDF/page | Hit@3 |
|---|---|---|
| How does PDF ingestion preserve page numbers? | main_document1.pdf / 1 | True |
| Why use overlap when splitting text into chunks? | main_document1.pdf / 2 | True |
| How does FAISS search normalized embedding vectors? | main_document1.pdf / 3 | True |
| How can search results identify their original source page? | main_document1.pdf / 4 | True |
| How does BM25 keyword search complement dense retrieval? | document2.pdf / 1 | True |
| What is the role of a cross-encoder reranker? | document2.pdf / 2 | True |

ไฟล์ตัวอย่างเป็นเอกสารสาธิตสองภาษาไทย/อังกฤษที่จัดทำเพื่อทดสอบ ไม่ใช่ไฟล์ของอาจารย์ มีเอกสารหลักและเอกสารเพิ่มเติมเพื่อทดสอบค้นหาข้ามไฟล์
ผล Hit@3 บนเอกสารตัวอย่างชุดเล็กไม่ใช่ accuracy สำหรับเอกสารทุกชนิด
รองรับ PDF ที่มี text layer; PDF สแกนล้วนต้องผ่าน OCR ภายนอกก่อน และ PDF มีรหัสผ่านที่เปิดไม่ได้จะถูกปฏิเสธ

รันซ้ำ: python run_pdf_assignment.py
ใช้ไฟล์จริงของคุณ: python run_pdf_assignment.py --pdf path/to/file.pdf path/to/another.pdf --chat
ผลทั้งหมดอยู่ใน outputs/pdf/ และ evidence/pdf/ แยกจากผล Q&A TXT เดิม
