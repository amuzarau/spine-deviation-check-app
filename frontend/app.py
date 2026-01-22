import requests
import streamlit as st
import os

# ==================================
# CONFIG
# ==================================
BACKEND_URL = os.getenv("BACKEND_URL", st.secrets["BACKEND_URL"])

st.set_page_config(
    page_title="Проверка формы позвоночника",
    layout="centered",
)

st.title("🧍 Проверка формы позвоночника")

st.info(
    "⚠️ Приложение осуществляет только предварительную оценку формы позвоночника "
    "и не является медицинским диагнозом. "
    "При наличии сомнений рекомендуется обратиться к врачу-ортопеду."
)

# ==================================
# RISK TRANSLATION
# ==================================
RISK_TRANSLATION = {
    "low": "низкий",
    "medium": "средний",
    "high": "высокий",
}


def translate_risk(value: str) -> str:
    return RISK_TRANSLATION.get(value, value)


# ==================================
# SESSION STATE
# ==================================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("email", None)
st.session_state.setdefault("role", "parent")

# ==================================
# LOGIN (EMAIL ONLY)
# ==================================
if not st.session_state.logged_in:
    st.subheader("🔐 Вход")

    email = st.text_input(
        "Email",
        placeholder="parent@example.com",
    )

    if st.button("Войти"):
        if not email:
            st.warning("Введите email")
        else:
            try:
                res = requests.post(
                    f"{BACKEND_URL}/auth/anonymous",
                    json={"email": email},
                    timeout=10,
                )

                if res.status_code == 200:
                    data = res.json()
                    st.session_state.logged_in = True
                    st.session_state.user_id = data["user_id"]
                    st.session_state.email = email
                    st.session_state.role = data.get("role", "parent")
                    st.rerun()
                else:
                    st.error("Ошибка входа")
                    st.code(res.text)

            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

    st.stop()

# ==================================
# AUTH OK
# ==================================
st.success(f"✅ Вы вошли как: {st.session_state.email}")

# ==================================
# UPLOAD PHOTOS (ОБА ОБЯЗАТЕЛЬНЫ)
# ==================================
st.subheader("📸 Загрузка фотографий")

st.markdown(
    """
**Необходимо загрузить ДВА изображения:**
- 📷 вид **со спины**
- 📷 вид **сбоку**

Максимальный размер файла — **200 МБ**
"""
)

back_photo = st.file_uploader(
    "Фото со спины (обязательно)",
    type=["jpg", "jpeg", "png"],
)

side_photo = st.file_uploader(
    "Фото сбоку (обязательно)",
    type=["jpg", "jpeg", "png"],
)

consent = st.checkbox(
    "Я подтверждаю, что являюсь родителем или законным представителем "
    "и даю согласие на проведение предварительной оценки."
)

# ==================================
# ANALYZE
# ==================================
if st.button("Анализировать"):
    if not consent:
        st.error("Необходимо подтвердить согласие")
    elif not back_photo or not side_photo:
        st.error("Необходимо загрузить оба фото: со спины и сбоку")
    else:
        files = {
            "back_photo": (
                back_photo.name,
                back_photo.getvalue(),
                back_photo.type,
            ),
            "side_photo": (
                side_photo.name,
                side_photo.getvalue(),
                side_photo.type,
            ),
        }

        try:
            with st.spinner("Анализ выполняется..."):
                res = requests.post(
                    f"{BACKEND_URL}/analyze",
                    params={"user_id": st.session_state.user_id},
                    files=files,
                    timeout=120,
                )

            if res.status_code != 200:
                st.error("Ошибка анализа")
                st.code(res.text)
            else:
                data = res.json()

                st.subheader("📊 Результаты оценки")

                st.write(
                    "**Риск деформации позвоночника во фронтальной плоскости:**",
                    translate_risk(data["frontal_risk"]),
                )

                st.write(
                    "**Риск деформации позвоночника в сагиттальной плоскости:**",
                    translate_risk(data["sagittal_risk"]),
                )

                st.write(
                    "**Суммарный риск деформации позвоночника:**",
                    translate_risk(data["overall_risk"]),
                )

                st.markdown("### 🧠 Пояснения")
                for line in data["explanation"]:
                    st.write(f"- {line}")

        except Exception as e:
            st.error(f"Ошибка соединения: {e}")

# ==================================
# HISTORY
# ==================================
st.markdown("---")
st.subheader("📚 История проверок")

try:
    res = requests.get(
        f"{BACKEND_URL}/history/{st.session_state.user_id}",
        timeout=10,
    )

    if res.status_code == 200:
        history = res.json()
        if not history:
            st.info("История пока пуста")
        else:
            for h in history:
                st.markdown(
                    f"""
                    **Дата:** {h["date"]}  
                    **Суммарный риск деформации позвоночника:** {translate_risk(h["overall_risk"])}  
                    ---
                    """
                )
    else:
        st.warning("Не удалось загрузить историю")

except Exception:
    st.warning("Сервер недоступен")

# ==================================
# LOGOUT
# ==================================
st.markdown("---")
if st.button("🚪 Выйти"):
    st.session_state.clear()
    st.rerun()
