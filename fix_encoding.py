
import os

file_path = 'assets/style.css'

try:
    with open(file_path, 'rb') as f:
        content = f.read()

    # Heuristic detection: if lots of null bytes, it's probably UTF-16
    if b'\x00' in content:
        print("Detected null bytes, attempting to convert from UTF-16 to UTF-8...")
        # decode
        text = content.decode('utf-16') if content.startswith(b'\xff\xfe') or content.startswith(b'\xfe\xff') else content.decode('utf-16') 
        # Actually standard windows notepad saves as utf-16 le (ff fe)
        # But if we just see nulls, we can try utf-16
        
        # However, it might be that the file is just mixed or has some issues.
        # Let's try simple decoding
        try:
            text = content.decode('utf-16')
        except:
             # Fallback: remove nulls if it's "fake" utf-16 (ascii with nulls)
             text = content.replace(b'\x00', b'').decode('utf-8')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Converted to UTF-8 successfully.")
    else:
        print("File seems to be valid, no null bytes density detected.")

except Exception as e:
    print(f"Error: {e}")
