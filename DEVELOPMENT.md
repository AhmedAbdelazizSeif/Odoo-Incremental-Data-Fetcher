# Odoo Incremental Data Fetcher - Development Notes

## Database Schema Requirements

The ETL pipeline expects the following tables to exist in your PostgreSQL database:

### Dimension Tables

- `dim_branches` - Branch information
- `dim_branches_branch_ref` - Branch reference mappings
- `dim_categories` - Product categories
- `dim_brands` - Product brands
- `dim_pos_categories` - POS categories
- `dim_products` - Product master data
- `dim_products_product` - Product reference mappings
- `dim_departments` - HR departments
- `dim_work_locations` - Work locations
- `dim_jobs` - Job positions
- `dim_emps` - Employee master data
- `dim_users` - System users
- `dim_teams` - Sales teams
- `dim_customers` - Customer/Partner data
- `dim_promotions` - Promotion master data
- `dim_promotion_types` - Promotion types
- `dim_purchases` - Purchase orders
- `dim_stock_picking_type` - Stock operation types

### Fact Tables

- `fact_warehouse` - Warehouse data
- `fact_stock_locations` - Stock locations
- `fact_stock` - Inventory levels
- `all_sales` - Unified sales orders (POS + Direct Sales)
- `fact_sales_lines` - Sales order line items
- `fact_purchases` - Purchase order lines

### Utility Tables

- `missing_data` - Logs foreign key violations and missing references

## Running the Pipeline

### Full ETL Run
```bash
python main.py
```

### Module-Specific Execution

You can also import and run specific extractors:

```python
from odoo_client import OdooAPI
from etl.extractors.products import extract_products
from etl.loaders import upsertion_method
from sqlalchemy import create_engine

api = OdooAPI(...)
api.connect()

engine = create_engine('postgresql://...')

# Extract only products
products_df, refs_df, ids = extract_products(api)
upsertion_method(products_df, 'dim_products', engine, ['ref_id'])
```

## Performance Tuning

### Batch Sizes
Adjust `BATCH_SIZE` in `.env` based on your network and database capacity:
- Small instances: 1000-2000
- Medium instances: 2500-5000
- Large instances: 5000-10000

### Connection Pooling
SQLAlchemy pool settings in `main.py`:
- `pool_size=20` - Number of connections to maintain
- `max_overflow=0` - Additional connections allowed
- `pool_timeout=30` - Seconds to wait for connection
- `pool_recycle=3600` - Recycle connections every hour

## Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Verify Odoo URL is accessible
   - Check username/password
   - Ensure XML-RPC is enabled in Odoo

2. **Foreign Key Violations**
   - Check `missing_data` table for logged issues
   - Ensure dimension tables are loaded before fact tables
   - Review extraction order in `main.py`

3. **Memory Issues with Large Datasets**
   - Reduce `BATCH_SIZE`
   - Process data in smaller date ranges
   - Increase available system memory

4. **Slow Performance**
   - Check database indexes
   - Optimize network connection
   - Increase batch size if network is fast
   - Review Odoo server load

## Development Guidelines

### Adding New Extractors

1. Create new file in `etl/extractors/`
2. Implement extraction function
3. Add to `etl/extractors/__init__.py`
4. Add to `main.py` pipeline sequence

Example:
```python
# etl/extractors/my_entity.py
import pandas as pd
from odoo_client import OdooAPI

def extract_my_entity(api: OdooAPI) -> pd.DataFrame:
    data = api.get_model('my.model').search_read(...)
    return pd.DataFrame(data)
```

### Adding New API Modules

1. Create new file in `odoo_client/`
2. Implement API class
3. Add property to `odoo_client/api.py`
4. Export from `odoo_client/__init__.py`

## Monitoring

### Log Files
- Default location: `logs/odoo_etl.log`
- Rotation: Implement log rotation for production
- Monitoring: Use tools like Logstash, Splunk, or CloudWatch

### State Tracking
- State file: `db_vars.json`
- Backup state file before major changes
- Contains max IDs for incremental sync

### Metrics to Monitor
- Extraction time per entity
- Record counts per table
- Error rates
- Database connection pool usage
- Memory consumption

## Deployment

### Production Checklist
- [ ] Configure production database credentials
- [ ] Set up log rotation
- [ ] Configure monitoring/alerting
- [ ] Schedule ETL runs (cron/scheduler)
- [ ] Set up backup for state file
- [ ] Configure firewall rules
- [ ] Test error recovery
- [ ] Document runbook for operators

### Scheduling Example (Linux cron)
```bash
# Run ETL daily at 2 AM
0 2 * * * cd /path/to/odoo_etl_project && /path/to/venv/bin/python main.py >> /var/log/odoo_etl_cron.log 2>&1
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## Maintenance

### Regular Tasks
- Monitor log files for errors
- Check `missing_data` table
- Verify data freshness
- Update dependencies quarterly
- Review and optimize slow queries
- Archive old logs

### Updates
- Test in staging before production
- Backup database before major updates
- Review changelog for breaking changes
- Update documentation
