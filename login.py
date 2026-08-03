from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Buka browser secara fisik agar Anda bisa login manual
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.tiktok.com/login")
    
    print("Silakan login ke akun TikTok Anda di browser yang terbuka...")
    print("Setelah berhasil login dan masuk ke halaman utama, kembali ke terminal ini dan tekan Enter.")
    input("Tekan Enter jika sudah berhasil login...")
    
    # Menyimpan status login (termasuk semua cookies) ke file auth.json
    context.storage_state(path="auth.json")
    print("Sesi login berhasil disimpan ke file auth.json!")
    browser.close()
