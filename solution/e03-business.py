from locust import HttpLocust, TaskSequence, task, between, seq_task
import os, re, json, csv, random

# List of URLs
CATEGORIES = []

# List of login/password pairs
CUSTOMERS = []

# Probability of using anonymous user instead of registered customer (0.0 - 1.0)
ANONYMOUS_USERS = 0.8

# Probability of opening product view page for each product (0.0 - 1.0)
PRODUCTS_OPEN_PAGE = 0.7

# Minimal and maximal number of products to process in each test
PRODUCTS_MIN = 2
PRODUCTS_MAX = 7

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.csv')

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'

class BusinessBehavior(TaskSequence):
    def setup(self):
        global CATEGORIES, CUSTOMERS
        self.client.headers['User-Agent'] = USER_AGENT

        response = self.client.get('/')
        # Parse URLs from response using regular expression
        result = re.findall('<li\s+class="[^"]*category-item[^"]*"><a href="([^"]+)"', response.text)
        for row in result:
            CATEGORIES.append(row)

        # Load credentials from 'credentials.csv' in script folder
        if (os.path.exists(CREDENTIALS_PATH)):
            with open(CREDENTIALS_PATH, 'r') as file:
                CUSTOMERS = list(csv.reader(file))

    def on_start(self):
        global CUSTOMERS
        # Determine which user should be used - anonymous or registered
        if random.random() >= ANONYMOUS_USERS and CUSTOMERS:
            self.loginCustomer(CUSTOMERS[random.randint(0, len(CUSTOMERS) - 1)])

    @seq_task(1)
    def taskClearCart(self):
        response = self.client.get('/')
        # Ensure that cart is empty
        self.clearCart(self.form_key(response.text))

    # Generate random number of products between PRODUCTS_MIN and PRODUCTS_MAX
    @task(random.randint(PRODUCTS_MIN, PRODUCTS_MAX))
    @seq_task(2)
    def taskProduct(self):
        global CATEGORIES, CUSTOMERS

        products = []

        # Running until some products will be found
        while not products:
            # Use random category URL
            category = random.choice(CATEGORIES)
            response = self.client.get(category, name="/catalog/category/view/id/%s")
            # Save form_key for further usage
            form_key = self.form_key(response.text)
            # Try to parse products from response
            products = self.parseProducts(response.text)

        # When there is only one products - random between 0 and 0 will fail
        if len(products) == 1:
            product = products.pop()
        else:
            product = products.pop(random.randint(0, len(products) - 1))

        # Load product view page with some randomness
        if random.random() <= PRODUCTS_OPEN_PAGE:
            form_key = self.viewProductPage(product)

        self.addToCart(form_key, product)

    @seq_task(3)
    def taskCart(self):
        self.client.get('/checkout/cart')

    def loginCustomer(self, customer):
        # Load login page to get the form key
        response = self.client.get('/customer/account/login')
        # Send credentials to log into web-site
        with self.client.post('/customer/account/loginPost', {
            'form_key': self.form_key(response.text),
            'login[username]': customer[0],
            'login[password]': customer[1]
        }, allow_redirects=False, catch_response=True) as response:
            if ('customer/account/login' in response.headers['location']):
                response.failure('Login failed')

    def viewProductPage(self, product):
        response = self.client.get('/catalog/product/view/id/%s' % product['product'], name="/catalog/product/view/id/%s")
        return self.form_key(response.text)

    def addToCart(self, form_key, product):
        # Prepare request params
        params = {
            'product': product['product'],
            'uenc': product['uenc'],
            'form_key': form_key,
        }

        # Add product attributes, like size, color, etc. Use randomly selected options
        for attrId in product['attributes']:
            params['super_attribute[%s]' % attrId] = random.choice(product['attributes'][attrId])

        response = self.client.post(product['action'], params, name="/checkout/cart/add/product/%s")
        return self.form_key(response.text)

    def clearCart(self, form_key):
        response = self.client.post('/checkout/cart/updatePost', {'form_key': form_key, 'update_cart_action': 'empty_cart'})
        return self.form_key(response.text)

    def parseProducts(self, responseData):
        # Find form element for all products using regular expression
        result = re.findall('<form data-role="tocart-form"\s*data-product-sku="([^"]+)"\s+action="([^"]+)"\s*method="post">((?:(?!<form).)*)</form>', responseData, re.I | re.M | re.S)
        products = []
        for row in result:
            product = {}
            # Get list of predefined parameters like SKU, uenc value, etc
            paramsList = re.findall('<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"[^>]*>', row[2])
            for param in paramsList:
                product[param[0]] = param[1]

            # Ensure that params contain product ID
            if 'product' not in product:
                continue

            product['sku'] = row[0]
            product['action'] = row[1].replace(self.parent.host, '')
            product['attributes'] = {}
            # Load JSON configuration for product attributes
            jsonConfig = re.findall('(\{\s*"\[data-role=swatch-option-%s\]"(?:(?!</script).)*)</script' % product['product'], responseData, re.I | re.M | re.S)
            if not jsonConfig:
                continue

            # Parse JSON into native dictionary and load all attributes
            jsonConfig = json.loads(jsonConfig[0])['[data-role=swatch-option-%s]' % product['product']]
            attributes = jsonConfig['Magento_Swatches/js/swatch-renderer']['jsonConfig']['attributes']
            for attrId in attributes:
                product['attributes'][attrId] = []
                for option in attributes[attrId]['options']:
                    product['attributes'][attrId].append(option['id'])

            products.append(product)

        return products

    def form_key(self, responseData):
        form_keys = re.findall('form_key.* value="([a-zA-Z0-9]{16})"', responseData)
        return form_keys[0] if len(form_keys) > 0 else ''

class TestUser(HttpLocust):
    task_set = BusinessBehavior
    wait_time = between(2, 4)
