import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet, InvalidToken

# ==========================================
# 1. Core Logic & Utilities
# ==========================================
def text_to_binary(data: bytes) -> str:
    return ''.join([format(byte, '08b') for byte in data])

def binary_to_bytes(binary_data: str) -> bytes:
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    return bytes([int(byte, 2) for byte in all_bytes])

# ==========================================
# 2. Tkinter GUI Application
# ==========================================
class SteganoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptographic LSB Steganography Tool")
        self.root.geometry("520x580")
        self.root.resizable(False, False)

        # Main Title
        tk.Label(root, text="Secure Image Steganography", font=("Helvetica", 16, "bold")).pack(pady=10)

        # --- ENCODE SECTION ---
        encode_frame = tk.LabelFrame(root, text="Inject Payload", padx=10, pady=10)
        encode_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(encode_frame, text="Secret Message:").pack(anchor="w")
        self.msg_entry = tk.Text(encode_frame, height=4, width=55)
        self.msg_entry.pack(pady=5)

        tk.Button(encode_frame, text="Select Image & Encode", command=self.handle_encode, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold")).pack(pady=5)

        # --- DECODE SECTION ---
        decode_frame = tk.LabelFrame(root, text="Extract Payload", padx=10, pady=10)
        decode_frame.pack(fill="x", padx=15, pady=15)

        tk.Button(decode_frame, text="Select Image & Key to Decode", command=self.handle_decode, bg="#2196F3", fg="white", font=("Helvetica", 10, "bold")).pack(pady=5)

        tk.Label(decode_frame, text="Extracted Message:").pack(anchor="w", pady=(10,0))
        self.result_text = tk.Text(decode_frame, height=5, width=55, state="disabled", bg="#f0f0f0")
        self.result_text.pack(pady=5)

    def handle_encode(self):
        secret_msg = self.msg_entry.get("1.0", tk.END).strip()
        if not secret_msg:
            messagebox.showwarning("Warning", "Please enter a message to hide.")
            return

        input_img = filedialog.askopenfilename(title="Select Original Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not input_img: return

        output_img = filedialog.asksaveasfilename(title="Save Encoded Image As", defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("BMP Files", "*.bmp")])
        if not output_img: return
        
        if not output_img.lower().endswith(('.png', '.bmp')):
            messagebox.showerror("Format Error", "Output format must be .png or .bmp to preserve the payload.")
            return

        key_path = filedialog.asksaveasfilename(title="Save Encryption Key As", defaultextension=".key", filetypes=[("Key Files", "*.key")])
        if not key_path: return

        # Encode Logic with GUI Error Handling
        try:
            key = Fernet.generate_key()
            with open(key_path, "wb") as key_file:
                key_file.write(key)

            f = Fernet(key)
            encrypted_bytes = f.encrypt(secret_msg.encode())
            
            delimiter = b'#####'
            data_to_hide = encrypted_bytes + delimiter
            binary_data = text_to_binary(data_to_hide)
            
            img = cv2.imread(input_img)
            if img is None:
                messagebox.showerror("File Error", "Unable to read the selected image.")
                return
                
            max_bits = img.shape[0] * img.shape[1] * 3
            if len(binary_data) > max_bits:
                messagebox.showerror("Capacity Error", f"Payload is too large. Max capacity: {max_bits} bits.")
                return
                
            flat_img = img.flatten()
            for i in range(len(binary_data)):
                flat_img[i] = (flat_img[i] & ~1) | int(binary_data[i])
                
            encoded_img = flat_img.reshape(img.shape)
            cv2.imwrite(output_img, encoded_img)
            
            messagebox.showinfo("Success", f"Payload successfully hidden!\nKey saved to: {os.path.basename(key_path)}")
            self.msg_entry.delete("1.0", tk.END)

        except PermissionError:
            messagebox.showerror("Permission Error", "Permission denied when saving files.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An error occurred: {str(e)}")

    def handle_decode(self):
        input_img = filedialog.askopenfilename(title="Select Encoded Image", filetypes=[("PNG Files", "*.png"), ("BMP Files", "*.bmp")])
        if not input_img: return

        key_path = filedialog.askopenfilename(title="Select Encryption Key", filetypes=[("Key Files", "*.key")])
        if not key_path: return

        # Decode Logic with GUI Error Handling
        try:
            with open(key_path, "rb") as key_file:
                key = key_file.read()

            img = cv2.imread(input_img)
            if img is None:
                messagebox.showerror("File Error", "Unable to read the selected image.")
                return
                
            flat_img = img.flatten()
            extracted_bits = [str(pixel & 1) for pixel in flat_img]
            binary_string = "".join(extracted_bits)
            
            extracted_bytes = binary_to_bytes(binary_string)
            delimiter = b'#####'
            delimiter_index = extracted_bytes.find(delimiter)
            
            if delimiter_index == -1:
                messagebox.showerror("Payload Error", "No delimiter found. Image is corrupted or contains no payload.")
                return
                
            encrypted_message = extracted_bytes[:delimiter_index]
            f = Fernet(key)
            decrypted_msg = f.decrypt(encrypted_message).decode()
            
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, decrypted_msg)
            self.result_text.config(state="disabled")
            
            messagebox.showinfo("Success", "Payload extracted and decrypted successfully!")

        except InvalidToken:
            messagebox.showerror("Decryption Error", "Invalid Key. The key does not match the encrypted payload.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganoApp(root)
    root.mainloop()
