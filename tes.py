import time
import pytz
import sys
import random
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# ==================== CONFIGURATION ====================
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# 📝 Daftar nama tampilan teman Anda
DAFTAR_TEMAN = [
    "Yann",
    "hottest إلمو",
    "Z",
    "n",
    "chell"
]

# 💬 Variasi pesan streak harian
DAFTAR_PESAN = [
    "🔥🔥🔥🔥",
]
# =======================================================

def kirim_lewat_inbox(): 
    waktu_log = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
    print(f"[{waktu_log}] Memulai browser otomatis (Metode Klik Kontak Sidebar)...")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--ignore-certificate-errors",
                    "--disable-gpu"
                ]
            )
            
            try:
                context = browser.new_context(
                    storage_state="auth.json",
                    user_agent=USER_AGENT,
                    viewport={'width': 1920, 'height': 1080},
                    locale="id-ID",
                    timezone_id="Asia/Jakarta"
                )
                print(f"[{waktu_log}] Berhasil memuat status login dari 'auth.json'.")
            except Exception as state_err:
                print(f"[{waktu_log}] GAGAL memuat 'auth.json': {state_err}")
                browser.close()
                return

            page = context.new_page()
            
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
            """)

            print(f"[{waktu_log}] Membuka halaman Kotak Masuk Utama...")
            page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded", timeout=60000)
            
            # Tunggu render list chat stabil
            page.wait_for_timeout(10000)  

            # 🔥 HAPUS TOMBOL "POSTING VIDEO" YANG MENGGANGU KLIK NAVIGASI
            print(f"[{waktu_log}] Membersihkan overlay tombol 'Posting video' jika ada...")
            page.evaluate("""() => {
                const badges = Array.from(document.querySelectorAll('div, button, a'));
                const targetBadge = badges.find(el => el.textContent.includes('Posting video'));
                if (targetBadge) {
                    const floatingContainer = targetBadge.closest('[class*="DivFloating"], [class*="Bubble"]') || targetBadge;
                    floatingContainer.remove();
                    console.log("Tombol 'Posting video' berhasil dihapus!");
                }
            }""")
            page.wait_for_timeout(2000)

            # Memproses teman berdasarkan navigasi elemen list chat
            for target_user in DAFTAR_TEMAN:
                waktu_skrg = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
                print(f"[{waktu_skrg}] --------------------------------------------------")
                print(f"[{waktu_skrg}] Memulai proses navigasi untuk: '{target_user}'")
                
                try:
                    chat_item = None
                    
                    # 🔥 FIX 1: Gunakan Regex Exact Match (^nama$) agar "Z" tidak salah pilih "L A 4 5 Z"
                    exact_pattern = re.compile(rf"^{re.escape(target_user)}$")
                    
                    # 🔥 FIX 2: Auto-Scroll Sidebar jika kontak berada jauh di bawah
                    print(f"[{waktu_skrg}] Mencari kontak '{target_user}' (dengan Auto-Scroll)...")
                    
                    for scroll_attempt in range(12): # Maksimal scroll ke bawah 12 kali
                        # Cari elemen span/div/p yang teksnya 100% SAMA PERSIS
                        candidates = page.locator("span, p, div").filter(has_text=exact_pattern)
                        
                        count = candidates.count()
                        for i in range(count):
                            el = candidates.nth(i)
                            try:
                                if el.is_visible():
                                    chat_item = el
                                    break
                            except:
                                continue
                        
                        if chat_item:
                            print(f"[{waktu_skrg}] Menemukan elemen kontak '{target_user}'!")
                            break
                        
                        # Arahkan kursor ke area sidebar chat lalu scroll ke bawah
                        page.mouse.move(200, 400)
                        page.mouse.wheel(0, 400)
                        page.wait_for_timeout(600)

                    if chat_item:
                        # Posisikan layar ke elemen tersebut
                        chat_item.scroll_into_view_if_needed()
                        page.wait_for_timeout(500)
                        
                        # Berikan fokus dan klik langsung ke teks tersebut
                        chat_item.focus()
                        page.wait_for_timeout(300)
                        chat_item.click(force=True)
                        page.wait_for_timeout(500)
                        
                        # Simulasikan Enter sebagai pengaman navigasi
                        page.keyboard.press("Enter")
                        print(f"[{waktu_skrg}] Trigger click & Enter dikirim ke '{target_user}'.")
                        
                        # Tunggu render obrolan kanan
                        page.wait_for_timeout(5000)
                        print(f"[{waktu_skrg}] DEBUG URL saat ini: -> {page.url}")

                        # Cari kotak ketik chat
                        chat_box = None
                        selectors_chat = [
                            'div[contenteditable="true"]',
                            'textarea',
                            'div[role="textbox"]',
                            'p[placeholder*="Kirim"]',
                            'p[placeholder*="Send"]',
                            'main div[contenteditable="true"]'
                        ]

                        for sel in selectors_chat:
                            el = page.locator(sel).first
                            try:
                                if el.is_visible(timeout=1500):
                                    chat_box = el
                                    print(f"[{waktu_skrg}] Menemukan elemen input chat dengan selector: '{sel}'")
                                    break
                            except:
                                continue

                        if chat_box:
                            pesan_acak = random.choice(DAFTAR_PESAN)
                            
                            # Klik chat box agar kursor aktif di dalamnya
                            chat_box.focus()
                            chat_box.click(force=True)
                            page.wait_for_timeout(1000)
                            
                            # Isi pesan dan kirim
                            chat_box.fill("")
                            chat_box.fill(pesan_acak)
                            page.wait_for_timeout(1000)
                            chat_box.press("Enter")
                            print(f"[{waktu_skrg}] SUKSES: Streak terkirim ke {target_user} -> '{pesan_acak}'")
                        else:
                            waktu_gagal = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
                            print(f"[{waktu_gagal}] GAGAL: Kolom ketik chat tidak ditemukan di sebelah kanan.")
                            page.screenshot(path=f"gagal_{target_user}.png")
                    else:
                        print(f"[{waktu_skrg}] TERSKIP: Kontak '{target_user}' tidak ditemukan setelah di-scroll.")
                        page.screenshot(path=f"missing_{target_user}.png")
                
                except Exception as user_err:
                    print(f"[{waktu_skrg}] GAGAL memproses {target_user}: {user_err}")
                    continue

                page.wait_for_timeout(3000)

            print(f"[{datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')}] Semua proses pengiriman selesai.")
            browser.close()

        except Exception as e:
            print(f"[{datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')}] ERROR UTAMA: {e}")

if __name__ == "__main__":
    kirim_lewat_inbox()
    sys.exit(0)
