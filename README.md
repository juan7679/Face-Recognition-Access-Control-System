# 🔐 Face Recognition Access Control System

> Real-time facial recognition system that identifies registered users and simulates an access control environment using Computer Vision and Artificial Intelligence.

---

## 📌 Project Overview

This project is a real-time facial recognition access control system developed in Python. Using a webcam, the application detects faces, compares them against a registered user database, and determines whether access should be granted or denied.

The system combines face detection, facial recognition, automatic user enrollment, and a custom graphical interface to create an educational simulation of a biometric access control solution.

This project was developed as part of an Artificial Intelligence course, focusing on Computer Vision, machine learning applications, human-computer interaction, and software modularization.

---

## ✨ Features

* 👤 Real-time face detection using MTCNN
* 🧠 Facial recognition using FaceNet through DeepFace
* 📷 Automatic user enrollment through webcam capture
* 🗂️ Local facial database management
* ✅ Access authorization for recognized users
* ❌ Access denial for unknown individuals
* 🎨 Custom graphical dashboard and monitoring interface
* ⚡ Performance optimization through frame-skipping
* 🏗️ Modular software architecture
* 🔒 Consent-based facial data registration

---

## 🏛️ System Architecture

```text
Webcam
   ↓
MTCNN Face Detection
   ↓
FaceNet Embedding Generation
   ↓
DeepFace Similarity Matching
   ↓
Identity Verification
   ↓
Access Control Decision
   ↓
Graphical User Interface
```

---

## 🛠️ Technologies Used

| Technology | Purpose                            |
| ---------- | ---------------------------------- |
| Python     | Core programming language          |
| OpenCV     | Webcam access and image processing |
| MTCNN      | Face detection                     |
| DeepFace   | Facial recognition framework       |
| FaceNet    | Face embedding generation          |
| NumPy      | Matrix and numerical operations    |
| Pillow     | Graphical interface rendering      |
| TensorFlow | Deep learning backend              |

---

## 📁 Project Structure

```text
face-recognition-access-control/
├── main.py
├── interfaz.py
├── detector.py
├── conocedor.py
├── captura.py
├── base_datos/
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/face-recognition-access-control.git
cd face-recognition-access-control
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install opencv-python
pip install numpy
pip install pillow
pip install mtcnn
pip install deepface
pip install tensorflow
pip install tf-keras
```

Or:

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

---

## 🖥️ Usage

### Available Controls

| Key | Action                   |
| --- | ------------------------ |
| R   | Register a new user      |
| E   | Delete a registered user |
| Q   | Exit the application     |

### User Registration Process

1. Press **R**
2. Enter the user's name
3. Confirm consent for facial data storage
4. The system automatically captures 20 facial images
5. Images are stored in the local database
6. The user becomes available for recognition

---

## ⚡ Performance Optimization

Facial recognition is computationally expensive. To improve responsiveness, the system does not execute recognition on every video frame.

Instead, identity analysis is performed periodically while the last detected identity is cached and displayed in real time. This reduces processing load while maintaining a smooth user experience.

---

## 👤 My Contribution

This was a collaborative academic project.

My primary contribution was the development of the graphical user interface (`interfaz.py`), including:

* User interaction workflows
* Access status visualization
* Registered user management
* Consent verification prompts
* Custom dashboard design
* Integration of the detection, recognition, and registration modules

I also contributed to the integration, testing, and refinement of other system components.

---

## 🔒 Ethical Considerations

This project was developed exclusively for educational purposes.

The system follows several ethical guidelines:

* Facial data is stored only with explicit user consent.
* Unknown individuals are not automatically registered.
* No continuous video recording is performed.
* The project is not intended for surveillance applications.
* The system serves as a learning platform for Computer Vision and Artificial Intelligence concepts.

---

## 🎥 Demo

### Authorized User

*Screenshot coming soon.*

### Unknown User

*Screenshot coming soon.*

### User Registration

*Screenshot coming soon.*

### System Dashboard

*Screenshot coming soon.*

---

## 🚀 Future Improvements

* [ ] Export recognition logs
* [ ] Multi-camera support
* [ ] User roles and permissions
* [ ] Improved recognition confidence analysis
* [ ] Cloud-based user database
* [ ] Web dashboard version
* [ ] Recognition statistics and analytics

---

## 📄 License

This project was developed for academic and educational purposes.
