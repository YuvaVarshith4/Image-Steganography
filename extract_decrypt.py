import cv2
import numpy as np
import os
import sys
from cryptography.fernet import Fernet, InvalidToken

def binary_to_bytes(binary_data: str) -> bytes:
    """Converts a binary string back into bytes."""
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    return bytes([int(byte, 2) for byte in all_bytes])

def extract_and_decrypt(image_path: str, key_path: str = "secret.key"):
    """Extracts LSB data from an image and decrypts it using the saved key."""
    
    # --- ERROR HANDLING: Input Validation ---
    if not os.path.exists(image_path):
        print(f"[-] Error: Encoded image '{image_path}' not found.")
        sys.exit(1)
        
    if not os.path.exists(key_path):
        print(f"[-] Error: Key file '{key_path}' not found. Cannot decrypt the payload.")
        sys.exit(1)

    try:
        # 1. Load the encryption key
        with open(key_path, "rb") as key_file:
            key = key_file.read()

        # 2. Load the encoded image
        img = cv2.imread(image_path)
        if img is None:
            print(f"[-] Error: Unable to read '{image_path}'. File might be corrupted.")
            sys.exit(1)
            
        # 3. Extract all Least Significant Bits (LSB)
        flat_img = img.flatten()
        extracted_bits = [str(pixel & 1) for pixel in flat_img]
        binary_string = "".join(extracted_bits)
        
        # 4. Convert bits to bytes
        extracted_bytes = binary_to_bytes(binary_string)
        
        # 5. Locate the delimiter
        delimiter = b'#####'
        delimiter_index = extracted_bytes.find(delimiter)
        
        # --- ERROR HANDLING: Delimiter Check ---
        if delimiter_index == -1:
            print("[-] Error: No delimiter found. The image does not contain a valid payload, or the LSBs were corrupted (e.g., via JPG compression).")
            sys.exit(1)
            
        encrypted_message = extracted_bytes[:delimiter_index]
        
        # 6. Decrypt the isolated message
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message).decode()
        print(f"\n[+] SUCCESS! Extracted Message:\n------------------------------\n{decrypted_message}\n------------------------------\n")
        return decrypted_message

    except InvalidToken:
        print("[-] Decryption failed: Invalid Key. The key does not match the encrypted payload.")
    except PermissionError:
        print("[-] Error: Permission denied when trying to read files.")
    except Exception as e:
        print(f"[-] An unexpected error occurred during extraction: {e}")

if __name__ == "__main__":
    # Setup your target files here
    target_image = "encoded.png"

    extract_and_decrypt(target_image)
