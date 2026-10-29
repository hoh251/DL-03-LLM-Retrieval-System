from pathlib import Path
import tempfile
import unittest
from pypdf import PdfReader, PdfWriter

from src.document_loader import load_pdf_files, load_qa_file
from src.text_splitter import build_chunks, split_text

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parents[2] / "work"
MAIN = ROOT / "data/pdf/main_document1.pdf"
ADD = ROOT / "data/pdf/document2.pdf"


class PdfPipelineTests(unittest.TestCase):
    def test_multiple_files_and_physical_pages(self):
        records = load_pdf_files([MAIN, ADD])
        self.assertEqual([(r["source_file"], r["page_number"]) for r in records],
                         [(MAIN.name, i) for i in range(1, 5)] + [(ADD.name, i) for i in range(1, 3)])

    def test_thai_text_layer_is_extracted(self):
        records = load_pdf_files([MAIN])
        self.assertIn("การอ่านเอกสาร PDF", records[0]["text"])

    def test_chunk_text_and_offsets_match_original_page(self):
        records = load_pdf_files([MAIN, ADD])
        chunks = build_chunks(records, 160, 30)
        self.assertGreater(len(chunks), len(records))
        for chunk in chunks:
            page = records[chunk["qa_id"]]
            self.assertEqual(chunk["text"], page["text"][chunk["page_char_start"]:chunk["page_char_end"]])
            self.assertEqual(chunk["source_file"], page["source_file"])
            self.assertEqual(chunk["page_number"], page["page_number"])

    def test_blank_page_does_not_renumber_physical_pages(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            path = Path(folder) / "with-blank-page.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=595, height=842)
            writer.add_page(PdfReader(MAIN).pages[0])
            writer.write(path)
            self.assertEqual(load_pdf_files([path])[0]["page_number"], 2)

    def test_no_text_layer_is_explicit(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            path = Path(folder) / "blank.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=595, height=842)
            writer.write(path)
            with self.assertRaisesRegex(ValueError, "OCR"):
                load_pdf_files([path])

    def test_password_protection_is_explicit(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            path = Path(folder) / "encrypted.pdf"
            writer = PdfWriter()
            writer.add_page(PdfReader(MAIN).pages[0])
            writer.encrypt("test-password")
            writer.write(path)
            with self.assertRaisesRegex(ValueError, "Password-protected"):
                load_pdf_files([path])

    def test_invalid_overlap_is_rejected(self):
        for size, overlap in [(0, 0), (10, 10), (10, -1), (10, 11)]:
            with self.subTest(size=size, overlap=overlap), self.assertRaises(ValueError):
                split_text("example", size, overlap)

    def test_existing_txt_dataset_still_works(self):
        records = load_qa_file(ROOT / "data/sex_q_a.txt")
        self.assertEqual(len(records), 391)
        self.assertEqual(len(build_chunks(records, 400, 50)), 541)


if __name__ == "__main__":
    unittest.main()
