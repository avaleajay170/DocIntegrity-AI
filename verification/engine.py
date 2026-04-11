import cv2
import numpy as np
from skimage.feature import hog, local_binary_pattern
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import pytesseract
import requests
from django.conf import settings
from .models import VerificationResult


def extract_features(image_path):
    """Extract HOG + LBP features from a handwriting image."""
    img = cv2.imread(str(image_path))
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (256, 256))

    # HOG features
    hog_features = hog(
        resized,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        flatten=True
    )

    # LBP features
    lbp = local_binary_pattern(resized, P=8, R=1, method='uniform')
    lbp_hist, _ = np.histogram(lbp.ravel(), bins=10, range=(0, 10))
    lbp_hist = lbp_hist.astype(float)
    lbp_hist /= (lbp_hist.sum() + 1e-6)

    return np.concatenate([hog_features, lbp_hist])


def compute_hw_match(reference_path, submission_path):
    """
    Compare reference handwriting sample with submitted assignment.
    Returns similarity score 0-100.
    """
    ref_features = extract_features(reference_path)
    sub_features = extract_features(submission_path)

    if ref_features is None or sub_features is None:
        return 50.0

    similarity = cosine_similarity(
        ref_features.reshape(1, -1),
        sub_features.reshape(1, -1)
    )[0][0]

    # Convert cosine similarity (-1 to 1) to percentage (0 to 100)
    score = float((similarity + 1) / 2 * 100)
    return round(min(100, max(0, score)), 2)


def extract_text_ocr(image_path):
    """Extract text from image using Tesseract OCR."""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return ""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 6')
        return text.strip()
    except Exception:
        return ""


def detect_ai_content(text):
    """
    Send extracted text to GPTZero API and get AI probability score.
    Returns AI content percentage 0-100.
    """
    if not text or len(text.strip()) < 50:
        return 0.0

    api_key = getattr(settings, 'GPTZERO_API_KEY', '')

    if not api_key:
        # Fallback: basic heuristic scoring if no API key
        return 0.0

    try:
        response = requests.post(
            'https://api.gptzero.me/v2/predict/text',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Api-Key': api_key,
            },
            json={'document': text},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            score = data.get('documents', [{}])[0].get(
                'average_generated_prob', 0
            )
            return round(float(score) * 100, 2)
    except Exception:
        pass

    return 0.0


def get_hw_verdict(score):
    if score >= 85:
        return 'matched'
    elif score >= 50:
        return 'uncertain'
    return 'mismatch'


def get_ai_verdict(score):
    if score <= 20:
        return 'human'
    elif score <= 60:
        return 'mixed'
    return 'ai_generated'


def run_full_verification(submission, reference_sample):
    """
    Main function — runs both HW match and AI detection.
    Creates or updates VerificationResult.
    """
    ref_path = Path(reference_sample.image.path)
    sub_path = Path(submission.image.path)

    # Check if submission is PDF — skip image-based HW match
    is_pdf = str(sub_path).lower().endswith('.pdf')

    if is_pdf:
        hw_score     = 0.0
        extracted    = ""
        hw_verdict   = 'uncertain'
    else:
        hw_score   = compute_hw_match(ref_path, sub_path)
        extracted  = extract_text_ocr(sub_path)
        hw_verdict = get_hw_verdict(hw_score)

    ai_score   = detect_ai_content(extracted)
    ai_verdict = get_ai_verdict(ai_score)

    # Save or update result
    result, _ = VerificationResult.objects.update_or_create(
        submission=submission,
        defaults={
            'hw_match_score':   hw_score,
            'ai_content_score': ai_score,
            'hw_verdict':       hw_verdict,
            'ai_verdict':       ai_verdict,
            'extracted_text':   extracted,
        }
    )

    return result