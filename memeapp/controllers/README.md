# Controllers

This is where all the code that handles requests lives. Each one of these `.py` files contains a few related functions
that are run when a user makes a request to a specific endpoint. The endpoint is defined at the beginning of the
function, and the function will return an HTTP response as a result.

Each of these uses a "blueprint", which is just a fancy Flask way to not have all of your code in the same file.

For more information, see the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/blueprints/)