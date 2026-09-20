"""OCR helpers for uploaded medical bills and prescriptions."""
import os
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
BASE_DIR = Path(__file__).resolve().parent.parent
PADDLE_CACHE_DIR = BASE_DIR / '.paddle_cache'
PADDLE_OCR_HOME = BASE_DIR / '.paddleocr'
PADDLE_PDX_CACHE_DIR = BASE_DIR / '.paddlex'
MATPLOTLIB_CACHE_DIR = BASE_DIR / '.matplotlib'
PADDLE_HOME_ROOT = BASE_DIR


def _ensure_paddle_environment():
    PADDLE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PADDLE_OCR_HOME.mkdir(parents=True, exist_ok=True)
    PADDLE_PDX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    MATPLOTLIB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ['HOME'] = str(PADDLE_HOME_ROOT)
    os.environ['USERPROFILE'] = str(PADDLE_HOME_ROOT)
    os.environ['PADDLE_HOME'] = str(PADDLE_CACHE_DIR)
    os.environ['XDG_CACHE_HOME'] = str(PADDLE_CACHE_DIR)
    os.environ['PADDLE_OCR_HOME'] = str(PADDLE_OCR_HOME)
    os.environ['PADDLE_PDX_CACHE_HOME'] = str(PADDLE_PDX_CACHE_DIR)
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
    os.environ['MPLCONFIGDIR'] = str(MATPLOTLIB_CACHE_DIR)
    os.environ['FLAGS_use_mkldnn'] = '0'


@lru_cache(maxsize=1)
def _get_paddle_ocr():
    _ensure_paddle_environment()
    from paddleocr import PaddleOCR

    return PaddleOCR(
        lang='en',
        ocr_version='PP-OCRv4',
        device='cpu',
        enable_mkldnn=False,
        cpu_threads=1,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )


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
        result = ocr.predict(str(path))
        lines = []
        for page in result or []:
            page_data = _normalize_ocr_result(page)
            for value in page_data.get('rec_texts', []):
                cleaned = str(value).strip()
                if cleaned:
                    lines.append(cleaned)

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


def _normalize_ocr_result(result_item):
    if isinstance(result_item, dict):
        return result_item.get('res', result_item)

    if hasattr(result_item, 'json'):
        json_value = getattr(result_item, 'json')
        if isinstance(json_value, dict):
            return json_value.get('res', json_value)

    if hasattr(result_item, 'res'):
        res_value = getattr(result_item, 'res')
        if isinstance(res_value, dict):
            return res_value

    if hasattr(result_item, 'to_dict'):
        dict_value = result_item.to_dict()
        if isinstance(dict_value, dict):
            return dict_value.get('res', dict_value)

    return {}
