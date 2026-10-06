import pandas as pd

customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv")
payments = pd.read_csv("data/payments.csv")

print("Shape:")
print(customers.shape)
print(products.shape)
print(orders.shape)
print(payments.shape)

print("\nDuplikasi:")
print(orders["order_id"].duplicated().sum())
print(customers["customer_id"].duplicated().sum())
print(products["product_id"].duplicated().sum())