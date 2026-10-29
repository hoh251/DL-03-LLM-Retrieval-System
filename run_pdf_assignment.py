"""PDF -> page-aware chunks -> embeddings -> FAISS -> real semantic search."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import numpy as np

import config
from src.document_loader import load_pdf_files
from src.text_splitter import build_chunks
from src.embedding_model import EmbeddingModel
from src.vector_store import VectorStore, save_chunk_store

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", nargs="+", type=Path, help="One or more text-layer PDFs")
    parser.add_argument("--chat", action="store_true")
    args = parser.parse_args()
    paths = args.pdf or sorted((ROOT / "data/pdf").glob("*.pdf"))
    if not paths:
        raise ValueError("No PDFs. Place text-layer PDFs under data/pdf or pass --pdf.")
    folder = ROOT / "outputs/pdf"
    folder.mkdir(parents=True, exist_ok=True)
    records = load_pdf_files(paths)
    chunks = build_chunks(records, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    for chunk in chunks:
        page = next(r for r in records if r["id"] == chunk["qa_id"])
        assert chunk["text"] == page["text"][chunk["page_char_start"]:chunk["page_char_end"]]
        assert chunk["page_number"] >= 1 and chunk["source_file"]
    model = EmbeddingModel(config.EMBEDDING_MODEL_NAME)
    embeddings = model.encode([chunk["text"] for chunk in chunks])
    np.save(folder / "embeddings.npy", embeddings)
    store = VectorStore()
    store.build_index(embeddings)
    store.save(str(folder / "document.index"))
    save_chunk_store(chunks, str(folder / "chunk_store.json"))
    (folder / "extracted_text.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    def search(query):
        scores, positions = store.search(model.encode_query(query), min(3, len(chunks)))
        return [{**chunks[int(position)], "score": float(score)} for score, position in zip(scores, positions) if position >= 0]
    cases = [
        ("How does PDF ingestion preserve page numbers?", "main_document1.pdf", 1),
        ("Why use overlap when splitting text into chunks?", "main_document1.pdf", 2),
        ("How does FAISS search normalized embedding vectors?", "main_document1.pdf", 3),
        ("How can search results identify their original source page?", "main_document1.pdf", 4),
        ("How does BM25 keyword search complement dense retrieval?", "document2.pdf", 1),
        ("What is the role of a cross-encoder reranker?", "document2.pdf", 2),
    ] if args.pdf is None else []
    results = []
    for question, expected_file, expected_page in cases:
        found = search(question)
        hit = any(c["source_file"] == expected_file and c["page_number"] == expected_page for c in found)
        results.append({"query": question, "expected_file": expected_file, "expected_page": expected_page,
                        "hit_at_3": hit, "results": found})
        print(question, "HIT" if hit else "MISS", flush=True)
    (folder / "retrieval_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    assert len(chunks) == embeddings.shape[0] == store.index.ntotal
    assert all(r["hit_at_3"] for r in results), "Some sample queries missed the labelled source page; inspect outputs/pdf/retrieval_results.json"
    fixture_description = ("Default PDFs are generated, labelled educational fixtures; not instructor-provided PDFs."
                           if args.pdf is None else "User-supplied PDF inputs; no labelled retrieval benchmark is assumed.")
    summary = {"executed_at_utc": datetime.now(timezone.utc).isoformat(), "files": len(paths),
               "pages_with_text": len(records), "chunks": len(chunks), "embedding_shape": list(embeddings.shape),
               "page_metadata_checked": True, "queries_tested": len(results),
               "hit_at_3": sum(r["hit_at_3"] for r in results)/len(results) if results else None,
               "source_pdfs": [{"file": Path(p).name, "sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in paths],
               "fixture_note": fixture_description,
               "ocr_supported": False}
    evidence = ROOT / "evidence/pdf"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = ["| Question | Expected PDF/page | Hit@3 |", "|---|---|---|"]
    rows += [f"| {r['query']} | {r['expected_file']} / {r['expected_page']} | {r['hit_at_3']} |" for r in results]
    (ROOT / "PDF-REPORT.md").write_text(f"""# งาน 3: การอ่าน PDF และค้นหาพร้อมเลขหน้า

รันจริงเมื่อ UTC {summary['executed_at_utc']}
อ่าน PDF {len(paths)} ไฟล์ รวม {len(records)} หน้าที่มีข้อความ สร้าง {len(chunks)} chunks
และ embeddings ขนาด {list(embeddings.shape)} จากโมเดลเดียวกันทั้งเอกสารและคำถาม

ขั้นตอน: pypdf อ่านข้อความแยกตามหน้าจริง → แบ่ง chunk ภายในหน้า → สร้าง embedding → FAISS → Top-3
metadata เก็บ source_file, source_sha256, page_number (เริ่มที่ 1), page_char_start และ page_char_end
ตรวจย้อนกลับว่าข้อความทุก chunk ตรงกับช่วงข้อความของหน้าเดิมแล้ว

{chr(10).join(rows)}

{'ไฟล์ตัวอย่างเป็นเอกสารสาธิตสองภาษาไทย/อังกฤษที่จัดทำเพื่อทดสอบ ไม่ใช่ไฟล์ของอาจารย์ มีเอกสารหลักและเอกสารเพิ่มเติมเพื่อทดสอบค้นหาข้ามไฟล์' if args.pdf is None else 'ใช้ PDF ที่ผู้ใช้ระบุ จึงไม่มีเฉลยคำถามที่กำหนดไว้ล่วงหน้าและไม่รายงาน accuracy ของชุดนี้'}
ผล Hit@3 บนเอกสารตัวอย่างชุดเล็กไม่ใช่ accuracy สำหรับเอกสารทุกชนิด
รองรับ PDF ที่มี text layer; PDF สแกนล้วนต้องผ่าน OCR ภายนอกก่อน และ PDF มีรหัสผ่านที่เปิดไม่ได้จะถูกปฏิเสธ

รันซ้ำ: python run_pdf_assignment.py
ใช้ไฟล์จริงของคุณ: python run_pdf_assignment.py --pdf path/to/file.pdf path/to/another.pdf --chat
ผลทั้งหมดอยู่ใน outputs/pdf/ และ evidence/pdf/ แยกจากผล Q&A TXT เดิม
""", encoding="utf-8")
    print("Saved PDF-REPORT.md and evidence/pdf/summary.json", flush=True)
    if args.chat:
        while True:
            query = input("\nPDF question (q to exit): ").strip()
            if query.lower() in {"q", "quit", "exit"}:
                break
            if query:
                for rank, chunk in enumerate(search(query), 1):
                    print(f"[{rank}] {chunk['source_file']} page {chunk['page_number']} | {chunk['score']:.4f}\n{chunk['text']}\n")


if __name__ == "__main__":
    main()
