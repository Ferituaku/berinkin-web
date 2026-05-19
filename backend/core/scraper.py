import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

class SeleniumUtils:
    @staticmethod
    def random_delay(min_sec=2, max_sec=4):
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def smooth_scroll(driver, scroll_pause=1.0, max_scrolls=5):
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 200);")
                time.sleep(0.5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
            last_height = new_height
            scrolls += 1

class EnhancedChromeDriver:
    def __init__(self, headless=True):
        self.headless = headless

    def create_driver(self):
        if UNDETECTED_AVAILABLE:
            options = uc.ChromeOptions()
            if self.headless: options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-blink-features=AutomationControlled')
            # Adjust version_main if necessary based on local Chrome
            driver = uc.Chrome(options=options, version_main=147)
        else:
            options = Options()
            if self.headless: options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-blink-features=AutomationControlled')
            driver = webdriver.Chrome(options=options)
        
        driver.set_window_size(1366, 768)
        return driver

class Liputan6Scraper:
    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://www.liputan6.com"
        
    def get_category_url(self, category):
        mapping = {
            'saham': 'saham',
            'bisnis': 'bisnis',
            'crypto': 'crypto',
            'tekno': 'tekno',
            'otomotif': 'otomotif',
            'health': 'health',
            'bola': 'bola'
        }
        path = mapping.get(category.lower(), category.lower())
        return f"{self.base_url}/{path}"

    def scrape_category_list(self, category, target_date=None, max_articles=15):
        base_url_for_scrape = ""
        is_index = False
        
        if target_date:
            try:
                date_obj = datetime.strptime(target_date, "%Y-%m-%d")
                year, month, day = date_obj.strftime("%Y"), date_obj.strftime("%m"), date_obj.strftime("%d")
                mapping = {
                    'saham': 'saham',
                    'bisnis': 'bisnis',
                    'crypto': 'crypto',
                    'tekno': 'tekno',
                    'otomotif': 'otomotif',
                    'health': 'health',
                    'bola': 'bola'
                }
                path = mapping.get(category.lower(), category.lower())
                base_url_for_scrape = f"{self.base_url}/{path}/indeks/{year}/{month}/{day}"
                is_index = True
            except Exception:
                base_url_for_scrape = self.get_category_url(category)
        else:
            base_url_for_scrape = self.get_category_url(category)
            
        articles_data = []
        seen_urls = set()
        
        page = 1
        while len(articles_data) < max_articles:
            if is_index:
                url = f"{base_url_for_scrape}?page={page}"
                print(f"[Liputan6Scraper] Accessing index page {page}: {url}")
            else:
                if page > 1:
                    break # Normal category relies on scroll
                url = base_url_for_scrape
                print(f"[Liputan6Scraper] Accessing normal category: {url}")
            
            self.driver.get(url)
            SeleniumUtils.random_delay(2, 4)
            
            if not is_index:
                needed_scrolls = max(3, max_articles // 5)
                SeleniumUtils.smooth_scroll(self.driver, max_scrolls=needed_scrolls)
                
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            article_elements = soup.find_all('article', class_=lambda x: x and ('articles--iridescent-list--item' in x or 'articles--rows--item' in x))
            if not article_elements:
                article_elements = soup.find_all('div', class_='articles--iridescent-list--text-item')
                
            if not article_elements:
                print(f"[Liputan6Scraper] No more article elements found on page {page}.")
                break # No more articles
                
            initial_count = len(articles_data)
            
            for el in article_elements:
                if len(articles_data) >= max_articles: break
                try:
                    link_tag = el.find('a', href=True)
                    if not link_tag: continue
                    article_url = link_tag['href']
                    title = link_tag.get('title') or " ".join(link_tag.get_text(separator=' ', strip=True).split())
                    if "top 3" in title.lower(): continue
                    if not article_url.startswith('http'): continue
                    if article_url in seen_urls: continue
                    
                    seen_urls.add(article_url)
                    articles_data.append({
                        'url': article_url,
                        'title': title,
                        'category': category,
                        'scraped_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    continue
                    
            if len(articles_data) == initial_count:
                break
                
            if not is_index:
                break
                
            page += 1
                
        return articles_data

    def get_article_content(self, url):
        try:
            self.driver.get(url + "?page=all")
            SeleniumUtils.random_delay(1, 3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 1. Judul
            title_elem = soup.find('h1', class_='read-page--header--title')
            title = title_elem.get_text(separator=' ', strip=True) if title_elem else ""
            
            # 2. Tanggal
            date_elem = soup.find('p', class_='read-page--header--author__datetime')
            date = date_elem.get_text(separator=' ', strip=True) if date_elem else ""
            
            # 4. Konten - Grab all content bodies to avoid missing paragraphs
            content_divs = soup.find_all('div', class_=lambda x: x and 'article-content-body' in x)
            
            valid_p = []
            for div in content_divs:
                # Remove noise
                for unwanted in div.find_all(['script', 'iframe', 'style', 'figure']):
                    unwanted.decompose()
                
                # Get paragraphs and inner divs
                paragraphs = div.find_all(['p', 'div'])
                for p in paragraphs:
                    text = p.get_text(separator=' ', strip=True)
                    if not text: continue
                    if any(noise in text for noise in ["Baca Juga", "Simak Video", "BACA JUGA", "Saksikan video", "ADVERTISEMENT"]):
                        continue
                    if len(text) > 30 and text not in valid_p:
                        valid_p.append(text)
                
            clean_content = " ".join(valid_p)
                
            return {
                "title": title,
                "date": date,
                "content": clean_content
            }
        except Exception as e:
            return None

def scrape_articles_pipeline_generator(category: str, target_date: str, max_items=10):
    """
    Generator pipeline to scrape articles and yield progress.
    """
    driver_manager = EnhancedChromeDriver(headless=True)
    driver = None
    try:
        yield {"progress": 5, "message": "Memulai Chrome Driver..."}
        driver = driver_manager.create_driver()
        scraper = Liputan6Scraper(driver)
        
        yield {"progress": 10, "message": f"Mencari daftar berita {category}..."}
        articles = scraper.scrape_category_list(category, target_date=target_date, max_articles=max_items)
        
        results = []
        total = len(articles)
        if total == 0:
            yield {"progress": 30, "message": "Tidak ada artikel ditemukan.", "results": []}
            return
            
        if total < max_items:
            yield {"progress": 15, "message": f"Hanya ditemukan {total} artikel dari target {max_items}. Melanjutkan proses..."}

        for i, art in enumerate(articles):
            perc = int(10 + (25 * (i / total)))
            yield {"progress": perc, "message": f"Mengekstrak teks artikel {i+1} dari {total}..."}
            detail = scraper.get_article_content(art['url'])
            if detail and detail['content'] and len(detail['content']) > 200:
                results.append({
                    'url': art['url'],
                    'title': detail['title'] or art['title'],
                    'content': detail['content'],
                    'category': category,
                    'date': detail['date'] or target_date
                })
        
        yield {"progress": 35, "message": "Scraping selesai.", "results": results}
    except Exception as e:
        yield {"progress": 35, "message": f"Scraping error: {e}", "results": []}
    finally:
        if driver:
            driver.quit()
