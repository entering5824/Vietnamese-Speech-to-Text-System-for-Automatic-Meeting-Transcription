import sys
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QHBoxLayout, QLineEdit, QComboBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import hashlib


# =====================
# Key Derivation
# =====================

def derive_keys(password: str):
    h = hashlib.sha256(password.encode()).digest()

    seed_int = int.from_bytes(h[0:4], "big")
    seed = (seed_int % 1_000_000) / 1_000_000

    r = 3.8 + (h[4] / 255) * 0.19

    patch_choices = [8, 16, 32]
    patch_size = patch_choices[h[-1] % 3]

    xor_key = np.frombuffer(h, dtype=np.uint8)

    return seed, r, patch_size, xor_key


# =====================
# Chaotic map
# =====================

def logistic_map(seed, r, size):
    x = seed
    arr = np.zeros(size)
    for i in range(size):
        x = r * x * (1 - x)
        arr[i] = x
    return arr


# =====================
# Patchify tools
# =====================

def patchify(img, patch_size=16):
    h, w, c = img.shape
    patches = (
        img.reshape(h // patch_size, patch_size, w // patch_size, patch_size, c)
           .swapaxes(1, 2)
           .reshape(-1, patch_size, patch_size, c)
    )
    return patches


def unpatchify(patches, img_shape, patch_size=16):
    h, w, c = img_shape
    H, W = h // patch_size, w // patch_size
    patches = patches.reshape(H, W, patch_size, patch_size, c)
    img = patches.swapaxes(1, 2).reshape(h, w, c)
    return img


# =====================
# Encrypt / decrypt
# =====================

def encrypt_patches(img_array, password):
    seed, r, patch_size, xor_key = derive_keys(password)
    patches = patchify(img_array, patch_size)
    N = len(patches)

    chaos = logistic_map(seed, r, N)
    perm = np.argsort(chaos)

    chaos_vals = (chaos * 255).astype(np.uint8)

    encrypted = []
    for i in range(N):
        p = patches[i].astype(np.uint8)
        key = chaos_vals[i] ^ xor_key[i % len(xor_key)]
        encrypted.append(p ^ key)

    encrypted = np.stack(encrypted)[perm]
    return unpatchify(encrypted, img_array.shape, patch_size)


def decrypt_patches(img_array, password):
    seed, r, patch_size, xor_key = derive_keys(password)
    patches = patchify(img_array, patch_size)
    N = len(patches)

    chaos = logistic_map(seed, r, N)
    perm = np.argsort(chaos)
    inv_perm = np.argsort(perm)

    chaos_vals = (chaos * 255).astype(np.uint8)

    decrypted = np.zeros_like(patches)
    for i in range(N):
        p = patches[inv_perm[i]].astype(np.uint8)
        key = chaos_vals[i] ^ xor_key[i % len(xor_key)]
        decrypted[i] = p ^ key

    return unpatchify(decrypted, img_array.shape, patch_size)



# =====================
# PyQt6 GUI
# =====================

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chaotic Patch Image Encryption (PyQt6)")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # ---- Buttons ----
        btn_load = QPushButton("📁 Chọn ảnh")
        btn_load.clicked.connect(self.load_image)
        layout.addWidget(btn_load)

        # ---- Password input ----
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("Nhập mật khẩu...")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pw_input)

        # ---- Mode select ----
        self.mode = QComboBox()
        self.mode.addItems(["Encrypt", "Decrypt"])
        layout.addWidget(self.mode)

        # ---- Run button ----
        btn_run = QPushButton("▶️ Run")
        btn_run.clicked.connect(self.run_encrypt)
        layout.addWidget(btn_run)

        # ---- Image preview ----
        self.input_label = QLabel("Chưa có ảnh input")
        self.input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_label)

        self.output_label = QLabel("Output sẽ hiển thị ở đây")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.output_label)

        # ---- Save button ----
        btn_save = QPushButton("💾 Lưu ảnh output")
        btn_save.clicked.connect(self.save_output)
        layout.addWidget(btn_save)

        self.img_array = None
        self.output_array = None

        self.setLayout(layout)

    # ---- Load image ----
    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Images (*.png *.jpg *.jpeg)")
        if not path:
            return

        img = Image.open(path).convert("RGB")
        img = img.resize((256, 256))
        self.img_array = np.array(img)

        self.show_image(self.img_array, self.input_label)

    # ---- Run encryption/decryption ----
    def run_encrypt(self):
        if self.img_array is None:
            return
        
        pw = self.pw_input.text()
        if len(pw) == 0:
            return

        if self.mode.currentText() == "Encrypt":
            self.output_array = encrypt_patches(self.img_array, pw)
        else:
            self.output_array = decrypt_patches(self.img_array, pw)

        self.show_image(self.output_array, self.output_label)

    # ---- Show image ----
    def show_image(self, img_array, label):
        h, w, c = img_array.shape
        img = QImage(img_array.data, w, h, 3 * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)
        label.setPixmap(pix.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio))

    # ---- Save output ----
    def save_output(self):
        if self.output_array is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Lưu ảnh", "", "PNG (*.png)")
        if path:
            Image.fromarray(self.output_array).save(path)


# =====================
# RUN APP
# =====================

app = QApplication(sys.argv)
win = App()
win.show()
sys.exit(app.exec())