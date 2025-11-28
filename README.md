# Odoo Incremental Data Fetcher

A modular and production-ready ETL (Extract, Transform, Load) pipeline for synchronizing data from Odoo ERP to PostgreSQL database. This project provides a clean, maintainable architecture with separate modules for data extraction, transformation, and loading.

## 🌟 Features

- **Modular Architecture**: Separate modules for client, extractors, loaders, and utilities
- **Incremental Sync**: Tracks state to sync only new/changed records
- **Batch Processing**: Efficient handling of large datasets
- **Foreign Key Handling**: Automatic handling of missing foreign key references
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Configuration Management**: Environment-based configuration
- **Type Safety**: Type hints throughout the codebase
- **Error Recovery**: Retry logic and graceful error handling

## 📁 Project Structure

```
Odoo-Incremental-Data-Fetcher/
│
├── odoo_client/              # Odoo XML-RPC client library
│   ├── __init__.py
│   ├── connection.py         # Connection and authentication
│   ├── model.py              # Base model operations
│   ├── domain_builder.py     # Query builder
│   ├── dataframe_processor.py # Data processing utilities
│   ├── api.py                # Main API facade
│   ├── pos_api.py            # POS-specific operations
│   ├── product_api.py        # Product operations
│   ├── partner_api.py        # Partner/Customer operations
│   ├── employee_api.py       # Employee operations
│   ├── stock_api.py          # Stock/Inventory operations
│   └── promotion_api.py      # Promotion operations
│
├── etl/                      # ETL pipeline modules
│   ├── extractors/           # Data extraction from Odoo
│   │   ├── __init__.py
│   │   ├── branches.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   ├── warehouses.py
│   │   ├── stock.py
│   │   ├── employees.py
│   │   ├── customers.py
│   │   ├── promotions.py
│   │   ├── sales.py
│   │   └── purchases.py
│   │
│   └── loaders/              # Data loading to PostgreSQL
│       ├── __init__.py
│       └── database_loader.py
│
├── config/                   # Configuration management
│   └── config.py
│
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── db_state.py          # State tracking
│   └── logging_config.py     # Logging setup
│
├── tests/                    # Unit tests
│
├── main.py                   # Main ETL orchestrator
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Access to Odoo instance with XML-RPC enabled
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AhmedAbdelazizSeif/Odoo-Incremental-Data-Fetcher
```
   
```bash
# Clone or navigate to project
cd Odoo-Incremental-Data-Fetcher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the ETL pipeline**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Odoo Configuration
ODOO_URL=https://erp.example.com
ODOO_DATABASE=production_db
ODOO_USERNAME=your_username@example.com
ODOO_PASSWORD=your_password

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# ETL Configuration
BATCH_SIZE=2500
LOG_LEVEL=INFO
LOG_FILE=logs/odoo_etl.log
```

## 📊 Data Flow

The ETL pipeline follows this sequence:

1. **Branches** → Extract POS configurations and branch mappings
2. **Categories** → Extract product categories, brands, and POS categories
3. **Products** → Extract products with batching
4. **Warehouses** → Extract warehouses and stock locations
5. **Stock** → Extract inventory levels with incremental sync
6. **Employees** → Extract HR data (departments, jobs, employees, users, teams)
7. **Customers** → Extract new customer/partner records
8. **Promotions** → Extract active and historical promotions
9. **Sales** → Extract POS and Direct Sales orders
10. **Sales Lines** → Extract order line items
11. **Purchases** → Extract purchase orders and lines

## 🔧 Usage Examples

### Using the Odoo Client Library

```python
from odoo_client import OdooAPI, DomainBuilder

# Initialize API
api = OdooAPI(
    url='https://erp.example.com',
    database='production',
    username='user@example.com',
    password='password'
)

# Connect
if api.connect():
    # Get POS orders
    orders = api.pos.get_orders(
        date_from='2024-01-01 00:00:00',
        date_to='2024-12-31 23:59:59',
        limit=1000
    )
    
    # Search products
    products = api.products.search_products(
        name='coffee',
        available_in_pos=True
    )
    
    # Custom query with DomainBuilder
    domain = DomainBuilder() \
        .equals('active', True) \
        .greater_than('list_price', 100) \
        .build()
    
    model = api.get_model('product.template')
    results = model.search_read(domain=domain)
```

### Custom Extractors

```python
from odoo_client import OdooAPI
from etl.extractors import extract_products
from etl.loaders import upsertion_method
from sqlalchemy import create_engine

# Setup
api = OdooAPI(...)
api.connect()

engine = create_engine('postgresql://...')

# Extract and load
products_df, products_ref_df, active_ids = extract_products(api)
upsertion_method(products_df, 'dim_products', engine, ['ref_id'])
```

## 📝 Logging

Logs are written to both console and file (default: `logs/odoo_etl.log`). The log level can be configured via the `LOG_LEVEL` environment variable.

Log format:
```
2024-01-15 10:30:45,123 - module_name - INFO - Log message
```

## 🛡️ Error Handling

The pipeline includes comprehensive error handling:

- **Foreign Key Violations**: Automatically logs and optionally creates placeholder records
- **Connection Errors**: Retry logic with exponential backoff
- **Data Validation**: Type checking and null handling
- **State Recovery**: Tracks progress to resume from failures

## 🔄 State Management

The pipeline maintains state in `db_vars.json` to enable incremental syncs:

```json
{
  "max_pos_order_id": 12345,
  "max_ds_order_id": 6789,
  "max_promotion_id": 100,
  "latest_stock_id": 50000
}
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=odoo_client --cov=etl tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for synchronizing Odoo ERP data to analytical databases
- Uses XML-RPC protocol for Odoo communication
- Optimized for large-scale data extraction

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🔗 Related Documentation

- [Odoo XML-RPC External API](https://www.odoo.com/documentation/16.0/developer/misc/api/odoo.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

**Version**: 2.0.0  
**Author**: Ahmed Seif  
**Last Updated**: November 2025
