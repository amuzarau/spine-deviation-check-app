import cv2
import numpy as np

# ⬇️ КЛЮЧЕВОЕ ИЗМЕНЕНИЕ
from mediapipe import solutions as mp_solutions


# -------------------------
# MediaPipe Pose init
# -------------------------
mp_pose = mp_solutions.pose

# Warm-up MediaPipe (один раз при старте сервера)
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
        raise ValueError("Не удалось декодировать изображение.")
    return img


# =========================
# BACK VIEW (FRONTAL PLANE)
# =========================
def analyze_back_photo(image_bytes: bytes) -> dict:
    image = _decode_image(image_bytes)

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = _pose_warmup.process(rgb)

    if not result.pose_landmarks:
        raise ValueError("Не удалось обнаружить контуры тела на фото со спины.")

    lm = result.pose_landmarks.landmark

    ls = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lh = lm[mp_pose.PoseLandmark.LEFT_HIP]
    rh = lm[mp_pose.PoseLandmark.RIGHT_HIP]

    shoulder_diff = abs(ls.y - rs.y)
    hip_diff = abs(lh.y - rh.y)

    explanation = []
    if shoulder_diff > 0.04:
        explanation.append("Обнаружена асимметрия плеч (вид со спины).")
    if hip_diff > 0.04:
        explanation.append("Обнаружена асимметрия таза (вид со спины).")
    if not explanation:
        explanation.append("Значимых асимметрий со спины не обнаружено.")

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

    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
    ) as pose:
        result = pose.process(rgb)

    if not result.pose_landmarks:
        raise ValueError("Не удалось обнаружить контуры тела на фото сбоку.")

    lm = result.pose_landmarks.landmark

    nose = lm[mp_pose.PoseLandmark.NOSE]
    shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
    ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]

    forward_head = abs(nose.x - shoulder.x)
    trunk_lean = abs(shoulder.x - ankle.x)

    explanation = []
    if forward_head > 0.06:
        explanation.append("Обнаружено выдвижение головы вперёд (вид сбоку).")
    if trunk_lean > 0.06:
        explanation.append(
            "Обнаружено отклонение корпуса вперёд или назад (вид сбоку)."
        )
    if not explanation:
        explanation.append("Значимых отклонений осанки сбоку не обнаружено.")

    return {
        "forward_head": round(float(forward_head), 3),
        "trunk_lean": round(float(trunk_lean), 3),
        "explanation": explanation,
    }
