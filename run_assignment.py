"""Rebuild all seven labs and save evidence from this machine."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    if args.chat:
        subprocess.run([sys.executable, "main.py"], check=True)
        return
    evidence = ROOT / "evidence"
    evidence.mkdir(exist_ok=True)
    runs = []
    for lab in sorted((ROOT / "labs").glob("lab*.py")):
        result = subprocess.run([sys.executable, str(lab)], capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
        (evidence / f"{lab.stem}.txt").write_text(result.stdout + "\n" + result.stderr,
                                                   encoding="utf-8")
        runs.append({"script": lab.name, "exit_code": result.returncode})
        print(lab.name, "PASS" if result.returncode == 0 else "FAIL", flush=True)
        if result.returncode:
            raise RuntimeError(f"See evidence/{lab.stem}.txt")
    import numpy as np
    import faiss
    chunks = json.loads((ROOT / "outputs/chunks.json").read_text(encoding="utf-8"))
    records = json.loads((ROOT / "outputs/extracted_text.json").read_text(encoding="utf-8"))
    vectors = np.load(ROOT / "outputs/embeddings.npy")
    index = faiss.read_index(str(ROOT / "vector_db/document.index"))
    results = json.loads((ROOT / "outputs/retrieval_results.json").read_text(encoding="utf-8"))
    assert len(chunks) == len(vectors) == index.ntotal
    assert len(results) == 4 and all(len(r["results"]) == 3 for r in results)
    summary = {"executed_at_utc": datetime.now(timezone.utc).isoformat(),
               "records": len(records), "chunks": len(chunks),
               "embedding_shape": list(vectors.shape), "faiss_vectors": index.ntotal,
               "sample_queries": len(results), "labs": runs,
               "answer_mode": "retrieval_only_no_llm"}
    (evidence / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = ["| คำถาม | ผลค้นหาอันดับ 1 | คะแนน cosine |", "|---|---|---:|"]
    for row in results:
        first = row["results"][0]
        rows.append(f"| {row['query']} | {first['question']} | {first['score']:.4f} |")
    report = f"""# ใบงาน 3: RAG — บันทึกผลการทดลองจริง

แหล่งโค้ด: aproot-en/Advanced-Topic-in-Computer-Software-Course, commit c0db2ac
รายงานนี้เป็นผล baseline Q&A TXT; การอ่าน PDF พร้อมเลขหน้าที่เพิ่มภายหลังอยู่ใน PDF-REPORT.md
รันเมื่อ (UTC): {summary['executed_at_utc']}

## วัตถุประสงค์และวิธีทำ

สร้างระบบค้นคืนจากฐานข้อมูล Q&A ภาษาไทย โดยทำ Lab 01–07 ตามลำดับ:
อ่านไฟล์ → แบ่ง chunk → สร้าง multilingual embedding → สร้าง FAISS index
→ แปลงคำถามเป็นเวกเตอร์ → ค้นหาด้วย cosine similarity → รวมเป็น retrieval pipeline

ข้อมูลจริงของโค้ดเป็น `data/sex_q_a.txt` แม้ README ต้นฉบับบางส่วนจะกล่าวถึง PDF
ใช้โมเดล paraphrase-multilingual-MiniLM-L12-v2, chunk size 400 ตัวอักษร,
overlap 50 ตัวอักษร และ Top-k = 3 ใน Lab 07

## ผลที่ได้จากเครื่องนี้

- อ่าน Q&A ได้ {len(records)} รายการ และสร้าง {len(chunks)} chunks
- embedding shape = {list(vectors.shape)}
- FAISS มี {index.ntotal} เวกเตอร์ ตรงกับจำนวน chunks
- รันทั้ง 7 labs สำเร็จ และทดลองค้นหา {len(results)} คำถาม

{chr(10).join(rows)}

## อภิปรายผล

คะแนน similarity ใช้จัดอันดับความใกล้เคียงของข้อความ ไม่ใช่ความน่าจะเป็นว่าคำตอบถูกต้อง
การค้นคืน Top-k อาจได้หลายคำถามจากเรื่องใกล้เคียงกัน จึงต้องอ่านเทียบคำถามและคำตอบจริง
ระบบนี้คืนข้อความจากฐานข้อมูลโดยตรง ยังไม่มี LLM สร้างคำตอบ และยังไม่มีชุดประเมินอิสระ
จึงไม่ใช้ผลตัวอย่าง 4 ข้อนี้อ้างเป็น accuracy ของระบบทั้งหมด

## หลักฐานและการรันซ้ำ

- `evidence/lab*.txt`: stdout/stderr ของแต่ละ lab จากการรันครั้งนี้
- `evidence/summary.json`: จำนวนข้อมูลและสถานะทั้ง 7 labs
- `outputs/retrieval_results.json`: ผล Top-3 พร้อม metadata
- `python run_assignment.py`: สร้างใหม่และบันทึกหลักฐาน
- `python run_assignment.py --chat`: ทดลองถามด้วยตัวเอง

สำเนา local ปรับ main.py ให้ใช้ Top-k จาก config.py และแจ้งวิธีสร้าง index เมื่อยังไม่มีไฟล์

เอกสารนี้เป็นผลทดลองที่จัดเตรียมด้วยความช่วยเหลือของ AI ผู้เรียนควรทดสอบและอธิบายการทำงานได้
ก่อนนำไปส่งตามรูปแบบที่อาจารย์กำหนด
"""
    (ROOT / "REPORT.md").write_text(report, encoding="utf-8")
    print("Saved REPORT.md and evidence/summary.json", flush=True)


if __name__ == "__main__":
    main()
