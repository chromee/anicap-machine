from capraping import CapScraper
from cap_manager import CapManager

cap_dir = r"D:\cap2"

scraper = CapScraper(200, 200, 0, 1, cap_dir)
scraper.execute()

# cap_m = CapManager(cap_dir)
# cap_m.extract_face_and_save()