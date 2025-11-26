# Odoo ETL Project - Complete File Structure

```
odoo_etl_project/
│
├── README.md                          # Main documentation
├── DEVELOPMENT.md                     # Development guide
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore rules
├── example_usage.py                   # Usage examples
├── main.py                            # Main ETL orchestrator
│
├── odoo_client/                       # Odoo XML-RPC Client Library
│   ├── __init__.py                    # Package exports
│   ├── connection.py                  # Connection & authentication
│   ├── model.py                       # Base model operations (search, read, create, etc.)
│   ├── domain_builder.py              # Query builder helper
│   ├── dataframe_processor.py         # DataFrame processing utilities
│   ├── api.py                         # Main API facade
│   ├── pos_api.py                     # POS-specific operations
│   ├── product_api.py                 # Product operations
│   ├── partner_api.py                 # Partner/Customer operations
│   ├── employee_api.py                # Employee operations
│   ├── stock_api.py                   # Stock/Inventory operations
│   └── promotion_api.py               # Promotion operations
│
├── etl/                               # ETL Pipeline Modules
│   ├── __init__.py                    # ETL package exports
│   │
│   ├── extractors/                    # Data Extraction Modules
│   │   ├── __init__.py                # Extractors exports
│   │   ├── branches.py                # Extract branch configurations
│   │   ├── categories.py              # Extract product categories & brands
│   │   ├── products.py                # Extract products (batched)
│   │   ├── warehouses.py              # Extract warehouses & locations
│   │   ├── stock.py                   # Extract stock levels
│   │   ├── employees.py               # Extract employee & HR data
│   │   ├── customers.py               # Extract customers/partners
│   │   ├── promotions.py              # Extract promotions
│   │   ├── sales.py                   # Extract POS & Direct Sales orders
│   │   └── purchases.py               # Extract purchase orders
│   │
│   └── loaders/                       # Data Loading Modules
│       ├── __init__.py                # Loaders exports
│       └── database_loader.py         # PostgreSQL upsert with FK handling
│
├── config/                            # Configuration Management
│   ├── __init__.py                    # Config exports
│   └── config.py                      # Environment-based configuration
│
├── utils/                             # Utility Modules
│   ├── __init__.py                    # Utils exports
│   ├── db_state.py                    # State tracking & management
│   └── logging_config.py              # Logging setup
│
└── tests/                             # Unit Tests
    ├── __init__.py                    # Tests package
    └── test_client.py                 # Client library tests
```

## File Descriptions

### Root Files

- **README.md**: Comprehensive project documentation with setup instructions, usage examples, and architecture overview
- **DEVELOPMENT.md**: Development guide with troubleshooting, performance tuning, and deployment instructions
- **LICENSE**: MIT License for open source distribution
- **requirements.txt**: Python package dependencies
- **.env.example**: Template for environment variables (credentials, configuration)
- **.gitignore**: Git ignore patterns for sensitive files and generated content
- **example_usage.py**: Practical examples of using the Odoo client library
- **main.py**: Main ETL pipeline orchestrator that runs the complete sync process

### odoo_client/ - Modular Odoo Client Library

**Core Components:**
- `connection.py`: Handles XML-RPC connection and authentication
- `model.py`: Generic model operations (CRUD, search, read_group)
- `domain_builder.py`: Fluent API for building Odoo search domains
- `dataframe_processor.py`: Converts Odoo records to pandas DataFrames

**Specialized APIs:**
- `pos_api.py`: POS order operations
- `product_api.py`: Product search and retrieval
- `partner_api.py`: Customer/partner management
- `employee_api.py`: Employee data access
- `stock_api.py`: Inventory and stock operations
- `promotion_api.py`: Promotion data access
- `api.py`: Unified facade providing access to all specialized APIs

### etl/ - ETL Pipeline

**Extractors** (etl/extractors/):
Each extractor module focuses on a specific entity type:
- Handles batch processing for large datasets
- Processes relational fields (Many2one, Many2many)
- Calculates derived fields
- Returns pandas DataFrames ready for loading

**Loaders** (etl/loaders/):
- `database_loader.py`: Intelligent upsert with:
  - Foreign key violation handling
  - Missing reference logging
  - Batch processing
  - Retry logic

### config/ - Configuration

- `config.py`: Centralized configuration using environment variables
  - Odoo credentials
  - PostgreSQL connection
  - ETL parameters (batch sizes, logging)

### utils/ - Utilities

- `db_state.py`: Manages ETL state for incremental syncs
  - Tracks max IDs
  - Persists state to JSON file
  - Retrieves existing records

- `logging_config.py`: Configures logging to file and console

### tests/ - Testing

- `test_client.py`: Unit tests for the Odoo client library
- Future: Add tests for extractors, loaders, and integration tests

## Key Features

### 1. Modular Architecture
Each class in its own file for:
- Easy maintenance
- Clear separation of concerns
- Testability
- Reusability

### 2. Incremental Sync
- Tracks state in `db_vars.json`
- Only syncs new/changed records
- Resumes from last successful position

### 3. Error Handling
- Foreign key violation recovery
- Automatic placeholder creation
- Comprehensive logging
- Retry logic

### 4. Type Safety
- Type hints throughout
- Clear interfaces
- IDE autocomplete support

### 5. Production Ready
- Environment-based configuration
- Comprehensive logging
- State management
- Error recovery
- Batch processing

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run ETL pipeline**
   ```bash
   python main.py
   ```

## Usage Patterns

### Using the Client Library
```python
from odoo_client import OdooAPI

api = OdooAPI(url='...', database='...', username='...', password='...')
api.connect()

# Use specialized APIs
orders = api.pos.get_orders(date_from='2024-01-01', limit=100)
products = api.products.search_products(available_in_pos=True)
customers = api.partners.get_all_customers()
```

### Custom Extraction
```python
from etl.extractors.products import extract_products
from etl.loaders import upsertion_method

products_df, refs_df, ids = extract_products(api)
upsertion_method(products_df, 'dim_products', engine, ['ref_id'])
```

### Building Custom Domains
```python
from odoo_client import DomainBuilder

domain = DomainBuilder() \
    .equals('active', True) \
    .greater_than('list_price', 100) \
    .in_list('state', ['draft', 'done']) \
    .build()
```

## Next Steps

1. **Setup your environment** - Configure `.env` file
2. **Review the README** - Understand the architecture
3. **Check DEVELOPMENT.md** - Learn about deployment and maintenance
4. **Run example_usage.py** - See the client library in action
5. **Execute main.py** - Run the full ETL pipeline

## Contributing

This project is ready for:
- Public repository hosting (GitHub, GitLab)
- Collaborative development
- Extension with new extractors
- Integration with other systems

All sensitive information has been externalized to `.env` file, which is gitignored.
