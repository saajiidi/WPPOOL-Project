import subprocess
import sys

# List of required libraries
required_libs = ["pandas", "dash", "plotly"]

# Install missing libraries
for lib in required_libs:
    try:
        __import__(lib)
    except ImportError:
        print(f"Installing missing library: {lib}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go


# Load the dataset
df = pd.read_csv('wppool_growth_data_sample_20k.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("WPPOOL Growth Analytics Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Dropdown for selecting analysis
    dcc.Dropdown(
        id='analysis-dropdown',
        options=[
            {'label': 'Churn Analysis', 'value': 'churn'},
            {'label': 'Conversion Rate Optimization', 'value': 'conversion'},
            {'label': 'Revenue & Upgrade Trends', 'value': 'revenue'},
            {'label': 'User Engagement Analysis', 'value': 'engagement'},
            {'label': 'Market Expansion Opportunities', 'value': 'market'},
            {'label': 'High-Engagement vs. Underpenetrated Markets', 'value': 'comparison'}
        ],
        value='churn',  # Default selection
        style={'width': '50%', 'margin': 'auto', 'marginBottom': '20px'}
    ),
    
    # Graph container
    html.Div(id='graph-container', style={'marginTop': '20px'})
])

# Callback to update the graph based on dropdown selection
@app.callback(
    Output('graph-container', 'children'),
    [Input('analysis-dropdown', 'value')]
)
def update_graph(selected_analysis):
    if selected_analysis == 'churn':
        # Churn Rate by Subscription Type (Pie Chart)
        churn_data = df.groupby('subscription_type')['churned'].mean() * 100
        fig = px.pie(churn_data, values=churn_data.values, names=churn_data.index, 
                      title='Churn Rate by Subscription Type', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'churn_rate'}})
    
    elif selected_analysis == 'conversion':
        # Conversion Rate by Country (Stacked Bar Chart)
        top_countries = df['country'].value_counts().nlargest(5).index
        conversion_data = df[df['country'].isin(top_countries)].groupby(['country', 'subscription_type']).size().unstack()
        fig = px.bar(conversion_data, barmode='stack', 
                      labels={'value': 'Number of Users', 'country': 'Country'},
                      title='Conversion Rate by Country (Top 5 Countries)',
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'conversion_rate'}})
    
    elif selected_analysis == 'revenue':
        # Monthly Revenue by Plan Type (Pie Chart)
        revenue_data = df[df['subscription_type'] == 'Pro'].groupby('plan_type')['monthly_revenue'].sum()
        fig = px.pie(revenue_data, values=revenue_data.values, names=revenue_data.index, 
                      title='Monthly Revenue by Plan Type', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'revenue_distribution'}})
    
    elif selected_analysis == 'engagement':
        # User Engagement by Subscription Type (Scatter Plot)
        fig = px.scatter(df, x='total_sessions', y='days_active', color='subscription_type',
                          labels={'total_sessions': 'Total Sessions', 'days_active': 'Days Active'},
                          title='User Engagement by Subscription Type',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'user_engagement'}})
    
    elif selected_analysis == 'market':
        # Market Expansion Opportunities: Total Revenue by Country (Choropleth Map)
        revenue_by_country = df.groupby('country')['monthly_revenue'].sum().reset_index()
        fig = px.choropleth(revenue_by_country, locations='country', locationmode='country names',
                             color='monthly_revenue', hover_name='country',
                             title='Total Revenue by Country',
                             color_continuous_scale=px.colors.sequential.Plasma)
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'market_expansion'}})
    
    elif selected_analysis == 'comparison':
        # High-Engagement vs. Underpenetrated Markets (Grouped Bar Chart)
        high_engagement = df.groupby('country')['total_sessions'].sum().nlargest(5).reset_index()
        underpenetrated = df.groupby('country')['total_sessions'].sum().nsmallest(5).reset_index()
        high_engagement['market_type'] = 'High Engagement'
        underpenetrated['market_type'] = 'Underpenetrated'
        combined_data = pd.concat([high_engagement, underpenetrated])
        
        fig = px.bar(combined_data, x='country', y='total_sessions', color='market_type',
                      labels={'x': 'Country', 'y': 'Total Sessions'},
                      title='High-Engagement vs. Underpenetrated Markets',
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'market_comparison'}})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)