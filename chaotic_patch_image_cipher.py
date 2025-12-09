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
    # Hash mật khẩu → 32 bytes (bảo đảm cố định)
    h = hashlib.sha256(password.encode()).digest()

    # Tạo seed cho logistic map (dựa trên 4 byte đầu)
    seed_int = int.from_bytes(h[0:4], "big")
    seed = (seed_int % 1_000_000) / 1_000_000

    # Tạo tham số r (mức độ hỗn loạn), dựa 1 byte của hash
    r = 3.8 + (h[4] / 255) * 0.19

    # Chọn patch size theo byte cuối → 8, 16, 32
    patch_choices = [8, 16, 32]
    patch_size = patch_choices[h[-1] % 3]

    # xor_key = toàn bộ 32 byte hash dùng làm key XOR
    xor_key = np.frombuffer(h, dtype=np.uint8)

    return seed, r, patch_size, xor_key


# =====================
# Chaotic map
# =====================

def logistic_map(seed, r, size):
    # Sinh dãy hỗn loạn logistic map kích thước size
    x = seed
    arr = np.zeros(size)
    for i in range(size):
        x = r * x * (1 - x)  # công thức logistic
        arr[i] = x
    return arr


# =====================
# Patchify tools
# =====================

def patchify(img, patch_size=16):
    # Chia ảnh thành các block patch_size x patch_size
    h, w, c = img.shape
    patches = (
        img.reshape(h // patch_size, patch_size, w // patch_size, patch_size, c)
           .swapaxes(1, 2)
           .reshape(-1, patch_size, patch_size, c)
    )
    return patches


def unpatchify(patches, img_shape, patch_size=16):
    # Ghép patch về lại thành ảnh hoàn chỉnh
    h, w, c = img_shape
    H, W = h // patch_size, w // patch_size
    patches = patches.reshape(H, W, patch_size, patch_size, c)
    img = patches.swapaxes(1, 2).reshape(h, w, c)
    return img


# =====================
# Encrypt / decrypt
# =====================

def encrypt_patches(img_array, password):
    # Lấy seed, r, patch size, XOR key từ mật khẩu
    seed, r, patch_size, xor_key = derive_keys(password)

    # Chia ảnh thành patch
    patches = patchify(img_array, patch_size)
    N = len(patches)

    # Tạo dãy hỗn loạn
    chaos = logistic_map(seed, r, N)

    # Tạo perm = thứ tự hoán vị patch
    perm = np.argsort(chaos)

    # chaos_vals = mỗi giá trị chaos chuyển thành 1 byte (0–255)
    chaos_vals = (chaos * 255).astype(np.uint8)

    encrypted = []
    for i in range(N):
        p = patches[i].astype(np.uint8)

        # key XOR = chaos_val XOR với 1 byte trong xor_key
        key = chaos_vals[i] ^ xor_key[i % len(xor_key)]

        # Mã hoá patch bằng XOR
        encrypted.append(p ^ key)

    # Hoán vị patch theo perm
    encrypted = np.stack(encrypted)[perm]

    # Ghép lại thành ảnh mã hoá
    return unpatchify(encrypted, img_array.shape, patch_size)


def decrypt_patches(img_array, password):
    # Tính lại key y như encrypt
    seed, r, patch_size, xor_key = derive_keys(password)
    patches = patchify(img_array, patch_size)
    N = len(patches)

    chaos = logistic_map(seed, r, N)
    perm = np.argsort(chaos)
    inv_perm = np.argsort(perm)   # đảo ngược perm để ghép đúng vị trí

    chaos_vals = (chaos * 255).astype(np.uint8)

    # Mảng rỗng chứa patch đã giải mã
    decrypted = np.zeros_like(patches)
    for i in range(N):
        # Lấy patch đúng thứ tự inverse permutation
        p = patches[inv_perm[i]].astype(np.uint8)

        # Tính lại key XOR như lúc encrypt
        key = chaos_vals[i] ^ xor_key[i % len(xor_key)]

        # Giải mã bằng XOR lại lần nữa
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

        # ---- Nút chọn ảnh ----
        btn_load = QPushButton("📁 Chọn ảnh")
        btn_load.clicked.connect(self.load_image)  # Gắn sự kiện click
        layout.addWidget(btn_load)

        # ---- Ô nhập mật khẩu ----
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("Nhập mật khẩu...")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pw_input)

        # ---- Chọn chế độ Encrypt/Decrypt ----
        self.mode = QComboBox()
        self.mode.addItems(["Encrypt", "Decrypt"])
        layout.addWidget(self.mode)

        # ---- Nút Run ----
        btn_run = QPushButton("▶️ Run")
        btn_run.clicked.connect(self.run_encrypt)
        layout.addWidget(btn_run)

        # ---- Khung preview input ----
        self.input_label = QLabel("Chưa có ảnh input")
        self.input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_label)

        # ---- Khung preview output ----
        self.output_label = QLabel("Output sẽ hiển thị ở đây")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.output_label)

        # ---- Nút lưu ảnh output ----
        btn_save = QPushButton("💾 Lưu ảnh output")
        btn_save.clicked.connect(self.save_output)
        layout.addWidget(btn_save)

        # Ảnh input / output
        self.img_array = None
        self.output_array = None

        self.setLayout(layout)

    # ---- Load image ----
    def load_image(self):
        # Mở file dialog
        path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Images (*.png *.jpg *.jpeg)")
        if not path:
            return

        # Load ảnh, convert RGB
        img = Image.open(path).convert("RGB")

        # Resize chuẩn 256x256
        img = img.resize((256, 256))

        # Convert thành numpy array
        self.img_array = np.array(img)

        # Hiển thị lên GUI
        self.show_image(self.img_array, self.input_label)

    # ---- Run encryption/decryption ----
    def run_encrypt(self):
        if self.img_array is None:
            return
        
        pw = self.pw_input.text()
        if len(pw) == 0:
            return

        # Chọn chế độ
        if self.mode.currentText() == "Encrypt":
            self.output_array = encrypt_patches(self.img_array, pw)
        else:
            self.output_array = decrypt_patches(self.img_array, pw)

        # Hiển thị output
        self.show_image(self.output_array, self.output_label)

    # ---- Hiển thị ảnh ----
    def show_image(self, img_array, label):
        h, w, c = img_array.shape
        
        # Convert numpy → QImage → QPixmap
        img = QImage(img_array.data, w, h, 3 * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)

        # Scale ảnh cho vừa khung
        label.setPixmap(pix.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio))

    # ---- Lưu ảnh output ----
    def save_output(self):
        if self.output_array is None:
            return
        
        # Mở hộp thoại lưu
        path, _ = QFileDialog.getSaveFileName(self, "Lưu ảnh", "", "PNG (*.png)")
        if path:
            Image.fromarray(self.output_array).save(path)


# =====================
# RUN APP
# =====================

app = QApplication(sys.argv)
win = App()     # Tạo cửa sổ chính
win.show()      # Hiển thị GUI
sys.exit(app.exec())   # Bắt đầu vòng lặp sự kiện