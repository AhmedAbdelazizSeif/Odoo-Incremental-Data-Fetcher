"""
Example: Using the Odoo Client Library
This script demonstrates how to use the modular Odoo client.
"""

from odoo_client import OdooAPI, DomainBuilder

# Initialize API
api = OdooAPI(
    url='https://erp.knozelhekma.com',
    database='KnozElHekmaProduction',
    username='data.analysis@knozelhekma.com',
    password='your_password'  # Replace with actual password
)

# Connect to Odoo
if api.connect():
    print("✓ Connected to Odoo successfully")
    
    # Get server version
    version = api.get_version()
    print(f"Odoo Version: {version.get('server_version', 'Unknown')}")
    
    # Example 1: Get POS orders
    print("\n" + "=" * 60)
    print("Example 1: Get recent POS orders")
    print("=" * 60)
    
    orders = api.pos.get_orders(
        date_from='2024-10-01 00:00:00',
        limit=5
    )
    print(f"Retrieved {len(orders)} orders")
    if not orders.empty:
        print(orders[['id', 'name', 'date_order', 'amount_total']].head())
    
    # Example 2: Search products
    print("\n" + "=" * 60)
    print("Example 2: Search products available in POS")
    print("=" * 60)
    
    products = api.products.search_products(
        available_in_pos=True,
        limit=5
    )
    print(f"Found {len(products)} products")
    if not products.empty:
        print(products[['id', 'name', 'list_price']].head())
    
    # Example 3: Get customers
    print("\n" + "=" * 60)
    print("Example 3: Get customers")
    print("=" * 60)
    
    customers = api.partners.search_partners(
        customer_rank=1,
        limit=5
    )
    print(f"Found {len(customers)} customers")
    if not customers.empty:
        print(customers[['id', 'name', 'email']].head())
    
    # Example 4: Custom domain query
    print("\n" + "=" * 60)
    print("Example 4: Custom domain query - Active products over $50")
    print("=" * 60)
    
    domain = DomainBuilder() \
        .equals('active', True) \
        .greater_than('list_price', 50) \
        .equals('available_in_pos', True) \
        .build()
    
    product_model = api.get_model('product.template')
    results = product_model.search_read(
        domain=domain,
        fields=['name', 'list_price', 'barcode'],
        limit=5
    )
    print(f"Found {len(results)} products")
    for product in results:
        print(f"- {product['name']}: ${product['list_price']}")
    
    # Example 5: Get stock levels
    print("\n" + "=" * 60)
    print("Example 5: Check stock availability")
    print("=" * 60)
    
    stock = api.stock.get_stock(
        available_only=True,
        limit=5
    )
    print(f"Found {len(stock)} stock records")
    if not stock.empty:
        print(stock.head())

else:
    print("✗ Failed to connect to Odoo")
