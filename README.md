# ⚙ Intelligent CPU Scheduler Simulator

---

## 📌 Problem Statement

Develop a simulator for CPU scheduling algorithms (FCFS, SJF, Round Robin, Priority Scheduling) with real-time visualizations. The simulator should allow users to input processes with arrival times, burst times, and priorities and visualize Gantt charts and performance metrics like average waiting time and turnaround time.

---

## 🧱 Project Modules

| # | Module | Tech | Description |
|---|--------|------|-------------|
| M1 | **Scheduling Algorithm Engine** | Python | 7 algorithms implemented as OOP classes |
| M2 | **Process Manager** | JavaScript | Input, validation, state management |
| M3 | **Visualization & AI Insights** | HTML/CSS/JS | Gantt chart, metrics, AI recommendations |

---

## 🚀 Algorithms Implemented

| Algorithm | Type | Complexity |
|-----------|------|-----------|
| FCFS | Non-Preemptive | O(n log n) |
| SJF | Non-Preemptive | O(n²) |
| SRTF | Preemptive | O(n²) |
| Round Robin | Preemptive | O(n × T/q) |
| Priority | Non-Preemptive | O(n²) |
| Preemptive Priority | Preemptive | O(n²) |
| **MLFQ** | **Intelligent** | O(n log n) |

---

## 🛠 Setup & Run

### Prerequisites
```bash
Python 3.10+
pip install flask flask-cors pytest
```

### Run Backend
```bash
python app.py
# API available at http://127.0.0.1:5000
```

### Open Frontend
Open `templates/index.html` in your browser, or access via `http://127.0.0.1:5000`

### Run Tests
```bash
pytest tests/test_schedulers.py -v
```

---

## 📡 API Reference

### POST `/api/schedule`
```json
{
  "algorithm": "fcfs",
  "processes": [
    {"pid": 1, "arrival_time": 0, "burst_time": 6, "priority": 3}
  ],
  "time_quantum": 2
}
```

### GET `/api/algorithms`
Returns list of all available algorithms.

### GET `/api/health`
Health check.

---

## 📁 Project Structure

```
intellisched/
├── app.py                    ← Flask API + all schedulers (Module 1)
├── templates/
│   └── index.html            ← Frontend UI (Module 2 & 3)
├── tests/
│   └── test_schedulers.py    ← Pytest unit tests
├── requirements.txt
└── README.md
```

---

## 📊 Features

- ✅ 7 scheduling algorithms with full preemptive/non-preemptive support
- ✅ Animated Gantt chart with per-process timeline rows
- ✅ Performance metrics: Avg WT, Avg TAT, CPU Utilization, Throughput
- ✅ Process result table with completion/waiting/turnaround breakdown
- ✅ AI Insights: fairness analysis, starvation detection, algorithm recommendation
- ✅ Side-by-side comparison of all 7 algorithms on the same process set
- ✅ 4 preset scenarios (Basic, Convoy Effect, Starvation, Burst Mix)
- ✅ REST API backend (Flask) + vanilla JS frontend
- ✅ 33 unit tests with 100% algorithm coverage
- ✅ Full project report included in Project Report tab

---

## 👥 Team
|      Member       |         Profile Link          |
|-------------------|-------------------------------|
|1. Aman Kumar      |https://github.com/amanmaurya39|
|2. Rohit Sharma    |https://github.com/Rohit-lpu-ai|
|3. Aswadh B Pramod |https://github.com/aswwadhh    |

