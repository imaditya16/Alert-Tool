# SQL Server Setup Guide

## Prerequisites

1. **Install Microsoft ODBC Driver for SQL Server**
   - Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
   - Choose Driver 17 or 18 (recommended: Driver 18)

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Connection String Options

### Option 1: Direct Connection String (Recommended)

Update your `config.env` file:

```env
DATABASE_URL=mssql+pyodbc://USERNAME:PASSWORD@SERVER_HOST:PORT/DATABASE_NAME?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

**Example:**
```env
DATABASE_URL=mssql+pyodbc://myuser:mypass@sqlserver.company.com:1433/MyDatabase?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

### Option 2: Using DSN (Data Source Name)

1. **Create a DSN** using ODBC Data Source Administrator:
   - Open "ODBC Data Sources" (64-bit)
   - Go to "System DSN" tab
   - Click "Add" → Select "ODBC Driver 18 for SQL Server"
   - Configure your server details
   - Test the connection

2. **Update config.env:**
```env
DATABASE_URL=mssql+pyodbc:///?odbc_connect=DSN=YourDsnName
```

## Connection String Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `USERNAME` | SQL Server username | `myuser` |
| `PASSWORD` | SQL Server password | `mypass` |
| `SERVER_HOST` | SQL Server hostname/IP | `sqlserver.company.com` |
| `PORT` | SQL Server port (usually 1433) | `1433` |
| `DATABASE_NAME` | Target database name | `MyDatabase` |
| `driver` | ODBC driver name | `ODBC+Driver+18+for+SQL+Server` |
| `TrustServerCertificate` | Trust server certificate | `yes` (for self-signed certs) |

## Common Connection String Examples

### Windows Authentication
```env
DATABASE_URL=mssql+pyodbc://@SERVER_HOST/DATABASE_NAME?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Authentication=ActiveDirectoryIntegrated
```

### SQL Server Authentication with specific port
```env
DATABASE_URL=mssql+pyodbc://user:pass@server:1433/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

### Using instance name instead of port
```env
DATABASE_URL=mssql+pyodbc://user:pass@server\INSTANCE_NAME/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

## Testing Your Connection

1. **Update config.env** with your SQL Server details
2. **Set CHECK_MODE=stored_procedure**
3. **Run the application:**
   ```bash
   python run.py
   ```

## Troubleshooting

### Common Issues:

1. **"ODBC Driver not found"**
   - Install Microsoft ODBC Driver for SQL Server
   - Use correct driver name in connection string

2. **"Login failed"**
   - Check username/password
   - Verify SQL Server authentication mode
   - Check if user has access to the database

3. **"Cannot connect to server"**
   - Verify server hostname/IP and port
   - Check firewall settings
   - Ensure SQL Server is running

4. **"Trust server certificate"**
   - Add `TrustServerCertificate=yes` to connection string
   - Or configure proper SSL certificates

### Testing Connection Manually:

```python
import pyodbc

# Test connection
conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_pass;TrustServerCertificate=yes"
try:
    conn = pyodbc.connect(conn_str)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
```

## Security Notes

- Never commit passwords to version control
- Use environment variables for sensitive data
- Consider using Windows Authentication when possible
- Use encrypted connections in production
