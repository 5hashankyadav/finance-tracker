import os

def check_files(directory):
    for root, dirs, files in os.walk(directory):
        if 'venv' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py') or file.endswith('.env'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f"NULL BYTE FOUND: {path}")
                        try:
                            content.decode('utf-8')
                        except UnicodeDecodeError:
                            print(f"INVALID UTF-8: {path}")
                except Exception as e:
                    print(f"ERROR READING: {path} - {e}")

if __name__ == "__main__":
    check_files('.')
