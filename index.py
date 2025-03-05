import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
# Replace 'your_dataset.csv' with the actual file path
df = pd.read_csv('cleaned_dataset.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("WPPOOL Growth Analytics Dashboard", style={'textAlign': 'center'}),
    
    # Dropdown for selecting analysis
    dcc.Dropdown(
        id='analysis-dropdown',
        options=[
            {'label': 'Churn Analysis', 'value': 'churn'},
            {'label': 'Revenue & Upgrade Trends', 'value': 'revenue'},
            {'label': 'User Engagement Analysis', 'value': 'engagement'},
            {'label': 'Conversion Rate Optimization', 'value': 'conversion'}
        ],
        value='churn',  # Default selection
        style={'width': '50%', 'margin': 'auto'}
    ),
    
    # Graph container
    html.Div(id='graph-container')
])

# Callback to update the graph based on dropdown selection
@app.callback(
    Output('graph-container', 'children'),
    [Input('analysis-dropdown', 'value')]
)
def update_graph(selected_analysis):
    if selected_analysis == 'churn':
        # Churn Rate by Subscription Type
        churn_data = df.groupby('subscription_type')['churned'].mean() * 100
        fig = px.bar(churn_data, x=churn_data.index, y=churn_data.values, 
                      labels={'x': 'Subscription Type', 'y': 'Churn Rate (%)'},
                      title='Churn Rate by Subscription Type')
        return dcc.Graph(figure=fig)
    
    elif selected_analysis == 'revenue':
        # Monthly Revenue by Plan Type
        revenue_data = df[df['subscription_type'] == 'Pro'].groupby('plan_type')['monthly_revenue'].sum()
        fig = px.bar(revenue_data, x=revenue_data.index, y=revenue_data.values, 
                      labels={'x': 'Plan Type', 'y': 'Monthly Revenue ($)'},
                      title='Monthly Revenue by Plan Type')
        return dcc.Graph(figure=fig)
    
    elif selected_analysis == 'engagement':
        # User Engagement by Subscription Type
        fig = px.box(df, x='subscription_type', y='total_sessions', 
                      labels={'x': 'Subscription Type', 'y': 'Total Sessions'},
                      title='User Engagement by Subscription Type')
        return dcc.Graph(figure=fig)
    
    elif selected_analysis == 'conversion':
        # Conversion Rate by Country (Top 5 Countries)
        top_countries = df['country'].value_counts().nlargest(5).index
        conversion_data = df[df['country'].isin(top_countries)].groupby('country')['subscription_type'].apply(lambda x: (x == 'Pro').mean() * 100)
        fig = px.bar(conversion_data, x=conversion_data.index, y=conversion_data.values, 
                      labels={'x': 'Country', 'y': 'Conversion Rate (%)'},
                      title='Conversion Rate by Country (Top 5 Countries)')
        return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)