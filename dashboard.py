#!/usr/bin/env python3
"""
Gemini Analytics Dashboard
===========================

Interactive Dash dashboard for visualizing farm analytics.
Can be embedded in Creao app or accessed standalone.

Usage:
    python dashboard.py
    
Then visit: http://localhost:8050
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import os

# Import analytics functions
try:
    from analyze_csv import analyze_csv
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Initialize Dash app
app = dash.Dash(__name__, title="Farm Analytics Dashboard")
app.config.suppress_callback_exceptions = True

# Sample farmers data (replace with real data from Creao)
FARMERS = [
    {"id": "farmer001", "name": "John's Farm"},
    {"id": "farmer002", "name": "Maria's Farm"},
    {"id": "farmer003", "name": "Chen's Farm"},
]

CROPS = ["All", "tomato", "mango", "lettuce", "carrot", "broccoli"]

# Colors
COLORS = {
    'primary': '#4CAF50',
    'secondary': '#8BC34A',
    'accent': '#FFC107',
    'background': '#f8f9fa',
    'text': '#212529'
}

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("🌾 Farm Analytics Dashboard", 
                   style={'color': 'white', 'margin': '0', 'fontSize': '32px'}),
            html.P("AI-Powered Insights for Farmers", 
                  style={'color': 'white', 'margin': '5px 0 0 0', 'fontSize': '16px'})
        ], style={'flex': '1'}),
        html.Div([
            html.Img(src='/assets/logo.png', style={'height': '50px'}) if os.path.exists('assets/logo.png') else None
        ])
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%)',
        'padding': '20px 40px',
        'display': 'flex',
        'alignItems': 'center',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("Select Farmer:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='farmer-dropdown',
                options=[{'label': f['name'], 'value': f['id']} for f in FARMERS],
                value=FARMERS[0]['id'],
                clearable=False,
                style={'width': '250px'}
            )
        ], style={'marginRight': '20px'}),
        
        html.Div([
            html.Label("Filter by Crop:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='crop-dropdown',
                options=[{'label': crop.title(), 'value': crop.lower()} for crop in CROPS],
                value='All',
                clearable=False,
                style={'width': '200px'}
            )
        ], style={'marginRight': '20px'}),
        
        html.Div([
            html.Label("Time Period:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='time-period',
                options=[
                    {'label': 'Last 4 Weeks', 'value': 4},
                    {'label': 'Last 8 Weeks', 'value': 8},
                    {'label': 'Last 12 Weeks', 'value': 12},
                ],
                value=12,
                clearable=False,
                style={'width': '180px'}
            )
        ], style={'marginRight': '20px'}),
        
        html.Button(
            '🔄 Refresh Analytics',
            id='refresh-button',
            n_clicks=0,
            style={
                'background': COLORS['primary'],
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '14px',
                'marginTop': '20px'
            }
        )
    ], style={
        'padding': '20px 40px',
        'background': 'white',
        'display': 'flex',
        'alignItems': 'flex-end',
        'borderBottom': '1px solid #e0e0e0'
    }),
    
    # Loading indicator
    dcc.Loading(
        id="loading",
        type="default",
        children=html.Div(id="loading-output")
    ),
    
    # Main Content
    html.Div([
        # Top Row - Key Metrics
        html.Div([
            html.Div([
                html.Div([
                    html.H3("📊", style={'fontSize': '32px', 'margin': '0'}),
                    html.P("Total Supply", style={'margin': '5px 0', 'color': '#666'}),
                    html.H4(id='metric-supply', children='--', 
                           style={'margin': '0', 'color': COLORS['primary']})
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'textAlign': 'center'
                })
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.Div([
                    html.H3("💰", style={'fontSize': '32px', 'margin': '0'}),
                    html.P("Sales Rate", style={'margin': '5px 0', 'color': '#666'}),
                    html.H4(id='metric-sales', children='--',
                           style={'margin': '0', 'color': COLORS['primary']})
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'textAlign': 'center'
                })
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.Div([
                    html.H3("⏱️", style={'fontSize': '32px', 'margin': '0'}),
                    html.P("Avg Delay", style={'margin': '5px 0', 'color': '#666'}),
                    html.H4(id='metric-delay', children='--',
                           style={'margin': '0', 'color': COLORS['primary']})
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'textAlign': 'center'
                })
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        
        # AI Insights Card
        html.Div([
            html.H3("💡 AI Insights", style={'marginBottom': '15px'}),
            html.Div(id='insights-container', children=[
                html.P("Click 'Refresh Analytics' to generate insights...", 
                      style={'color': '#666'})
            ])
        ], style={
            'background': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Charts Row 1
        html.Div([
            html.Div([
                dcc.Graph(id='supply-chart', config={'displayModeBar': False})
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                dcc.Graph(id='sales-chart', config={'displayModeBar': False})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        
        # Charts Row 2
        html.Div([
            html.Div([
                dcc.Graph(id='forecast-chart', config={'displayModeBar': False})
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                dcc.Graph(id='crop-distribution', config={'displayModeBar': False})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        
        # Recommendations Card
        html.Div([
            html.H3("🎯 Recommendations", style={'marginBottom': '15px'}),
            html.Div(id='recommendations-container', children=[
                html.P("Click 'Refresh Analytics' to generate recommendations...", 
                      style={'color': '#666'})
            ])
        ], style={
            'background': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        })
    ], style={
        'padding': '20px 40px',
        'background': COLORS['background']
    }),
    
    # Footer
    html.Div([
        html.P("Powered by Gemini AI | CalHacks 2025", 
              style={'margin': '0', 'color': '#666', 'textAlign': 'center'})
    ], style={
        'padding': '20px',
        'background': 'white',
        'borderTop': '1px solid #e0e0e0',
        'marginTop': '20px'
    }),
    
    # Hidden div to store data
    html.Div(id='analytics-data', style={'display': 'none'})
], style={'fontFamily': 'Arial, sans-serif', 'margin': '0', 'padding': '0'})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('analytics-data', 'children'),
     Output('loading-output', 'children')],
    [Input('refresh-button', 'n_clicks')],
    [State('farmer-dropdown', 'value'),
     State('crop-dropdown', 'value'),
     State('time-period', 'value')]
)
def update_analytics(n_clicks, farmer_id, crop_filter, weeks):
    """Generate analytics when refresh button is clicked"""
    if n_clicks == 0:
        return None, None
    
    try:
        # Load sample data (replace with Creao API call)
        csv_path = "sample_weekly.csv"
        
        if GEMINI_AVAILABLE:
            # Run analytics
            crop = None if crop_filter == 'All' else crop_filter
            analytics = analyze_csv(csv_path, crop=crop)
        else:
            # Use mock data
            analytics = {
                "insights": [
                    {"title": "Strong Demand", "explanation": "Sales are 90% of supply"},
                    {"title": "Improving Efficiency", "explanation": "Delivery times decreased"}
                ],
                "forecast": [
                    {"week_start": "2025-10-01", "crop": "tomato", "kg": 610},
                    {"week_start": "2025-10-08", "crop": "tomato", "kg": 620}
                ],
                "recommendations": [
                    "Focus on high-demand crops",
                    "Optimize delivery routes",
                    "Increase inventory by 10%"
                ]
            }
        
        # Convert to JSON for storage
        import json
        return json.dumps(analytics), None
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@app.callback(
    [Output('metric-supply', 'children'),
     Output('metric-sales', 'children'),
     Output('metric-delay', 'children'),
     Output('insights-container', 'children'),
     Output('recommendations-container', 'children'),
     Output('supply-chart', 'figure'),
     Output('sales-chart', 'figure'),
     Output('forecast-chart', 'figure'),
     Output('crop-distribution', 'figure')],
    [Input('analytics-data', 'children'),
     Input('crop-dropdown', 'value')]
)
def update_dashboard(analytics_json, crop_filter):
    """Update all dashboard components"""
    
    # Load sample data for charts
    df = pd.read_csv("sample_weekly.csv")
    
    # Filter by crop if needed
    if crop_filter and crop_filter != 'All':
        df = df[df['crop'] == crop_filter]
    
    # Calculate metrics
    total_supply = f"{df['total_supplied_kg'].sum():.0f} kg"
    sales_rate = f"{(df['total_sold_kg'].sum() / df['total_supplied_kg'].sum() * 100):.1f}%"
    avg_delay = f"{df['avg_delivery_delay_min'].mean():.0f} min"
    
    # Parse analytics
    insights_div = []
    recommendations_div = []
    forecast_data = []
    
    if analytics_json:
        import json
        analytics = json.loads(analytics_json)
        
        # Insights
        for i, insight in enumerate(analytics.get('insights', []), 1):
            insights_div.append(html.Div([
                html.H4(f"{i}. {insight['title']}", 
                       style={'color': COLORS['primary'], 'marginBottom': '5px'}),
                html.P(insight['explanation'], style={'color': '#666', 'marginBottom': '15px'})
            ]))
        
        # Recommendations
        for i, rec in enumerate(analytics.get('recommendations', []), 1):
            recommendations_div.append(html.Div([
                html.P(f"{i}. {rec}", style={
                    'padding': '10px 15px',
                    'background': '#E8F5E9',
                    'borderRadius': '5px',
                    'marginBottom': '10px',
                    'borderLeft': f'4px solid {COLORS["primary"]}'
                })
            ]))
        
        # Forecast data
        forecast_data = analytics.get('forecast', [])
    
    # Create charts
    
    # Supply Trend Chart
    supply_fig = go.Figure()
    for crop in df['crop'].unique():
        crop_data = df[df['crop'] == crop]
        supply_fig.add_trace(go.Scatter(
            x=crop_data['week_start'],
            y=crop_data['total_supplied_kg'],
            mode='lines+markers',
            name=crop.title(),
            line=dict(width=3)
        ))
    supply_fig.update_layout(
        title="Supply Trend (kg)",
        xaxis_title="Week",
        yaxis_title="Supply (kg)",
        hovermode='x unified',
        template='plotly_white',
        height=300
    )
    
    # Sales Performance Chart
    sales_fig = go.Figure()
    for crop in df['crop'].unique():
        crop_data = df[df['crop'] == crop]
        sales_fig.add_trace(go.Bar(
            x=crop_data['week_start'],
            y=crop_data['total_sold_kg'],
            name=crop.title()
        ))
    sales_fig.update_layout(
        title="Sales Performance (kg)",
        xaxis_title="Week",
        yaxis_title="Sold (kg)",
        barmode='group',
        template='plotly_white',
        height=300
    )
    
    # Forecast Chart
    if forecast_data:
        forecast_df = pd.DataFrame(forecast_data)
        forecast_fig = go.Figure()
        for crop in forecast_df['crop'].unique():
            crop_forecast = forecast_df[forecast_df['crop'] == crop]
            forecast_fig.add_trace(go.Scatter(
                x=crop_forecast['week_start'],
                y=crop_forecast['kg'],
                mode='lines+markers',
                name=crop.title(),
                line=dict(width=3, dash='dash')
            ))
        forecast_fig.update_layout(
            title="2-Week Forecast",
            xaxis_title="Week",
            yaxis_title="Predicted Supply (kg)",
            hovermode='x unified',
            template='plotly_white',
            height=300
        )
    else:
        forecast_fig = go.Figure()
        forecast_fig.update_layout(
            title="2-Week Forecast",
            annotations=[{
                'text': 'Click Refresh to generate forecast',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 14, 'color': '#666'}
            }],
            template='plotly_white',
            height=300
        )
    
    # Crop Distribution Pie Chart
    crop_totals = df.groupby('crop')['total_supplied_kg'].sum()
    pie_fig = go.Figure(data=[go.Pie(
        labels=[c.title() for c in crop_totals.index],
        values=crop_totals.values,
        hole=0.4
    )])
    pie_fig.update_layout(
        title="Supply Distribution by Crop",
        template='plotly_white',
        height=300
    )
    
    return (
        total_supply,
        sales_rate,
        avg_delay,
        insights_div if insights_div else html.P("Click 'Refresh Analytics' to generate insights...", style={'color': '#666'}),
        recommendations_div if recommendations_div else html.P("Click 'Refresh Analytics' to generate recommendations...", style={'color': '#666'}),
        supply_fig,
        sales_fig,
        forecast_fig,
        pie_fig
    )

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("="*60)
    print("🌾 Farm Analytics Dashboard")
    print("="*60)
    print("\n🚀 Starting server...")
    print(f"\n📊 Dashboard URL: http://localhost:8050")
    print(f"📱 Shareable URL: http://YOUR_PUBLIC_IP:8050")
    print("\n💡 For deployment:")
    print("   - Render: See DASHBOARD_DEPLOYMENT.md")
    print("   - Railway: railway up")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)

