import sys
import time
import threading
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


## La url final sera esta https://www.adidas.es/yeezy-boost-350-v2/CP9366.html?forceSelSize=CP9366_630
## Url para testear https://www.adidas.es/bota-de-futbol-predator-18_-cesped-natural-seco/DB2013.html?forceSelSize=DB2013_630
START_URL =        'https://www.adidas.es/yeezy-boost-350-v2/CP9366.html?forceSelSize=CP9366_630'
REQUESTS_SPAM_REFRESH = 1
NUM_BROWSERS = 2
MAX_WAIT_FOR_ELEMENT = 60

def spam_page_untill_200():
    r = requests.get(START_URL)
    if len(r.history) >= 1 and r.history[0].status_code == 302:
        print('going to sleep, then retry')
        time.sleep(REQUESTS_SPAM_REFRESH)
        spam_page_untill_200()
    else:
        start_threads()

def start_threads():
    try:
        for i in range(NUM_BROWSERS):
            thread = browserThread(i)
            thread.start()
    except:
        print(sys.exc_info()[0])
        print('[ERROR]: unable to start a thread')
        raise

class browserThread(threading.Thread):
    
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        print(f'[STARTING BROWSER n-{thread_id}]')

    def fill_input(self, element_id, text):
        element = self.browser.find_element_by_id(element_id)
        element.send_keys(text)
        time.sleep(0.01)

    def wait_for_element_and_click(self, xpath, text_on_element):
        start_time = time.time()
        while True:
            try:
                print(f'Finding element ({xpath})...')
                element = self.browser.find_element_by_xpath(xpath)
                assert text_on_element in element.text
                element.click()
                print(f'Element ({xpath}) clicked!')
                return
            except (AssertionError, WebDriverException) as e:
                print(e)
                if time.time() - start_time > MAX_WAIT_FOR_ELEMENT:
                    raise e
                time.sleep(0.01)
        
    def run(self):
        # Abre firefox con la url del zapato y la talla ya seleccionada
        self.browser = webdriver.Firefox()
        self.browser.set_window_position(self.thread_id * 470, 0)
        self.browser.set_window_size(470, 1200)
        self.browser.get(START_URL)
        # Encuentra y clicka el boton de meter en carrito
        self.wait_for_element_and_click('//button[@data-auto-id="add-to-bag"]', 'CARRITO')
        # Encuentra y clicka el boton de ir al carrito
        self.wait_for_element_and_click('//a[@data-auto-id="view-bag-mobile"]', 'CARRITO')
        # Una vez en el carrito encuentra y clicka el boton de Conntinuar
        self.wait_for_element_and_click('//button[@name="dwfrm_cart_checkoutCart"]', 'CONTINUAR')
        # Rellena el formulario de entrega
        self.fill_input('dwfrm_shipping_shiptoaddress_shippingAddress_firstName', 'Daniel')
        self.fill_input('dwfrm_shipping_shiptoaddress_shippingAddress_lastName', 'Ciurana')
        self.fill_input('dwfrm_shipping_shiptoaddress_shippingAddress_address1', 'c:/valldemosa 23 2A Derecha')
        self.fill_input('dwfrm_shipping_shiptoaddress_shippingAddress_postalCode', '07010')
        self.fill_input('dwfrm_shipping_shiptoaddress_shippingAddress_city', 'Palma de Mallorca')
        self.fill_input('dwfrm_shipping_email_emailAddress', 'admin@victorciurana.com')
        # Confirma direccion
        self.wait_for_element_and_click('//button[@name="dwfrm_shipping_submitshiptoaddress"]', 'REVISAR Y PAGAR')
        # Rellena pago y muestra ventana final a usuario
        ## Seleccionamos ci-test-id porque otros campos son encriptados cada sesion
        element = self.browser.find_element_by_xpath('//input[@data-ci-test-id="cardNumberField"]')
        element.send_keys('1111222233334444')
        ## MES
        self.browser.find_element_by_xpath('//div[@data-default-value="Mes"]').click()
        self.browser.find_element_by_xpath('//div[@data-value="03"]').click()
        ## ANYO
        self.browser.find_element_by_xpath('//div[@data-default-value="Año"]').click()
        self.browser.find_element_by_xpath('//div[@data-value="2020"]').click()
        ## CVC
        self.fill_input('dwfrm_adyenencrypted_cvc', '123')
        # Clicka en comprar
        ## CLICK MANUAL
        # Se va a la mierda
        # browser.quit()
        print(f'[BROWSER n-{self.thread_id} ENDED THE PROCESS]')


if __name__ == '__main__':
    print('STARTING...')
    spam_page_untill_200()
