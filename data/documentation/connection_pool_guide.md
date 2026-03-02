# CI/CD Testing Guide

## Connection Pool Management

### Overview
The database connection pool is a critical component of our CI/CD infrastructure. It manages database connections to prevent resource exhaustion and ensure optimal performance.

### Configuration
- **Maximum Connections**: 10 per service instance
- **Connection Timeout**: 30 seconds
- **Idle Timeout**: 5 minutes
- **Retry Policy**: Exponential backoff (1s, 2s, 4s, 8s)

### Common Issues and Solutions

#### Issue: Connection Pool Exhausted
**Symptom**: "TimeoutError: Connection pool exhausted"

**Root Causes**:
1. Long-running queries holding connections
2. Unclosed database connections in application code
3. Connection leak in database driver
4. Too many concurrent requests

**Solutions**:
1. **Reduce query timeout**: Lower the max execution time for queries
2. **Increase pool size**: Adjust MAX_CONNECTIONS environment variable
3. **Connection reuse**: Enable connection pooling in ORM configuration
4. **Query optimization**: Add database indexes to reduce query time
5. **Circuit breaker**: Implement circuit breaker pattern for database calls

#### Issue: Connection Leak
**Symptom**: Pool size gradually decreases, eventual timeout

**Root Causes**:
1. Missing connection.close() calls
2. Database transaction not properly closed
3. Connection held during exception

**Solutions**:
1. Use context managers for database connections
2. Add finally blocks to close connections
3. Implement proper error handling

## Test Environment Setup

### Database Configuration
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
```

### Running Tests
```bash
# Initialize test database
python scripts/init_test_db.py

# Run tests with proper cleanup
pytest tests/ --tb=short

# Run with database debugging
pytest tests/ -v --log-cli-level=DEBUG
```

## Performance Benchmarks

- Average test suite execution: 45 seconds
- Expected connection acquisition time: < 100ms
- Maximum acceptable connection pool wait: 30 seconds

## Debugging Connection Issues

1. Check connection pool metrics
2. Review slow query logs
3. Monitor connection lifecycle in application
4. Verify connection close() is called in all code paths
