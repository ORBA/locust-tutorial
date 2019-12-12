# Locust exercises

## Exercise 1 - avoid exceptions

* There are 2 exceptions in `clearCart` and `addToCart` method – please, update code to avoid raising exceptions
* Use some variable to save interim results and validate it before usage

## Exercise 2 - Refactoring code with a little help of TaskSequence

* Use TaskSequence instead of TaskSet in business.py to refactor the test. Use example for reference.
* Each step should be moved into separate task
* Tasks should be ordered using `@seq_task` decorator
* Adding product to cart should be represented as a single task with `@task` decorator.
Use `products_left` as `weight` argument

## Exercise 3 - loginCustomer errors handling

* Currently, test only tries to login using provided credentials, without checking the result
* For some reason, provided credentials may be wrong – please, check the response of `loginPost` request
* *Hint:* use `allow_redirects=False` and response.headers attribute to check the redirection URL
* *Hint:* you can use `print(%var%)` function to output variable value to console while running test.
If there is no need to continue test after printing data – use `exit()` function to terminate the test
* *Hint:* complex data types (list, dictionary) can be converted to human-readable structured text for printing
using `json.dumps(%var%, indent=2)`

