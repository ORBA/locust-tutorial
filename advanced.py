from locust import HttpLocust, TaskSet, task, between
import re, random

CATEGORIES = []
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'

class AdvancedBehavior(TaskSet):
    def setup(self):
        global CATEGORIES
        self.client.headers['User-Agent'] = USER_AGENT

        response = self.client.get('/')
        # Parse URLs from response using regular expression
        result = re.findall('<li\s+class="[^"]*category-item[^"]*"><a href="([^"]+)"', response.text)
        for row in result:
            CATEGORIES.append(row)

    @task
    def load_category(self):
        global CATEGORIES
        # Load random category using saved list of URLs
        self.client.get(random.choice(CATEGORIES), name="Loading category")


class TestUser(HttpLocust):
    task_set = AdvancedBehavior
    wait_time = between(1, 5)

