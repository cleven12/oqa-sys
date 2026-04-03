#!/bin/bash
# Fix MySQL timezone tables

echo "Loading timezone data into MySQL..."
echo "This requires your MySQL root password."
echo ""

# Read database credentials from .env
if [ -f .env ]; then
    source .env
fi

# Load timezone data
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u ${DB_USER:-root} -p${DB_PASSWORD} mysql

if [ $? -eq 0 ]; then
    echo "✅ Timezone data loaded successfully!"
    echo "Now restart your Django server."
else
    echo "❌ Failed to load timezone data."
    echo ""
    echo "Alternative: Connect to MySQL and run manually:"
    echo "  mysql -u root -p mysql < <(mysql_tzinfo_to_sql /usr/share/zoneinfo)"
fi
