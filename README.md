# 🎓 Student Skill Exchange

A web-based platform designed to help students share their skills, learn from one another, and collaborate through peer-to-peer skill exchange.

## 🌐 Live Demo

- **Live Website:** https://student-skill-exchange-awky.onrender.com
- **GitHub Repository:** https://github.com/pavanimandati13-jpg/student-skill-exchange

## 📌 Project Overview

Student Skill Exchange is a Python Flask web application developed to support collaborative learning among students. It provides a platform where students can explore skill-sharing opportunities and connect through the exchange of knowledge and abilities.

The project demonstrates the development and cloud deployment of a web application using Python, Flask, HTML, and cloud hosting services.

## 🎯 Objectives

- Encourage peer-to-peer learning among students.
- Promote sharing of knowledge and practical skills.
- Provide a simple interface for skill exchange.
- Support collaboration and knowledge sharing.
- Demonstrate cloud-based web application deployment.

## ✨ Features

- **Skill Exchange:** Supports the concept of sharing and learning skills.
- **Web-Based Interface:** Access the application through a browser.
- **Simple Design:** Provides an interface for users to interact with the application.
- **Python Backend:** Uses Flask to handle application logic.
- **Cloud Deployment:** Hosted on Render for public access.

*Note: The exact available features depend on the implementation in the source code.*

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web application framework |
| HTML | Web page structure |
| CSS | User interface styling |
| Gunicorn | Production WSGI server |
| Render | Cloud hosting and deployment |
| Git | Version control |
| GitHub | Source code hosting |

## 📂 Project Structure

```text
student-skill-exchange/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── Procfile
├── .gitignore
├── templates/
└── tests/
```

## ⚙️ Prerequisites

- Python 3.10 or a compatible version
- pip package manager
- Git
- A modern web browser

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/pavanimandati13-jpg/student-skill-exchange.git
```

### 2. Navigate to the project directory

```bash
cd student-skill-exchange
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Start the application

```bash
python app.py
```

### 7. Open the website

Visit:

http://127.0.0.1:5000

## ☁️ Cloud Deployment

The application is deployed using Render.

**Deployment settings:**

- **Service Type:** Web Service
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

**Live URL:** https://student-skill-exchange-awky.onrender.com

## 🧪 Testing

The project includes
