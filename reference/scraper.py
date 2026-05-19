# Import libraries
import time
import random
import json
import os
import hashlib
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent

# Undetected ChromeDriver
try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    from webdriver_manager.chrome import ChromeDriverManager

class SeleniumUtils:
    """Utilities untuk simulasi human behavior"""
    @staticmethod
    def random_delay(min_sec=2, max_sec=5):
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def smooth_scroll(driver, scroll_pause=1.0, max_scrolls=10):
        """Scroll halaman ke bawah untuk load infinite scroll"""
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Coba scroll sedikit ke atas lalu ke bawah lagi (trigger trigger)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 200);")
                time.sleep(0.5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
            
            last_height = new_height
            scrolls += 1
            print(f"    ⬇️ Scrolling... ({scrolls}/{max_scrolls})")

class EnhancedChromeDriver:
    """Setup Driver"""
    def __init__(self, headless=False):
        self.headless = headless

    def create_driver(self):
        print("🚀 Initializing Chrome Driver...")
        if UNDETECTED_AVAILABLE:
            options = uc.ChromeOptions()
            if self.headless: options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-blink-features=AutomationControlled')
            driver = uc.Chrome(options=options, version_main=147)
        else:
            options = Options()
            if self.headless: options.add_argument('--headless=new')
            options.add_argument(f'user-agent={UserAgent().random}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        
        driver.set_window_size(1366, 768)
        return driver

class Liputan6Scraper:
    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://www.liputan6.com"
        
    def get_category_url(self, category):
        """Mapping kategori ke URL Liputan6"""
        # Mapping khusus jika nama kategori berbeda dengan URL path
        mapping = {
            'saham': 'saham',
            'bisnis': 'bisnis',
            'crypto': 'crypto',
            'tekno': 'tekno',
            'properti': 'properti',
            'bank': 'bank',
            'ekonomi': 'ekonomi'
        }
        path = mapping.get(category.lower(), category.lower())
        return f"{self.base_url}/{path}"

    def scrape_category_list(self, category, max_articles=20):
        """Scrape daftar artikel dari halaman kategori"""
        url = self.get_category_url(category)
        print(f"\n📂 Mengakses Kategori: {category.upper()} -> {url}")
        
        self.driver.get(url)
        SeleniumUtils.random_delay(3, 5)
        
        # Scroll untuk load lebih banyak artikel
        scroll_needed = max_articles // 5  # Asumsi 1 scroll load 5-10 artikel
        SeleniumUtils.smooth_scroll(self.driver, max_scrolls=scroll_needed)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        articles_data = []
        
        # Selector Liputan6 (Perlu disesuaikan jika layout web berubah)
        # Mencari container artikel umum
        article_elements = soup.find_all('article', class_=lambda x: x and 'articles--iridescent-list--item' in x)
        
        # Fallback jika class di atas tidak ketemu (layout berbeda per kategori)
        if not article_elements:
            article_elements = soup.find_all('div', class_='articles--iridescent-list--text-item')

        print(f"    🔍 Ditemukan {len(article_elements)} potensi artikel di halaman list.")

        count = 0
        seen_urls = set()

        for el in article_elements:
            if count >= max_articles: break
            
            try:
                # Mencari link dan judul
                link_tag = el.find('a', href=True)
                if not link_tag: continue
                
                url = link_tag['href']
                title = link_tag.get('title') or " ".join(link_tag.get_text().split())
                
                # Validasi URL
                if not url.startswith('http'): 
                    continue # Skip link internal relatif/iklan
                    
                if url in seen_urls: continue
                
                seen_urls.add(url)
                
                articles_data.append({
                    'url': url,
                    'title': title,
                    'category': category,
                    'scraped_at': datetime.now().isoformat()
                })
                count += 1
                
            except Exception as e:
                continue
                
        return articles_data

    # def get_article_content(self, url):
    #     """Mengambil isi berita full text"""
    #     try:
    #         print(f"    📖 Membaca: {url[:50]}...")
    #         self.driver.get(url + "?page=all") # Trik: coba ambil mode 'all page' jika ada
    #         SeleniumUtils.random_delay(2, 4)
            
    #         soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
    #         # 1. Judul
    #         title_elem = soup.find('h1', class_='read-page--header--title')
    #         title = title_elem.get_text(strip=True) if title_elem else ""
            
    #         # 2. Tanggal
    #         date_elem = soup.find('p', class_='read-page--header--author__datetime')
    #         date = date_elem.get_text(strip=True) if date_elem else ""
            
    #         # 3. Author
    #         author_elem = soup.find('span', class_='read-page--header--author__name')
    #         author = author_elem.get_text(strip=True) if author_elem else ""
            
    #         # 4. Konten (Pembersihan Noise)
    #         content_div = soup.find('div', class_='article-content-body__item-content')
            
    #         if not content_div:
    #             # Fallback selector
    #             content_div = soup.find('div', class_='article-content-body')
            
    #         clean_content = ""
    #         if content_div:
    #             # Hapus elemen pengganggu: Baca Juga, Video, Iklan
    #             for unwanted in content_div.find_all(['div', 'script', 'iframe', 'style']):
    #                 unwanted.decompose()
                
    #             # Hapus paragraf yang mengandung kata "Baca Juga" atau "Simak Video"
    #             paragraphs = []
    #             for p in content_div.find_all('p'):
    #                 text = p.get_text(strip=True)
    #                 lower_text = text.lower()
    #                 if "baca juga" in lower_text or "saksikan video" in lower_text:
    #                     continue
    #                 if len(text) < 20: # Skip paragraf terlalu pendek (biasanya caption foto salah parse)
    #                     continue
    #                 paragraphs.append(text)
                
    #             clean_content = " ".join(paragraphs)
            
    #         # Validasi konten kosong
    #         if not clean_content:
    #             return None

    #         return {
    #             'title': title,
    #             'date': date,
    #             'author': author,
    #             'content': clean_content
    #         }
            
    #     except Exception as e:
    #         print(f"    ❌ Gagal ambil konten: {e}")
    #         return None
    def get_article_content(self, url):
        try:
            # FORCE ALL PAGE MODE
            if "?page=all" not in url:
                target_url = url + "?page=all"
            else:
                target_url = url

            print(f"    📖 Membaca (Full Page): {target_url[:60]}...")
            self.driver.get(target_url)
            
            # Tunggu elemen body muncul
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "article-content-body"))
                )
            except:
                print("    ⚠️ Timeout waiting for body")
            
            # Scroll pelan-pelan ke bawah untuk trigger lazy load gambar/teks
            SeleniumUtils.smooth_scroll(self.driver, max_scrolls=5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 1. Ambil Metadata
            title = soup.find('h1', class_='read-page--header--title')
            title = " ".join(title.get_text().split()) if title else ""
            
            date_elem = soup.find('p', class_='read-page--header--author__datetime')
            date = " ".join(date_elem.get_text().split()) if date_elem else ""
            
            author_elem = soup.find('span', class_='read-page--header--author__name')
            author = " ".join(author_elem.get_text().split()) if author_elem else ""
            
           
            content_divs = soup.find_all('div', class_='article-content-body__item-content')
            
            if not content_divs:
                # Fallback jika struktur beda
                content_divs = soup.find_all('div', class_='article-content-body')

            full_text_parts = []
            
            for div in content_divs:
                # Bersihkan elemen pengganggu DI DALAM setiap div
                for unwanted in div.find_all(['script', 'iframe', 'style', 'div']):
                    # Hapus div iklan di dalam teks (biasanya class 'baca-juga' atau 'advertisement')
                    unwanted.decompose()
                
                # Ambil semua paragraf
                paragraphs = div.find_all('p')
                for p in paragraphs:
                    text = " ".join(p.get_text().split())
                    # Filter kasar di awal
                    if len(text) > 10: 
                        full_text_parts.append(text)
            
            clean_content = " ".join(full_text_parts)
            
            if not clean_content:
                return None

            return {
                'title': title,
                'date': date,
                'author': author,
                'content': clean_content
            }
            
        except Exception as e:
            print(f"    ❌ Gagal ambil konten: {e}")
            return None
            
class DatasetManager:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        
    def save_article(self, article_data):
        """Menyimpan artikel sebagai file JSON individu sesuai struktur README"""
        category = article_data['category']
        
        # Struktur folder: data/raw/liputan6/saham/
        dir_path = os.path.join(self.base_dir, 'raw', 'liputan6', category)
        os.makedirs(dir_path, exist_ok=True)
        
        # Buat nama file unik berdasarkan hash URL
        url_hash = hashlib.md5(article_data['url'].encode()).hexdigest()[:10]
        filename = f"{url_hash}.json"
        filepath = os.path.join(dir_path, filename)
        
        # Format sesuai README.md user
        final_data = {
            "url": article_data['url'],
            "title": article_data.get('title', ''),
            "content": article_data.get('content', ''),
            "category": category,
            "date": article_data.get('date', ''),
            "author": article_data.get('author', ''),
            "scraped_at": article_data.get('scraped_at', ''),
            "tags": [] # Placeholder jika ingin tambah tag nanti
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        return filepath

# ================= MAIN EXECUTION =================
def main():
    print("="*60)
    print("  LIPUTAN6 MULTI-DOC DATASET COLLECTOR")
    print("="*60)
    
    # Kategori target (sesuaikan dengan URL liputan6)
    TARGET_CATEGORIES = ['tekno', 'crypto',  'bola', 'otomotif', 'health', 'saham', 'bisnis']
    ARTICLES_PER_CATEGORY = 50 # Target per kategori
    BATCH_SIZE = 10
    
    driver_manager = EnhancedChromeDriver(headless=False)
    driver = driver_manager.create_driver()
    scraper = Liputan6Scraper(driver)
    data_manager = DatasetManager()
    
    total_saved = 0
    
    try:
        for category in TARGET_CATEGORIES:
            print(f"\n🔄 Memproses Kategori: {category}")
            
            # 1. Dapatkan List URL dulu (ini jarang error)
            try:
                articles_list = scraper.scrape_category_list(category, max_articles=ARTICLES_PER_CATEGORY)
            except Exception as e:
                print(f"    ❌ Gagal ambil list kategori {category}: {e}")
                continue
                
            print(f"    📋 Mendapatkan {len(articles_list)} URL. Mulai download konten...")
            
            # 2. Download Konten per URL dengan Batching
            for idx, item in enumerate(articles_list, 1):
                
                # --- LOGIKA RESTART DRIVER (BATCHING) ---
                if idx > 1 and idx % BATCH_SIZE == 1:
                    print(f"\n    ☕ Istirahat sejenak & Restart Driver (Batch {BATCH_SIZE})...")
                    try:
                        driver.quit() # Matikan browser lama
                        time.sleep(5) # Jeda nafas
                        driver = driver_manager.create_driver() # Buka browser baru
                        scraper.driver = driver # Update driver di object scraper
                        print("    ✅ Driver berhasil direfresh!\n")
                    except Exception as e:
                        print(f"    ⚠️ Gagal restart driver: {e}")
                # ----------------------------------------

                # Proses download artikel
                full_data = scraper.get_article_content(item['url'])
                
                if full_data:
                    item.update(full_data)
                    filepath = data_manager.save_article(item)
                    print(f"    ✅ ({idx}/{len(articles_list)}) Tersimpan: {filepath}")
                    total_saved += 1
                else:
                    print(f"    ⚠️ ({idx}/{len(articles_list)}) Skip (Gagal ambil konten)")
                
                # Jeda antar artikel (Random delay kecil)
                SeleniumUtils.random_delay(2, 5)
                
            print(f"    🎉 Selesai kategori {category}")
            
            # Istirahat panjang antar kategori
            print("    zzz... Istirahat panjang sebelum kategori selanjutnya...")
            time.sleep(10)
            
    except Exception as e:
        print(f"❌ Error Utama: {e}")
            
    finally:
        if driver:
            driver.quit()
        print("\n" + "="*60)
        print(f"🏁 SCRAPING SELESAI. Total Artikel: {total_saved}")
        print("📁 Cek folder 'data/raw/liputan6/'")

if __name__ == "__main__":
    main()