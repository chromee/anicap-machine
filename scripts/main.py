from scripts.capraping import CapScraper
from scripts.cap_manager import CapManager

## Windows用
# cap_dir = r"D:¥cap2"
# face_dir = r"D:¥cap2¥_face"

# Mac用
cap_dir = r"/Users/denx_mac/Projects/anicap-machine/data/cap"
face_dir = r"/Users/denx_mac/Projects/anicap-machine/data/face"

scraper = CapScraper(0, 1, cap_dir)
scraper.execute()

cap_m = CapManager(cap_dir, face_dir)
cap_m.extract_face_and_save()
