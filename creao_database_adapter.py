#!/usr/bin/env python3
"""
Creao Database Adapter
======================

Adapts Creao's database structure to work with analytics API.

Handles:
1. User database (Farm Connect Users Database.csv)
2. Transaction/Order data (if available)
3. Generates analytics from Creao data
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime

class CreaoDataAdapter:
    """Adapter to convert Creao data to analytics format"""
    
    def __init__(self):
        self.users = {}
        self.transactions = {}
    
    def load_users_database(self, csv_path: str):
        """
        Load Creao users database.
        Expected columns: ID, Email, Role, Name, Creator, Updater, Created, Updated
        """
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            user_id = row['ID']
            self.users[user_id] = {
                'id': user_id,
                'email': row['Email'],
                'role': row['Role'],  # 'Buyer' or 'Farmer'
                'name': row['Name'],
                'created': row['Created'],
                'updated': row['Updated']
            }
        
        return {
            'total_users': len(self.users),
            'farmers': len([u for u in self.users.values() if u['role'] in ['Farmer', 'Seller']]),
            'buyers': len([u for u in self.users.values() if u['role'] == 'Buyer'])
        }
    
    def load_transactions_database(self, csv_path: str):
        """
        Load Creao transactions/orders database.
        
        Expected columns (adjust based on your actual transaction table):
        - order_id
        - farmer_id
        - buyer_id
        - crop/product
        - quantity_kg
        - price_per_kg
        - total_revenue
        - order_date
        - status
        - delivery_time
        """
        try:
            df = pd.read_csv(csv_path)
            
            # Group by farmer
            for farmer_id in df['farmer_id'].unique():
                farmer_orders = df[df['farmer_id'] == farmer_id]
                
                # Convert to weekly format for analytics
                weekly_data = self._aggregate_to_weekly(farmer_orders)
                
                self.transactions[farmer_id] = {
                    'farmer_name': self.users.get(farmer_id, {}).get('name', f'Farmer {farmer_id}'),
                    'weekly_data': weekly_data,
                    'total_orders': len(farmer_orders),
                    'total_revenue': farmer_orders['total_revenue'].sum()
                }
            
            return {
                'farmers_with_transactions': len(self.transactions),
                'total_orders': len(df)
            }
            
        except Exception as e:
            print(f"⚠️  No transaction data found: {e}")
            return None
    
    def _aggregate_to_weekly(self, orders_df: pd.DataFrame) -> List[Dict]:
        """Convert orders to weekly aggregated format"""
        # Convert timestamp to week
        orders_df['week_start'] = pd.to_datetime(orders_df['order_date'], unit='s').dt.to_period('W').dt.start_time
        
        weekly = []
        for (week, crop), group in orders_df.groupby(['week_start', 'crop']):
            weekly.append({
                'week_start': week.strftime('%Y-%m-%d'),
                'crop': crop,
                'total_supplied_kg': group['quantity_kg'].sum(),
                'total_sold_kg': group[group['status'] == 'completed']['quantity_kg'].sum(),
                'avg_delivery_delay_min': group.get('delivery_time', 0).mean()
            })
        
        return weekly
    
    def get_farmer_data_for_analytics(self, farmer_id: str) -> Dict:
        """Get farmer data in format ready for analytics API"""
        if farmer_id not in self.transactions:
            return None
        
        farmer_data = self.transactions[farmer_id]
        
        return {
            'farmer_id': farmer_id,
            'farmer_name': farmer_data['farmer_name'],
            'data': farmer_data['weekly_data'],
            'metadata': {
                'total_orders': farmer_data['total_orders'],
                'total_revenue': farmer_data['total_revenue']
            }
        }
    
    def get_all_farmers_for_upload(self) -> List[Dict]:
        """Get all farmers' data ready for bulk upload"""
        return [
            self.get_farmer_data_for_analytics(farmer_id)
            for farmer_id in self.transactions.keys()
        ]

def convert_creao_to_analytics_format(users_csv: str, transactions_csv: str = None):
    """
    Main function to convert Creao databases to analytics format.
    
    Args:
        users_csv: Path to Farm Connect Users Database.csv
        transactions_csv: Path to transactions/orders CSV (if available)
    
    Returns:
        Dictionary with all farmers' data ready for analytics
    """
    adapter = CreaoDataAdapter()
    
    # Load users
    print("📊 Loading Creao users database...")
    users_info = adapter.load_users_database(users_csv)
    print(f"✅ Loaded {users_info['total_users']} users:")
    print(f"   - Farmers: {users_info['farmers']}")
    print(f"   - Buyers: {users_info['buyers']}")
    
    # Load transactions if available
    if transactions_csv:
        print("\n📦 Loading transactions database...")
        trans_info = adapter.load_transactions_database(transactions_csv)
        if trans_info:
            print(f"✅ Loaded {trans_info['total_orders']} orders")
            print(f"   - Farmers with data: {trans_info['farmers_with_transactions']}")
        else:
            print("⚠️  No transaction data available")
    else:
        print("\n⚠️  No transaction database provided")
        print("   Using mock data for demonstration")
        # Generate sample data for each farmer
        adapter = _generate_mock_data_for_farmers(adapter)
    
    return adapter.get_all_farmers_for_upload()

def _generate_mock_data_for_farmers(adapter: CreaoDataAdapter) -> CreaoDataAdapter:
    """Generate mock transaction data for farmers for demo purposes"""
    import random
    from datetime import datetime, timedelta
    
    farmers = [uid for uid, u in adapter.users.items() if u['role'] in ['Farmer', 'Seller']]
    
    for farmer_id in farmers:
        # Generate 12 weeks of sample data
        weekly_data = []
        start_date = datetime.now() - timedelta(weeks=12)
        
        crops = ['tomato', 'mango', 'lettuce', 'carrot']
        
        for week in range(12):
            week_date = start_date + timedelta(weeks=week)
            crop = random.choice(crops)
            
            supplied = random.randint(100, 600)
            sold = int(supplied * random.uniform(0.7, 0.95))
            
            weekly_data.append({
                'week_start': week_date.strftime('%Y-%m-%d'),
                'crop': crop,
                'total_supplied_kg': supplied,
                'total_sold_kg': sold,
                'avg_delivery_delay_min': random.randint(10, 40)
            })
        
        adapter.transactions[farmer_id] = {
            'farmer_name': adapter.users[farmer_id]['name'],
            'weekly_data': weekly_data,
            'total_orders': len(weekly_data),
            'total_revenue': sum(w['total_sold_kg'] * 10 for w in weekly_data)  # $10/kg avg
        }
    
    return adapter

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python creao_database_adapter.py <users_csv> [transactions_csv]")
        print("Example: python creao_database_adapter.py 'Farm Connect Users Database.csv'")
        sys.exit(1)
    
    users_csv = sys.argv[1]
    transactions_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Convert
    farmers_data = convert_creao_to_analytics_format(users_csv, transactions_csv)
    
    print(f"\n✅ Converted {len(farmers_data)} farmers' data")
    print("\n📤 Ready to upload to analytics API!")
    
    # Save to JSON for easy upload
    import json
    with open('creao_farmers_data.json', 'w') as f:
        json.dump(farmers_data, f, indent=2)
    
    print("💾 Saved to: creao_farmers_data.json")

