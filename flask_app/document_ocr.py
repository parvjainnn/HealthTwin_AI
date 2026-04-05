"""OCR helpers for uploaded medical bills and prescriptions."""
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}


@lru_cache(maxsize=1)
def _get_paddle_ocr():
    from paddleocr import PaddleOCR

    return PaddleOCR(use_angle_cls=True, lang='en', show_log=False)


def extract_document_text(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == '.pdf':
        return _extract_pdf_text(path)

    if suffix in IMAGE_EXTENSIONS:
        return _extract_image_text(path)

    return {
        'text': '',
        'engine': 'Unsupported',
        'status': 'unsupported',
        'message': 'OCR is only enabled for PDF and image documents.',
    }


def _extract_pdf_text(path):
    try:
        reader = PdfReader(str(path))
        text_parts = []
        for page in reader.pages:
            page_text = (page.extract_text() or '').strip()
            if page_text:
                text_parts.append(page_text)
        combined = '\n\n'.join(text_parts).strip()
        if combined:
            return {
                'text': combined,
                'engine': 'PDF text extraction',
                'status': 'completed',
                'message': 'Embedded PDF text extracted successfully.',
            }
    except Exception:
        pass

    return {
        'text': '',
        'engine': 'PaddleOCR',
        'status': 'unavailable',
        'message': 'No embedded PDF text was found. Upload an image version for PaddleOCR extraction.',
    }


def _extract_image_text(path):
    try:
        ocr = _get_paddle_ocr()
    except Exception as exc:
        return {
            'text': '',
            'engine': 'PaddleOCR',
            'status': 'unavailable',
            'message': f'PaddleOCR is not available: {exc}',
        }

    try:
        result = ocr.ocr(str(path), cls=True)
        lines = []
        for page in result or []:
            for item in page or []:
                if not item or len(item) < 2:
                    continue
                text_block = item[1]
                if isinstance(text_block, (list, tuple)) and text_block:
                    value = str(text_block[0]).strip()
                else:
                    value = str(text_block).strip()
                if value:
                    lines.append(value)

        combined = '\n'.join(lines).strip()
        if combined:
            return {
                'text': combined,
                'engine': 'PaddleOCR',
                'status': 'completed',
                'message': 'Text extracted successfully with PaddleOCR.',
            }

        return {
            'text': '',
            'engine': 'PaddleOCR',
            'status': 'empty',
            'message': 'PaddleOCR ran, but no readable text was detected.',
        }
    except Exception as exc:
        return {
            'text': '',
            'engine': 'PaddleOCR',
            'status': 'failed',
            'message': f'PaddleOCR failed: {exc}',
        }
