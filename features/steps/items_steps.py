"""
Inventory Steps

Steps file for items.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following items')
def step_impl(context):
    """ Delete all Items and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the items and delete them one by one
    context.resp = requests.get(context.base_url + '/inventory', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for item in context.resp.json():
        context.resp = requests.delete(context.base_url + '/inventory/' + str(item["_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new items
    create_url = context.base_url + '/inventory'
    for row in context.table:
        data = {
            "name": row['name'],
            "category": row['category'],
            "quantity": row['quantity'],
            "condition": row['condition']
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)