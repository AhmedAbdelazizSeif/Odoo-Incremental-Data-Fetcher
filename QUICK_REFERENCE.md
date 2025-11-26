# Odoo ETL Quick Reference

## Installation & Setup

```bash
# Clone or navigate to project
cd odoo_etl_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup project
python setup.py

# Configure credentials
cp .env.example .env
# Edit .env with your credentials

# Run ETL
python main.py
```

## Environment Variables (.env)

```env
# Odoo
ODOO_URL=https://erp.example.com
ODOO_DATABASE=production
ODOO_USERNAME=user@example.com
ODOO_PASSWORD=secret

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=warehouse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret

# ETL
BATCH_SIZE=2500
LOG_LEVEL=INFO
LOG_FILE=logs/odoo_etl.log
```

## Common Commands

```bash
# Run full ETL pipeline
python main.py

# Test client connection
python example_usage.py

# Run tests
pytest tests/

# Setup/reset environment
python setup.py
```

## Quick API Usage

### Initialize Client

```python
from odoo_client import OdooAPI

api = OdooAPI(
    url='https://erp.example.com',
    database='production',
    username='user@example.com',
    password='secret'
)
api.connect()
```

### Get POS Orders

```python
# All orders
orders = api.pos.get_orders()

# With filters
orders = api.pos.get_orders(
    date_from='2024-01-01 00:00:00',
    date_to='2024-12-31 23:59:59',
    state='done',
    limit=1000
)

# With order lines
orders_with_lines = api.pos.get_orders_with_lines(
    date_from='2024-01-01 00:00:00'
)
```

### Search Products

```python
# By name
products = api.products.search_products(
    name='coffee',
    available_in_pos=True
)

# All products
products = api.products.get_all_products()
```

### Get Customers

```python
# Search
customers = api.partners.search_partners(
    name='John',
    is_company=False
)

# All customers
customers = api.partners.get_all_customers()
```

### Stock Levels

```python
# By product
stock = api.stock.get_stock(product_id=123)

# By location
stock = api.stock.get_stock(location_id=8)

# Available only
stock = api.stock.get_stock(available_only=True)
```

## Domain Builder Examples

### Simple Query

```python
from odoo_client import DomainBuilder

domain = DomainBuilder() \
    .equals('active', True) \
    .build()
# Result: [['active', '=', True]]
```

### Multiple Conditions (AND)

```python
domain = DomainBuilder() \
    .equals('active', True) \
    .greater_than('list_price', 100) \
    .build()
# Result: ['&', ['active', '=', True], ['list_price', '>', 100]]
```

### Multiple Conditions (OR)

```python
domain = DomainBuilder() \
    .equals('state', 'draft') \
    .equals('state', 'done') \
    .build_or()
# Result: ['|', ['state', '=', 'draft'], ['state', '=', 'done']]
```

### Date Range

```python
domain = DomainBuilder() \
    .date_range('create_date', '2024-01-01', '2024-12-31') \
    .build()
```

### In List

```python
domain = DomainBuilder() \
    .in_list('state', ['draft', 'done', 'posted']) \
    .build()
```

### Combined Query

```python
domain = DomainBuilder() \
    .equals('active', True) \
    .greater_than('list_price', 50) \
    .less_than('list_price', 500) \
    .in_list('categ_id', [1, 2, 3]) \
    .like('name', '%coffee%') \
    .build()
```

## Custom Model Access

```python
# Get any model
model = api.get_model('sale.order')

# Search
order_ids = model.search([['state', '=', 'sale']])

# Read
orders = model.read(order_ids, fields=['name', 'amount_total'])

# Search and read
orders = model.search_read(
    domain=[['state', '=', 'sale']],
    fields=['name', 'partner_id', 'amount_total'],
    limit=100
)

# Count
count = model.search_count([['state', '=', 'sale']])

# Create
order_id = model.create({'name': 'New Order', ...})

# Update
model.write([order_id], {'state': 'done'})

# Delete
model.unlink([order_id])
```

## ETL Usage

### Extract Only

```python
from odoo_client import OdooAPI
from etl.extractors import extract_products

api = OdooAPI(...)
api.connect()

products_df, refs_df, active_ids = extract_products(api)
```

### Load Only

```python
from etl.loaders import upsertion_method
from sqlalchemy import create_engine

engine = create_engine('postgresql://...')

upsertion_method(
    df=products_df,
    table_name='dim_products',
    engine=engine,
    primary_key=['ref_id']
)
```

### Custom ETL Flow

```python
from odoo_client import OdooAPI
from etl.extractors import extract_products, extract_sales
from etl.loaders import upsertion_method
from config.config import Config
from sqlalchemy import create_engine

# Setup
api = OdooAPI(**Config.get_odoo_config())
api.connect()
engine = create_engine(Config.get_postgres_url())

# Extract
products_df, _, _ = extract_products(api)
sales_df = extract_sales(api, max_pos_id=0, max_ds_id=0)

# Load
upsertion_method(products_df, 'dim_products', engine, ['ref_id'])
upsertion_method(sales_df, 'all_sales', engine, ['id'])
```

## State Management

```python
from utils.db_state import DBStateManager
from sqlalchemy import create_engine

engine = create_engine('postgresql://...')
state = DBStateManager(engine)

# Get max ID
max_id = state.get_max_id('all_sales', 'id', prefix='POS-')

# Get existing IDs
existing = state.get_existing_ids('dim_customers', 'id')

# Update state
state.set('max_pos_order_id', 12345)
state.update({'max_ds_order_id': 6789})
state.save_state()

# Read state
value = state.get('max_promotion_id', default=0)
```

## Logging

```python
from utils.logging_config import setup_logging
import logging

# Setup
logger = setup_logging('my_etl.log', 'INFO')

# Use
logger.info("Starting extraction")
logger.warning("Missing data detected")
logger.error("Failed to connect", exc_info=True)
```

## Troubleshooting

### Connection Issues

```python
# Test connection
api = OdooAPI(...)
if not api.connect():
    print("Connection failed")
    version = api.get_version()
    print(f"Server info: {version}")
```

### Check Database

```python
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://...')

with engine.connect() as conn:
    # Test connection
    result = conn.execute(text("SELECT version()"))
    print(result.scalar())
    
    # Check table
    result = conn.execute(text("SELECT COUNT(*) FROM dim_products"))
    print(f"Products: {result.scalar()}")
```

### Debug Mode

```python
# Enable debug logging
from utils.logging_config import setup_logging

logger = setup_logging('debug.log', 'DEBUG')

# SQLAlchemy echo
from sqlalchemy import create_engine

engine = create_engine('postgresql://...', echo=True)
```

## Performance Tips

1. **Batch Size**: Adjust `BATCH_SIZE` in .env (1000-5000)
2. **Limit Queries**: Use `limit` parameter in search operations
3. **Select Fields**: Specify only needed fields in `search_read`
4. **Incremental Sync**: Use state management to track progress
5. **Parallel Processing**: Run independent extractions in parallel

## File Locations

- **Configuration**: `.env`
- **State**: `db_vars.json`
- **Logs**: `logs/odoo_etl.log`
- **Main Script**: `main.py`
- **Examples**: `example_usage.py`

## Common Errors

### "Not authenticated"
```python
# Always call connect() before using API
api = OdooAPI(...)
api.connect()  # ← Don't forget this!
```

### Foreign key violation
```python
# Check missing_data table
SELECT * FROM missing_data ORDER BY created_at DESC LIMIT 10;
```

### Out of memory
```python
# Reduce batch size in .env
BATCH_SIZE=1000
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🏗️ Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 🔧 Review [DEVELOPMENT.md](DEVELOPMENT.md) for advanced topics
- 📝 See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for file organization
