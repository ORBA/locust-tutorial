from locust import HttpLocust, TaskSet, task, between

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'

class SimpleBehavior(TaskSet):
    def setup(self):
        self.client.headers['User-Agent'] = USER_AGENT

    @task(1)
    def test(self):
        self.client.get("/")

class TestUser(HttpLocust):
    task_set = SimpleBehavior
    wait_time = between(3, 3)
