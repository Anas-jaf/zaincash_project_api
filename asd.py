import jwt
import requests
import os

PORT = os.environ.get("PORT", 5000)

# If the environment if it was on production or on testing mode
init_url = 'https://test.zaincash.iq/transaction/init'
request_url = 'https://test.zaincash.iq/transaction/pay?id='

if os.environ.get("PRODUCTION") == "true":
    init_url = 'https://api.zaincash.iq/transaction/init'
    request_url = 'https://api.zaincash.iq/transaction/pay?id='

# Set the serviceType (Any text you like such as your website name)
service_type = "book"

# After a successful or failed order, the user will redirect to this URL
redirect_url = 'https://example.com/redirect'

"""
Notes about redirectionUrl:
In this URL, the API will add a new parameter (token) to its end like:
https://example.com/redirect?token=XXXXXXXXXXXXXX
"""

# Handling the payment request
def handle_payment_request():
    # Set the amount to 250 if there is no amount in the request (For testing)
    # It has to be more than 250 IQD
    amount = 250

    # Set an order id (This usually should be the order id in your sys DB)
    order_id = "YOUR_ORDER_ID_FROM_YOUR_DB"

    # Set the token expire time
    time = int(datetime.now().timestamp())

    # Building the transaction data to be encoded in a JWT token
    data = {
        'amount': amount,
        'serviceType': service_type,
        'msisdn': os.environ.get("MSISDN"),
        'orderId': order_id,
        'redirectUrl': redirect_url,
        'iat': time,
        'exp': time + 60 * 60 * 4
    }

    # Encoding the data
    token = jwt.encode(data, os.environ.get("SECRET"), algorithm="HS256")

    # Preparing the payment data to be sent to ZC API
    post_data = {
        'token': token,
        'merchantId': os.environ.get("MERCHANTID"),
        'lang': os.environ.get("LANG")
    }

    # Request options
    request_options = {
        'uri': init_url,
        'json': post_data,
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

    # Initializing a ZC order by sending a request with the tokens
    response = requests.post(**request_options)

    # Getting the operation id
    operation_id = response.json().get("id")

    # Redirect the user to ZC payment Page
    redirect_url = request_url + operation_id
    print(f"Redirecting to: {redirect_url}")


# Handling the redirect
def handle_redirect(token):
    if token:
        try:
            decoded = jwt.decode(token, os.environ.get("SECRET"), algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            # Handle decoding error
            pass
        else:
            if decoded.get("status") == 'success':
                # Do whatever you like
                pass
            else:
                # Do other things
                pass


# Running the script from the terminal
if __name__ == "__main__":
    command = input("Enter command (request or redirect): ")
    
    if command == "request":
        handle_payment_request()
    elif command == "redirect":
        token = input("Enter token: ")
        handle_redirect(token)
    else:
        print("Invalid command")
