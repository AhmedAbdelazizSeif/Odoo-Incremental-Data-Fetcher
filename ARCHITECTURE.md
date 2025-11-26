# Odoo ETL Project - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ODOO ERP SYSTEM                                 │
│                     (XML-RPC API Interface)                             │
└─────────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ XML-RPC
                                   │
┌──────────────────────────────────┼──────────────────────────────────────┐
│                                  │                                       │
│                        ODOO CLIENT LIBRARY                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │  │
│  │  │ Connection   │──────│    Model     │──────│ DomainBuilder│   │  │
│  │  │   Manager    │      │   (CRUD)     │      │   (Queries)  │   │  │
│  │  └──────────────┘      └──────────────┘      └──────────────┘   │  │
│  │                                                                   │  │
│  │  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │  │
│  │  │   POS API    │ Product API  │ Partner API  │ Employee API │   │  │
│  │  ├──────────────┼──────────────┼──────────────┼──────────────┤   │  │
│  │  │  Stock API   │Promotion API │              │              │   │  │
│  │  └──────────────┴──────────────┴──────────────┴──────────────┘   │  │
│  │                                                                   │  │
│  │                     OdooAPI (Unified Facade)                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           ETL PIPELINE                                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        EXTRACTORS                                 │  │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐    │  │
│  │  │ Branches │Categories│ Products │Warehouses│    Stock     │    │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────────┤    │  │
│  │  │Employees │ Customers│Promotions│  Sales   │  Purchases   │    │  │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────────┘    │  │
│  │                                                                   │  │
│  │                           ▼ pandas DataFrames                    │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                    TRANSFORMERS                             │ │  │
│  │  │  • Process relational fields                                │ │  │
│  │  │  • Calculate derived fields                                 │ │  │
│  │  │  • Handle data types                                        │ │  │
│  │  │  • Apply business logic                                     │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  │                                                                   │  │
│  │                           ▼ Processed DataFrames                 │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                      LOADERS                                │ │  │
│  │  │  • Batch processing                                         │ │  │
│  │  │  • Upsert operations                                        │ │  │
│  │  │  • Foreign key handling                                     │ │  │
│  │  │  • Error recovery                                           │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         UTILITIES                                 │  │
│  │  ┌──────────────────┬─────────────────┬──────────────────────┐   │  │
│  │  │   State Manager  │ Logging Config  │  Config Manager      │   │  │
│  │  │  (db_vars.json)  │ (File + Console)│  (.env variables)    │   │  │
│  │  └──────────────────┴─────────────────┴──────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      POSTGRESQL DATABASE                                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    DIMENSION TABLES                               │  │
│  │  • dim_branches        • dim_categories      • dim_brands         │  │
│  │  • dim_products        • dim_employees       • dim_customers      │  │
│  │  • dim_promotions      • dim_departments     • dim_jobs           │  │
│  │  • dim_users           • dim_teams           • dim_work_locations │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      FACT TABLES                                  │  │
│  │  • all_sales           • fact_sales_lines    • fact_stock         │  │
│  │  • fact_purchases      • fact_warehouse      • fact_stock_locations│ │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    UTILITY TABLES                                 │  │
│  │  • missing_data (FK violation tracking)                           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. EXTRACTION PHASE
```
Odoo → OdooAPI → Specialized API → Extractor → Raw DataFrame
```
- Connect to Odoo via XML-RPC
- Use specialized APIs for entity-specific operations
- Extract in batches for large datasets
- Return pandas DataFrames

### 2. TRANSFORMATION PHASE
```
Raw DataFrame → Process Relations → Calculate Fields → Clean Data → Processed DataFrame
```
- Extract IDs from Many2one fields
- Calculate derived fields (age, tenure, etc.)
- Convert timezones
- Truncate strings to DB limits

### 3. LOADING PHASE
```
Processed DataFrame → Batch → Upsert → Handle Errors → PostgreSQL
```
- Batch processing for performance
- ON CONFLICT DO UPDATE (upsert)
- Foreign key violation handling
- Automatic retry logic

## Component Interactions

### Odoo Client Library
```
User Code
   │
   ├─→ OdooAPI (facade)
   │      │
   │      ├─→ OdooConnection (auth, execute_kw)
   │      ├─→ POSOrderAPI
   │      ├─→ ProductAPI
   │      ├─→ PartnerAPI
   │      └─→ ... (other specialized APIs)
   │
   └─→ DomainBuilder (query construction)
```

### ETL Pipeline
```
main.py
   │
   ├─→ Initialize (Config, Engine, API, StateManager)
   │
   ├─→ For each entity:
   │      ├─→ Extract (via extractors)
   │      ├─→ Transform (in extractor)
   │      └─→ Load (via database_loader)
   │
   └─→ Update State & Save
```

### State Management
```
DBStateManager
   │
   ├─→ Load state from db_vars.json
   ├─→ Query max IDs from database
   ├─→ Provide state to extractors
   └─→ Save updated state after load
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION ENVIRONMENT                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Cron / Scheduler                        │   │
│  │  (Daily/Hourly ETL execution)                        │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│  ┌───────────────────▼──────────────────────────────────┐   │
│  │           Python ETL Application                     │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  main.py (Orchestrator)                        │  │   │
│  │  │  ├─ odoo_client/                               │  │   │
│  │  │  ├─ etl/extractors/                            │  │   │
│  │  │  ├─ etl/loaders/                               │  │   │
│  │  │  └─ utils/                                     │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                        │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Configuration                                 │  │   │
│  │  │  • .env (credentials)                          │  │   │
│  │  │  • db_vars.json (state)                        │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────┘  │
│                      │                 │                     │
│                      │                 │                     │
│  ┌───────────────────▼─────┐  ┌───────▼──────────────────┐  │
│  │   Odoo ERP System       │  │  PostgreSQL Database     │  │
│  │   (External)            │  │  (Data Warehouse)        │  │
│  └─────────────────────────┘  └──────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Monitoring & Logging                    │   │
│  │  • Application logs (logs/odoo_etl.log)              │   │
│  │  • Error alerts                                      │   │
│  │  • Performance metrics                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

1. **Facade Pattern**: `OdooAPI` provides unified interface to specialized APIs
2. **Builder Pattern**: `DomainBuilder` constructs complex queries fluently
3. **Strategy Pattern**: Different extractors for different entity types
4. **Template Method**: Common extraction/loading pattern with entity-specific details
5. **Singleton**: Configuration and state managers

## Scalability Considerations

- **Batch Processing**: Configurable batch sizes for memory efficiency
- **Incremental Sync**: Only fetch new/changed records
- **Connection Pooling**: Reuse database connections
- **Parallel Processing**: Can parallelize independent extractions
- **State Persistence**: Resume from failures
