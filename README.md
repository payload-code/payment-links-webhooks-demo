# Payment Links with Webhooks Demo

This is a sample Flask app that demonstrates how to use Payload's PaymentLink and Webhook objects.

## Setup

To use it, begin by cloning this repository onto your machine:
```
$ git clone https://github.com/payload-code/payment-links-webhooks-demo.git
```
You'll need to make some changes to the code for it to handle requests properly. These have been marked with `#TODOs` in `routes.py`

In line 11, insert your Payload secret key:
```
pl.api_key = 'your_secret_key_123'
```
In line 58, insert the ID of the processing account that you want to use:
```
processing_id='YOUR_PROCESSING_ID_HERE'
```
Next, install the required dependencies with `pipenv` (make sure to run this command in the project directory):
```
$ pipenv install
```
Start the project's virtualenv:
```
$ pipenv shell
```
Start the app with:
```
$ flask run
```
or 
``` 
$ python app.py
```

## Testing

`routes.py` defines three endpoints: `/generate_payment_links`, `/create_webhook`, and a `/webhook_handler`. 

To create a webhook, you'll need a service that exposes your local webserver, like [ngrok](https://dashboard.ngrok.com/get-started):
```
$ /path/to/ngrok http 5000
```
Once your local app is exposed, you can create a webhook using the `/create_webhook` endpoint:
```
$ curl http://localhost:5000/create_webhook -X POST -d trigger='payment' -d url='your-url.ngrok.io/webhook_handler'
```
Try this sample command to generate 20 dummy payment links:
```
$ curl http://localhost:5000/generate_payment_links -X POST
```
Now navigate to one of the payment links in your browser and complete the form. Use `4242 4242 4242 4242` or `5103 2088 7967 2792` as the card number for testing purposes.

Once the payment completes, the app should print `Webhook triggered`, along with the Webhook Trigger payload and the ID of the invoice that was paid.

## External Invoices
To incorporate invoices from an external source, like JD Edwards or Microsoft Dynamics, replace line 35 in `routes.py` with a call to the service that manages your invoices:
```
invoices = get_invoices_from_external_API()
```
To mark invoices as paid, replace line 98 of `routes.py` (in `handle_payment()`):
```
update_invoice_on_external_API(invoice_id)
```

You can generate Payment Links with a call to `/generate_payment_links`, or use the job in lines 103-105, which automatically generates Payment Links every 24 hours:
```
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_payment_links, trigger="interval", hours=24)
scheduler.start()
```
