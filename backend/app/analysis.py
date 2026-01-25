import cv2
import numpy as np
from mediapipe.python.solutions import pose as mp_pose

Pose = mp_pose.Pose
PoseLandmark = mp_pose.PoseLandmark

# -------------------------
# MediaPipe Pose (WARMUP)
# -------------------------

# Прогрев модели (ускоряет первый запрос)
_pose_warmup = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=0,
    enable_segmentation=False,
    min_detection_confidence=0.5,
)


def _decode_image(image_bytes: bytes):
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Не удалось декодировать изображение")
    return img


# =========================
# BACK VIEW (FRONTAL PLANE)
# =========================
def analyze_back_photo(image_bytes: bytes) -> dict:
    image = _decode_image(image_bytes)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    result = _pose_warmup.process(rgb)

    if not result.pose_landmarks:
        raise ValueError("Контуры тела не обнаружены (вид со спины)")

    lm = result.pose_landmarks.landmark

    ls = lm[PoseLandmark.LEFT_SHOULDER]
    rs = lm[PoseLandmark.RIGHT_SHOULDER]
    lh = lm[PoseLandmark.LEFT_HIP]
    rh = lm[PoseLandmark.RIGHT_HIP]

    shoulder_diff = abs(ls.y - rs.y)
    hip_diff = abs(lh.y - rh.y)

    explanation = []
    if shoulder_diff > 0.04:
        explanation.append("Обнаружена асимметрия плеч")
    if hip_diff > 0.04:
        explanation.append("Обнаружена асимметрия таза")
    if not explanation:
        explanation.append("Значимых асимметрий не обнаружено")

    return {
        "shoulder_diff": round(float(shoulder_diff), 3),
        "hip_diff": round(float(hip_diff), 3),
        "explanation": explanation,
    }


# =========================
# SIDE VIEW (SAGITTAL PLANE)
# =========================
def analyze_side_photo(image_bytes: bytes) -> dict:
    image = _decode_image(image_bytes)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
    ) as pose:
        result = pose.process(rgb)

    if not result.pose_landmarks:
        raise ValueError("Контуры тела не обнаружены (вид сбоку)")

    lm = result.pose_landmarks.landmark

    nose = lm[PoseLandmark.NOSE]
    shoulder = lm[PoseLandmark.RIGHT_SHOULDER]
    ankle = lm[PoseLandmark.RIGHT_ANKLE]

    forward_head = abs(nose.x - shoulder.x)
    trunk_lean = abs(shoulder.x - ankle.x)

    explanation = []
    if forward_head > 0.06:
        explanation.append("Выдвижение головы вперёд")
    if trunk_lean > 0.06:
        explanation.append("Отклонение корпуса")
    if not explanation:
        explanation.append("Значимых отклонений не обнаружено")

    return {
        "forward_head": round(float(forward_head), 3),
        "trunk_lean": round(float(trunk_lean), 3),
        "explanation": explanation,
    }
