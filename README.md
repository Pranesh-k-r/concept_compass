# Concept Compass

**Concept Compass** is an educational diagnostic web application for Mathematics (Grades 7–8). It helps students discover possible prerequisite concept gaps behind incorrect quiz answers, receive targeted explanations and learning activities, practice related problems, and verify whether their understanding improves.

Developed by **Team IGNITES**: Pranesh K R, Basavaraj M C, Sagar B S.

## 1. Project Overview & Architecture
This application follows a learning cycle: **Diagnose → Explain → Teach → Practise → Verify → Update**. Rather than simply grading a student as correct or incorrect, it analyzes patterns of mistakes to infer underlying prerequisite gaps using a deterministic diagnostic engine and a Math concept graph.

### Architectural Components:
- **Concepts & Prerequisite Graph:** `concepts` app manages the mathematical knowledge hierarchy.
- **Diagnostic Engine & Evidence Reporting:** `diagnostics` and `quizzes` apps handle adaptive quizzing, deterministic evidence-based gap analysis, and the printable Diagnostic Report.
- **Learning & Verification:** `learning` app handles DB-backed micro-lessons, targeted practice, and verification checks.
- **Progress Tracking:** `progress` app manages the `ConceptMastery` state (Mastered/Unmastered) for each student and dynamically color-codes the `vis.js` concept graph.
- **Teacher Portal & Gamification:** `accounts` app handles User profiles, gamification (points/streaks), and class-wide analytics for authorized Teacher accounts.

## 2. Features Implemented (Complete Upgrades)
- **Student Authentication & Roles:** Secure student and teacher login.
- **Gamified Dashboard:** Real-time Chart.js tracking, streaks, and unlockable badges (Bronze, Silver, Gold).
- **Adaptive Quizzing:** Quizzes dynamically scale difficulty based on right/wrong answers.
- **Explainable Diagnostics:** Deterministic engine traces incorrect answers to their foundational prerequisite gap.
- **Visual Concept Graph:** Interactive physics-based graph (`vis.js`) that dynamically colors concepts green or red based on student mastery data.
- **AI Chatbot Tutor:** Rule-based floating widget for contextual hints during practice.
- **Teacher Portal:** Aggregated analytics showing class-wide struggling concepts and student leaderboards.
- **UI/UX Polish:** Modern glassmorphism design, Dark Mode toggle, sound effects, PWA support (`manifest.json`), and printable PDF reports.

## 3. Technology Stack
- **Language:** Python 3
- **Backend:** Django 4.2+
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Vanilla JS, Chart.js, Vis.js
- **Data Analysis:** Pandas (for dataset import)

## 4. Setup Instructions
### Python Version
Python 3.8 to 3.11 is recommended.

### Virtual Environment Creation (Windows)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Dependency Installation
```powershell
pip install -r requirements.txt
```

### Database Migration Commands
```powershell
python manage.py makemigrations
python manage.py migrate
```

## 5. Dataset Import Instructions
To import the `concepts.csv` and `questions.csv` datasets safely into the database:
```powershell
python manage.py import_dataset
```
*(This command safely parses the CSV schema and creates relationships without overwriting student progress).*

## 6. Development Server Startup
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

## 7. Test Commands
To run the automated tests covering quiz logic and the diagnostic engine:
```powershell
python manage.py test
```

## 8. Diagnostic Methodology & Evaluation
The core diagnostic engine (`diagnostics.engine`) does not use hallucination-prone LLMs. It uses a deterministic traversal algorithm. When a student answers incorrectly, the engine traverses downward in the prerequisite tree, identifying the lowest shared prerequisite as the candidate "root gap", assigning a confidence category based on aggregated evidence across the quiz.

To run offline metrics on the 10k synthetic profiles:
```powershell
python manage.py evaluate_diagnostics
```

## 9. Recommended Hackathon Demonstration Sequence
1. **The Hook:** Start on the landing page, hit the Dark Mode toggle (🌙), and explain the "Diagnose → Explain → Teach → Practise → Verify" cycle.
2. **The Quiz:** Log into a student account, click **Start Diagnostic Quiz**, and deliberately answer incorrectly to simulate a struggling student.
3. **The Tech (Diagnostic Report):** Show the judges the Diagnostic Report. Emphasize that the deterministic engine traced the incorrect answer back to a foundational prerequisite gap.
4. **The Solution (Learning):** Click **Start Lesson**. Show the targeted micro-lesson on the exact root cause.
5. **The Verification:** Click **Start Practice**, answer it correctly (listen for the sound effect!), and proceed to Verification. Pass Verification to automatically update the DB's `ConceptMastery` status to "Mastered".
6. **The Wow Factor (Concept Graph):** Navigate to the **Concept Map** to show the interactive graph dynamically updating with their mastered concepts (Green nodes).
7. **Analytics:** End by showing the **Teacher Portal** to demonstrate class-wide tracking and the Student Dashboard for gamification badges.

## 10. Synthetic-Data Limitations
**Important:** The dataset in `Datasets/` is synthetic. The root-gap labels and responses are generated from a simulated latent mastery model. Evaluation metrics generated reflect alignment with the generator's patterns, not real-world pedagogical diagnostic validity. 
