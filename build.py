import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',  # Измените на актуальное имя вашего основного скрипта
    '--onefile',
    '--windowed',  # если не хотите консольного окна
    '--icon=icon.ico',
])
