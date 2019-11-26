from flask import Flask, request, Blueprint
import payload as pl
import uuid

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

#TODO: Add your secret key
# Your secret key here
pl.api_key = 'your_secret_key_123'
routes = Blueprint('routes', __name__)

# Function that auto-generates dummy invoices for testing purposes
def get_invoices_from_external_API():
    invoices = []
    for i in range(1, 21):
        id = uuid.uuid4()
        invoice = {
            'payment_link_type': 'one_time',
            'description': 'Services rendered',
            'amount': i + 0.99,
            'id': str(id),
            'customer_name': 'Test Customer ' + str(id),
            # For testing purposes, insert your own email here
            'customer_email': 'testcustomer+' + str(id) + '@example.com'
        }
        invoices.append(invoice)
    return(invoices)

@routes.route("/generate_payment_links", methods=['POST'])
def generate_payment_links():
    # TODO: Pull in your invoices from an external service and massage them into
    # the correct format to use pl.PaymentLink.create()
    invoices = get_invoices_from_external_API()
    urls = {}
    for invoice in invoices:
        payment_link = pl.PaymentLink.create(
            # type can be 'one_time' or 'reusable'.
            # Most PaymentLinks for invoices will be 'one_time'
            type=invoice['payment_link_type'],
            description=invoice['description'],
            amount = invoice['amount'],
            # Storing the external invoice_id as metadata will allow you to
            # update it later once a payment is made
            attrs = {
                'invoice_id': invoice['id']
            },
            # If you include the customer's name and email when generating the
            # PaymentLink, an email will be automatically sent to them with the
            # details of the payment and a secure link
            customer = pl.Customer(
                name=invoice['customer_name'],
                email=invoice['customer_email']
            ),
            # TODO: Add your processing ID
            # The ID of your processing account
            processing_id='YOUR_PROCESSING_ID_HERE'
        )
        urls[invoice['id']] = payment_link.url
    return(urls)

@routes.route("/create_webhook", methods=['POST'])
def create_webhook():
    webhook = pl.Webhook.create(
        # This trigger can be 'bank_account_reject', 'refund', 'void',
        # 'chargeback', 'chargeback_reversal', 'automatic_payment', 'payment',
        # or 'decline'
        #
        # For PaymentLinks, the trigger should probably be 'payment'
        trigger=request.json['trigger'],

        # The url of the endpoint that handles webhooks in your app. In this
        # example, the url would be
        # 'https://www.some-example-domain.com/webhook_handler'
        url=request.json['url']
    )
    return(webhook.json())

@routes.route("/webhook_handler", methods=['POST'])
def handle_payment():
    print("Webhook triggered")
    print(request.json)

    # Select all payment attributes and Payment's hidden payment_link_id attribute from the Payment that triggered the webhook
    payment = pl.Payment.select(pl.attr.payment_link_id, *pl.Payment).get(request.json['triggered_on']['id'])

    # Find the PaymentLink object that matches the payment's payment_link_id
    payment_link = pl.PaymentLink.get(payment.payment_link_id)

    # The invoice_id will be where you left it - in attrs
    invoice_id = payment_link.attrs['invoice_id']

    print(invoice_id)

    #TODO: Make some API call to the service that manages your invoices to mark
    # the invoice with that invoice_id as paid:
    # update_invoice_on_external_API(invoice_id)

    return('')

# Job that auto-generates payment links every 24 hours and emails them to customers
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_payment_links, trigger="interval", hours=24)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
