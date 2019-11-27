# Locust tutorial

## Run local Locust

### Prerequirements
* [Python 3.6 + PIP package manager](https://www.python.org/downloads/release/python-368/) - Windows/MacOS (in case of using Linux - 
use embedded package manager to install Python 3.6)
* *[Windows only]:* [Visual Studio Build Tools 2019](https://visualstudio.microsoft.com/downloads/):
  - MSVC v140
  - MSVC v142
  - C++ CMake tools for Windows
  - Windows 10 SDK 

### Locust installation
* Install Locust via pip: `python -m pip install locust` 

### Run test
* Headless: `locust --host=${HOST_NAME} -f ${SCRIPT_NAME} -c ${CUSTOMERS} -r ${HATCH_RATE} -t ${DURATION} --no-web`
* With GUI: `locust --host=${HOST_NAME} -f ${SCRIPT_NAME} -P ${PORT} --web-host=${WEB_HOST}`

Variables:
HOST_NAME - URL of tested service. May contain subfolder, must contain protocol, trailing slash should be removed: `https://example.com`
SCRIPT_NAME - name of locust test script. In case of this example - `simple.py`, `advanced.py` or `business.py`
CUSTOMERS - number of customers being simulated simultaneously
HATCH_RATE - number of customers to summon (per second)
DURATION - test duration in seconds
PORT - port for GUI (default - 8089)
WEB_HOST - interface to bind for GUI (default - 0.0.0.0)

### Test cases
There are 3 test cases:
* Simple case - just home page loading, may be used on any web-site
* Advanced case - loading categores of products, designed for default installation of Magento 2
* Business case - loading categories, products and adding them to cart with some fuzzy logic. Designed for default
 installation of Magento 2 

#### Simple case
This case only loads home page without any additional logic

Command:
* Headless: `locust --host=${HOST_NAME} -f simple.py -c 5 -r 1 -t 60 --no-web`
* With GUI: `locust --host=${HOST_NAME} -f simple.py -P 8089 --web-host=localhost`

GUI will be accessible at http://localhost:8089/ 

#### Advanced case
This case initially loads home page to parse available categories list.
After this, random categories are being loaded by each customer

Command:
* Headless: `locust --host=${HOST_NAME} -f advanced.py -c 5 -r 1 -t 60 --no-web`
* With GUI: `locust --host=${HOST_NAME} -f advanced.py -P 8089 --web-host=localhost`

GUI will be accessible at http://localhost:8089/

#### Business case
There is simple business scenario in this test:
At the beginning, script loads registered customers credentials from `credentials.csv` file (if exists) and collects
list of available categories (in simalar to `advanced.py` way)
After this, for each customer it decides which kind of user should be used - anonymous or registered.
For registered user, log in routine is being performed
Then, typical business scenario is being run several times:
* Determine number of products to use (PRODUCTS_MIN <= N <= PRODUCTS_MAX)
* Clear the cart
* Repeat N times:
  - Load random category, pick random product, open product page (when RANDOM[0, 1] <= PRODUCTS_OPEN_PAGE) and add the 
product to cart.
* Finally open the cart

Command:
* Headless: `locust --host=${HOST_NAME} -f business.py -c 5 -r 1 -t 60 --no-web`
* With GUI: `locust --host=${HOST_NAME} -f business.py -P 8089 --web-host=localhost`

GUI will be accessible at http://localhost:8089/

There are several variables defined in business.py which affects script's behavior:

* ANONYMOUS_USERS - probability of using anonymous user instead of registered one (0.0-1.0, default - 0.8)
* PRODUCTS_OPEN_PAGE - probability of opening product page before adding product to cart (0.0-1.0, default - 0.7)
* PRODUCTS_MIN - minimal number of products picked for adding to cart (default - 2)
* PRODUCTS_MAX - maximal number of products picked for adding to cart (default - 7) 

#### Registered customers
In case of using business scenario, you may use registered users credentials for testing scenario for registering users
as well. Credentials may be put into `credentials.csv` file in next format:
* Each line contains information about single customer: comma-separated email and password

***All customers should be manually created before using their credentials for testing!***

Self-registering feature can be used for this.   


### Results handling
* Headless: By default, locust displays statistics in console every second and doesn't generate any output files.
This behavior can be changed by using CLI options:
  - --csv=${CSV_BASE_NAME} - locust will create two files, ${CSV_BASE_NAME}_distribution.csv and ${CSV_BASE_NAME}_requests.csv
  - --only-summary - disables displaying statistics during the test, only final results will be displayed

* GUI: Locust displays statistics in GUI, final results can be downloaded from `Download data` tab. Also, some charts are available in `Charts` tab  
