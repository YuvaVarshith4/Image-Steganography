import cv2
import numpy as np
import os
import sys
from cryptography.fernet import Fernet

def text_to_binary(data: bytes) -> str:
    """Converts byte data to a continuous binary string."""
    return ''.join([format(byte, '08b') for byte in data])

def encrypt_and_hide(image_path: str, secret_message: str, output_path: str, key_path: str = "secret.key"):
    """Encrypts a message, hides it in an image's LSBs, and saves the encryption key."""
    
    # --- ERROR HANDLING: Input Validation ---
    if not os.path.exists(image_path):
        print(f"[-] Error: Original image '{image_path}' not found.")
        sys.exit(1)
        
    if not output_path.lower().endswith(('.png', '.bmp')):
        print("[-] Error: Output format must be lossless (.png or .bmp). JPEGs will destroy the hidden payload.")
        sys.exit(1)

    try:
        # 1. Generate and save the encryption key
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        print(f"[+] Encryption key saved to: {key_path}")

        # 2. Encrypt the message (Fernet uses AES-128 in CBC mode)
        f = Fernet(key)
        encrypted_bytes = f.encrypt(secret_message.encode())
        
        # 3. Add a delimiter for extraction
        delimiter = b'#####'
        data_to_hide = encrypted_bytes + delimiter
        binary_data = text_to_binary(data_to_hide)
        
        # 4. Load the image
        img = cv2.imread(image_path)
        if img is None:
            print(f"[-] Error: Unable to read '{image_path}'. File might be corrupted.")
            sys.exit(1)
            
        # --- ERROR HANDLING: Capacity Check ---
        max_bits = img.shape[0] * img.shape[1] * 3
        if len(binary_data) > max_bits:
            print(f"[-] Error: Payload is too large ({len(binary_data)} bits). Maximum capacity for this image is {max_bits} bits.")
            sys.exit(1)
            
        # 5. Hide the binary data in the Least Significant Bits (LSB)
        flat_img = img.flatten()
        for i in range(len(binary_data)):
            flat_img[i] = (flat_img[i] & ~1) | int(binary_data[i])
            
        # 6. Reshape and save the new image
        encoded_img = flat_img.reshape(img.shape)
        success = cv2.imwrite(output_path, encoded_img)
        
        if success:
            print(f"[+] Secret message successfully encoded and saved to: {output_path}")
        else:
            print(f"[-] Error: Failed to write to {output_path}. Check file permissions.")
            
    except PermissionError:
        print("[-] Error: Permission denied when trying to write files. Run with appropriate privileges.")
    except Exception as e:
        print(f"[-] An unexpected error occurred during encoding: {e}")

if __name__ == "__main__":
    # Setup your target files here
    input_image = "input.png"      
    output_image = "encoded.png"
    message = "This is a highly classified payload."

    encrypt_and_hide(input_image, message, output_image)
