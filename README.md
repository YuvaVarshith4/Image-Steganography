# 🔐 Secure Image Steganography (Cryptographic LSB)

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![Cryptography](https://img.shields.io/badge/Cryptography-Fernet-red.svg)

A robust Python-based steganography tool that securely hides encrypted payloads within the **Least Significant Bits (LSB)** of an image.

Unlike traditional steganography systems that store plain text, this project implements a **two-layer security mechanism**:
- Encrypt the message using **Fernet (AES-128 in CBC mode)**
- Embed the encrypted payload into image pixel data using LSB encoding

---

## 🚀 Features

- 🔐 **Two-Layer Security**
  - Encryption + Steganography
  - Payload remains unreadable without the cryptographic key

- 🖼️ **Lossless Data Embedding**
  - LSB manipulation ensures minimal visual distortion
  - Maintains image quality and integrity

- 💻 **Dual Interface Support**
  - **CLI Tools** for automation (`encrypt_hide.py`, `extract_decrypt.py`)
  - **GUI Application** using Tkinter (`stegano_gui.py`)

- ⚙️ **Efficient Processing**
  - Uses NumPy-based vectorized operations for faster pixel manipulation

- 🛡️ **Robust Error Handling**
  - Detects insufficient image capacity
  - Handles missing/corrupt key files
  - Prevents invalid file formats

---

## 🛠️ Tech Stack

- Python
- OpenCV
- NumPy
- Cryptography (Fernet)
- Tkinter (GUI)

---

## 📦 Installation

Make sure Python 3.8+ is installed.

```bash
pip install opencv-python numpy cryptography
