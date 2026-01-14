
try:
    with open('assets/style.css', 'rb') as f:
        content = f.read()
        print(content.decode('utf-8', errors='ignore')[1000:3500])
except Exception as e:
    print(e)
