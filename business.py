from locust import HttpLocust, TaskSet, task, between
import os, re, json, csv, random

CATEGORIES = []
CUSTOMERS = []
ANONYMOUS_USERS = 0.8
PRODUCTS_OPEN_PAGE = 0.7
PRODUCTS_MIN = 2
PRODUCTS_MAX = 7
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'

class BusinessBehavior(TaskSet):
    def setup(self):
        global CATEGORIES, CUSTOMERS
        self.client.headers['User-Agent'] = USER_AGENT

        response = self.client.get('/')
        result = re.findall('<li\s+class="[^"]*category-item[^"]*"><a href="([^"]+)"', response.text)
        for row in result:
            CATEGORIES.append(row)

        with open(os.path.join(os.path.dirname(__file__), 'credentials.csv'), 'r') as file:
            CUSTOMERS = list(csv.reader(file))

    def on_start(self):
        global CUSTOMERS
        if random.random() >= ANONYMOUS_USERS and CUSTOMERS:
            self.loginCustomer(CUSTOMERS[random.randint(0, len(CUSTOMERS) - 1)])

    @task(1)
    def test(self):
        global CATEGORIES, CUSTOMERS

        products = []
        productsLeft = random.randint(PRODUCTS_MIN, PRODUCTS_MAX)

        response = self.client.get('/')
        form_key = self.clearCart(self.form_key(response.text))

        while productsLeft:
            while not products:
                category = random.choice(CATEGORIES)
                response = self.client.get(category, name="/catalog/category/view/id/%s")
                form_key = self.form_key(response.text)
                products = self.parseProducts(response.text)

            if len(products) == 1:
                product = products.pop()
            else:
                product = products.pop(random.randint(0, len(products) - 1))

            if random.random() <= PRODUCTS_OPEN_PAGE:
                form_key = self.viewProductPage(product)

            self.addToCart(form_key, product)
            products = []
            productsLeft -= 1

        self.client.get('/checkout/cart')

    def loginCustomer(self, customer):
        response = self.client.get('/customer/account/login')
        self.client.post('/customer/account/loginPost', {
            'form_key': self.form_key(response.text),
            'login[username]': customer[0],
            'login[password]': customer[1]
        })

    def viewProductPage(self, product):
        response = self.client.get('/catalog/product/view/id/%s' % product['product'], name="/catalog/product/view/id/%s")
        return self.form_key(response.text)

    def addToCart(self, form_key, product):
        params = {
            'product': product['product'],
            'uenc': product['uenc'],
            'form_key': form_key,
        }

        for attrId in product['attributes']:
            params['super_attribute[%s]' % attrId] = random.choice(product['attributes'][attrId])

        response = self.client.post(product['action'], params, name="/checkout/cart/add/product/%s")
        return self.form_key(response.text)

    def clearCart(self, form_key):
        response = self.client.post('/checkout/cart/updatePost', {'form_key': form_key, 'update_cart_action': 'empty_cart'})
        return self.form_key(response.text)

    def parseProducts(self, responseData):
        result = re.findall('<form data-role="tocart-form"\s*data-product-sku="([^"]+)"\s+action="([^"]+)"\s*method="post">((?:(?!<form).)*)</form>', responseData, re.I | re.M | re.S)
        products = []
        for row in result:
            product = {}
            paramsList = re.findall('<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"[^>]*>', row[2])
            for param in paramsList:
                product[param[0]] = param[1]

            if 'product' not in product:
                continue

            product['sku'] = row[0]
            product['action'] = row[1].replace(self.parent.host, '')
            product['attributes'] = {}
            jsonConfig = re.findall('(\{\s*"\[data-role=swatch-option-%s\]"(?:(?!</script).)*)</script' % product['product'], responseData, re.I | re.M | re.S)
            if not jsonConfig:
                continue

            jsonConfig = json.loads(jsonConfig[0])['[data-role=swatch-option-%s]' % product['product']]
            attributes = jsonConfig['Magento_Swatches/js/swatch-renderer']['jsonConfig']['attributes']
            for attrId in attributes:
                product['attributes'][attrId] = []
                for option in attributes[attrId]['options']:
                    product['attributes'][attrId].append(option['id'])

            products.append(product)

        return products

    def form_key(self, responseData):
        return re.findall('form_key.* value="([a-zA-Z0-9]{16})"', responseData)[0]

class TestUser(HttpLocust):
    task_set = BusinessBehavior
    wait_time = between(2, 4)
