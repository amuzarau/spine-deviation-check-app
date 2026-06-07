# 🧍‍♂️ Spine Deviation Check App (MVP)

**Spine Deviation Check App** — это **full-stack web-приложение для удалённого предварительного ориентировочного скрининга состояния позвоночника у детей** на основе анализа фотографий **со спины и сбоку**.

> ⚠️ **ВАЖНО**  
> Приложение **НЕ является медицинским диагностическим инструментом**.  
> Оно предназначено для **оценки потенциального риска**  
> (**низкий / средний / высокий**) и **принятия решения о необходимости дальнейшего медицинского обследования**.

---

## 🎯 Назначение проекта

Проект разрабатывается для использования в учреждении:

**УО  
«Могилёвская государственная санаторная школа-интернат  
для детей, больных сколиозом»**  
🔗 https://mgsshi.by/

### Основные цели:
- обеспечить **дистанционный предварительный скрининг** состояния позвоночника ребёнка;
- **снизить нагрузку** на врачей-ортопедов;
- дать родителям и педагогам **ранний ориентир риска**;
- при необходимости — **направить ребёнка на полноценное медицинское обследование**.

---

## 🌐 Онлайн-доступ

- 🎨 **Фронтенд (Streamlit):**  
  https://spine-deviation-check.streamlit.app/

- 🧠 **Бэкенд API (FastAPI):**  
  Развернут в облаке (Render)

- 🗄️ **База данных (PostgreSQL):**  
  Supabase

- 📷 **Образцы фотографий для проверки приложения:**  
  [Открыть папку sample_images](https://github.com/amuzarau/spine-deviation-check-app/tree/main/sample_images)



---

## 🧱 Архитектура проекта (Full-Stack)

### Общая схема (Cloud-Native)

```mermaid
flowchart LR
    User["Родитель / Ученик"]
    Frontend["Streamlit Frontend<br/>Streamlit Community Cloud"]
    Backend["FastAPI Backend<br/>Render + Docker"]
    DB["PostgreSQL<br/>Supabase"]

    User --> Frontend
    Frontend --> Backend
    Backend --> DB
```

---

🧩 **Архитектура по компонентам**

🎨 **Frontend (Streamlit)**

```mermaid
flowchart TD
    UI["Streamlit UI"]
    Upload["Загрузка фото<br/>(спина + бок)"]
    Request["HTTP запрос"]
    Result["Отображение риска<br/>и пояснений"]

    UI --> Upload
    Upload --> Request
    Request --> Result
```

🧠 **Backend (FastAPI / Render)**

```mermaid
flowchart TD
    API["FastAPI API"]
    Analysis["analysis.py<br/>OpenCV + MediaPipe"]
    Logic["Risk Evaluation Logic"]
    DBLayer["SQLAlchemy ORM"]

    API --> Analysis
    Analysis --> Logic
    Logic --> DBLayer
```

🗄️ **Database (PostgreSQL / Supabase)**

```mermaid
erDiagram
    USERS ||--o{ SCREENINGS : has

    USERS {
        uuid id
        text email
        text role
        timestamp created_at
    }

    SCREENINGS {
        uuid id
        uuid user_id
        text frontal_risk
        text sagittal_risk
        text overall_risk
        jsonb metrics
        jsonb explanation
        timestamp created_at
    }
```
---

🔄 **Flow работы приложения**
```mermaid
sequenceDiagram
    participant U as User
    participant F as Streamlit
    participant B as FastAPI
    participant A as analysis.py
    participant D as Database

    U->>F: Загружает 2 фото
    F->>B: POST /analyze
    B->>A: Анализ изображений
    A->>B: Метрики + риск
    B->>D: Сохранение результата
    B->>F: Ответ (JSON)
    F->>U: Отображение результата
```
---

🛠️ **Технологический стек**

🐍 **Backend**

Python 3.11

FastAPI — REST API

OpenCV — обработка изображений

MediaPipe Pose — детекция ключевых точек тела

SQLAlchemy — ORM

Alembic — миграции БД

Docker — production-деплой

---

🎨 **Frontend**

Streamlit

HTTP-интеграция с backend

Responsive UI

---

🗄️ **Database**

PostgreSQL

Supabase (managed cloud DB)

---

🧠 **Ключевая логика — analysis.py**

Файл analysis.py — сердце приложения.
Он отвечает за обработку изображений и первичную оценку состояния позвоночника.

Использование OpenCV

декодирование изображений (cv2.imdecode);

конвертация цветовых пространств (BGR → RGB);

подготовка данных для MediaPipe.

Использование MediaPipe

Pose — детекция 33 ключевых точек тела;

анализ плеч, таза, головы и голеностопа.

📐 **Логика анализа**

1️⃣ Фронтальная плоскость (вид со спины)

Оцениваются:

асимметрия плеч;

асимметрия таза.

Метрика:

|y_left - y_right|


Интерпретация:

малая разница → низкий риск;

выраженная разница → повышенный риск.


2️⃣ Сагиттальная плоскость (вид сбоку)

Оцениваются:

положение головы относительно плеч;

наклон корпуса.

Текущая MVP-метрика:

|x_nose - x_shoulder|


⚠️ Используется координатная, а не угловая модель.

⚠️ Ограничения MVP (осознанно)

не измеряются реальные углы кифоза/лордоза;

не анализируется линия позвоночника;

отсутствует калибровка камеры;

результат намеренно консервативный.

---

🚀 **Пути развития проекта**
🔹 **Без нейросетей (Computer Vision)**

угловые метрики (ear–shoulder–hip);

анализ вертикальной оси тела;

нормализация под рост;

многоточечная оценка осанки.

🔹 **С нейросетями (ML / DL)**

CNN / Vision Transformers;

размеченная обучающая выборка;

регрессия углов позвоночника;

классификация степени риска.

---

🧩 **Возможные дополнительные фичи**

отправка фото врачу-ортопеду (EmailJS);

личный кабинет (auth / roles);

React-frontend;

аналитика истории обследований;

экспорт PDF-отчётов;

медицинская экспертная панель.

---

⚖️ **Медицинский дисклеймер**

**Результаты анализа являются предварительной ориентировочной оценкой
и не заменяют консультацию врача-ортопеда.**
---

🏁 **Статус проекта**

✅ MVP реализован

✅ Full-stack облачное приложение

🚧 Активное развитие

---

👨‍💻 **Автор**

**Андрей Музарев** 
ML-инженер / STEAM-педагог

GitHub: https://github.com/amuzarau 

Website: https://andreimuzarau.com/

⭐ Если вы врач, заинтересованный родитель, педагог или разработчик — обратная связь приветствуется! 
Свяжитесь со мной через форму в разделе Контакты моего веб-сайта **https://andreimuzarau.com/**
