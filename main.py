from selenium import webdriver
from selenium.webdriver.common.by import By #by sınıfı web sayfasının içeriklerine ulaşabilmemiz için.
import sqlite3
#Gerekli kütüphanleri aktardık.

#selenium kullanarak chrome tarayıcısıyla siteyi açtık.
driver = webdriver.Chrome()


driver.get("https://www.arcelik.com.tr/turk-kahve-makinesi")
#Siteye ulaştık.
js_code ="""
        function closeCookiePopup() {
            var cookieAcceptButton = document.getElementById('onetrust-accept-btn-handler');
            if (cookieAcceptButton) {
                cookieAcceptButton.click();
            }
        }
        closeCookiePopup();"""
#Sayfa açıldığında çıkan pop-up' ı tıklayarak kapatan bir js kodu yazdık.
driver.execute_script(js_code)#Js kodunu çalıştırdık.
content = driver.find_element(By.CLASS_NAME, "productgridcomponent-page")
#Ürünleri bulundukları class ile seçtik
urun = content.find_elements(By.CLASS_NAME, "prd-inner")
#Her bir ürünün bulunduğu alanı seçtik.

urun_link= []
for sinif in urun:
        # her ürün için içerisindeki a etiketini bularak href içindeki linkleri çektik.
        try:
            a = sinif.find_element(By.TAG_NAME, "a")
            link = a.get_attribute("href")


            urun_link.append(link)
            # her sayfadaki linkleri toplayıp urun linkleri listesine ekledik.
        except:
            print("hata")



for i in urun_link:
    print(i)
#Tüm linkleri ekrana yazdırdık.
ad_mar_fiy=[]
özll=[]
yorum=[]
puan=[]
#Ürünün özelliklerini tutacak listeler oluşturduk.
for urun_id,i in enumerate(urun_link):
    driver.get(i)
    #Sayfayı açtık.
    driver.implicitly_wait(1)
    #Sayfanın yüklenmesini bekledik.
    try:

        urun_adi = driver.find_element(By.XPATH,"//*[@id=\"pdp-general\"]/div[3]/div[1]/div[1]/h1").text
        marka = "Arçelik"
        fiyat = driver.find_element(By.XPATH,"//*[@id=\"pdp-general\"]/div[3]/div[6]/div[2]/div[3]/div[1]/div/div[1]").text
        ozellikler = driver.find_element(By.XPATH,"//*[@id=\"pdp-general\"]/div[3]/div[11]/div[1]").text
        #Ürünün ilgili özelliğini bulunduğu yol ile çektik.
        bilgiler=[urun_adi, fiyat, marka]
        özellik=[ozellikler]
        ad_mar_fiy.append(bilgiler)
        özll.append(özellik)
        #Sonrasında kullanabilmek için oluşturduğumuz listelere özellikleri ekledik
        print(bilgiler)

        """button = driver.find_element(By.CLASS_NAME, "pdp-video active")
        if (button == True):
            button.click()"""#işe yaramadı.
        yorumbar=driver.find_element(By.CLASS_NAME,"qtyValue").click()
        #Tıklatarak yorumların olduğu kısmı aktif hale getirdik.
        yorumlar = driver.find_elements(By.CLASS_NAME, "rvw-item-text")

        ort_puan = driver.find_element(By.CLASS_NAME, "rvw-average").text
        print(ort_puan)
        puan.append(ort_puan)

        tarihler=driver.find_elements(By.CLASS_NAME,"rvw-item-date")
        tarihler_text=[tarih.text for tarih in tarihler ]

        yorumlar_text = [yorum.text for yorum in yorumlar]
        trh_yrm = list(zip(tarihler_text, yorumlar_text))
        #İki listeyi ikili olarak birleştirmek içim zip kullandık.
        print(trh_yrm)
        # Yorum olmayanlarda ve sayfada vvideo olanlarda hata veriyor.
        yorum.append(trh_yrm)



        print("-----------------------")


    except:

        print("hata")


driver.quit()
#Tarayıcıyı kapattık.


conn = sqlite3.connect("arcelik_kahve_makinesi2.db")
#Sqlite veritabanına bağlantı kurduk.
c = conn.cursor()
#Veritabanı üzerinde işlem yapabilmek için cursor oluşturduk.

c.execute("""
    CREATE TABLE IF NOT EXISTS urunler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urun_adi TEXT,
        fiyat REAL,
        marka TEXT
    )
""")


c.execute("""
    CREATE TABLE IF NOT EXISTS yorumlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        k_id INTEGER,
        date TEXT,
        comment TEXT
    )
""")
# Ürünlere ve yorumlara ait tabloyu oluşturduk.
conn.commit()
#Yapılanları kaydettik.
sayac = 0
for i in ad_mar_fiy:
    sayac += 1#Her bir ürünü sayabilmek için sayaç oluşturduk.
    c.execute("INSERT INTO urunler (urun_adi, fiyat, marka) VALUES (?, ?, ?)", (i[0], i[1], i[2]))
    #Bilgileri sql kodu ile veritabanına ekledik.
    conn.commit()

    for j in yorum:
        for k in list(j):
            #Tarih yorum ikilisini çektik
            date = k[0]
            comment = k[1]
            c.execute("INSERT INTO yorumlar (k_id, date, comment) VALUES (?, ?, ?)", (sayac, date, comment))
            #K_id ile ürün idleriyle ilişkilendirip yorum ve tarihleri ekledik.
            conn.commit()

conn.close()
#Veritabanı ile bağlantıyı sonlandırdık.
