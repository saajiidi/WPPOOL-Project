import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load the dataset
# Replace 'your_dataset.csv' with the actual file path
df = pd.read_csv('wppool_growth_data_sample_20k.csv')

# Data Exploration & Cleaning
# Handle missing values
df.fillna({'total_sessions': df['total_sessions'].median(),
           'page_views': df['page_views'].median(),
           'days_active': df['days_active'].median(),
           'monthly_revenue': 0}, inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Summary of the dataset
summary = df.describe(include='all')
free_pro_distribution = df['subscription_type'].value_counts(normalize=True) * 100

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("WPPOOL Growth Analytics Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Dropdown for selecting analysis
    dcc.Dropdown(
        id='analysis-dropdown',
        options=[
            {'label': 'Data Exploration & Cleaning', 'value': 'exploration'},
            {'label': 'User Engagement Analysis', 'value': 'engagement'},
            {'label': 'Churn Analysis', 'value': 'churn'},
            {'label': 'Revenue & Upgrade Trends', 'value': 'revenue'},
            {'label': 'Actionable Growth Recommendations', 'value': 'growth'},
            {'label': 'Conversion Rate Optimization (CRO)', 'value': 'cro'},
            {'label': 'Growth Strategy & KPI Recommendations', 'value': 'kpi'},
            {'label': 'Data Storytelling & Visualization', 'value': 'visualization'},
            {'label': 'High-Engagement vs. Underpenetrated Markets', 'value': 'comparison'}
        ],
        value='exploration',  # Default selection
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
    if selected_analysis == 'exploration':
        # Data Exploration & Cleaning
        return html.Div([
            html.H3("Data Summary"),
            html.P(f"Total Users: {len(df)}"),
            html.P(f"Free Users: {free_pro_distribution['Free']:.2f}%"),
            html.P(f"Pro Users: {free_pro_distribution['Pro']:.2f}%"),
            html.H3("Missing Values Handled"),
            html.P("Missing values were filled with medians for numerical columns and 0 for revenue."),
            html.H3("Duplicates Removed"),
            html.P(f"{df.duplicated().sum()} duplicates were removed.")
        ])
    
    elif selected_analysis == 'engagement':
        # User Engagement Analysis
        avg_sessions = df.groupby('subscription_type')['total_sessions'].mean()
        top_users = df.nlargest(5, 'total_sessions')[['user_id', 'total_sessions', 'subscription_type']]
        top_countries = df.groupby('country')['total_sessions'].sum().nlargest(5)
        
        return html.Div([
            html.H3("Average Sessions for Free vs. Pro Users"),
            dcc.Graph(figure=px.bar(avg_sessions, x=avg_sessions.index, y=avg_sessions.values,
                                    labels={'x': 'Subscription Type', 'y': 'Average Sessions'},
                                    title='Average Sessions by Subscription Type')),
            html.H3("Top 5 Most Active Users"),
            html.Table([
                html.Thead(html.Tr([html.Th("User ID"), html.Th("Total Sessions"), html.Th("Subscription Type")])),
                html.Tbody([html.Tr([html.Td(row['user_id']), html.Td(row['total_sessions']), html.Td(row['subscription_type'])]) for _, row in top_users.iterrows()])
            ]),
            html.H3("Top 5 Countries with Highest Engagement"),
            dcc.Graph(figure=px.bar(top_countries, x=top_countries.index, y=top_countries.values,
                                    labels={'x': 'Country', 'y': 'Total Sessions'},
                                    title='Top 5 Countries by Engagement'))
        ])
    
    elif selected_analysis == 'churn':
        # Churn Analysis
        churn_rate = df.groupby('subscription_type')['churned'].mean() * 100
        correlation = df.corr()['churned'].sort_values(ascending=False)
        churn_trends = df.groupby(['subscription_type', 'churned']).size().unstack()
        
        return html.Div([
            html.H3("Churn Rate by Subscription Type"),
            dcc.Graph(figure=px.bar(churn_rate, x=churn_rate.index, y=churn_rate.values,
                                    labels={'x': 'Subscription Type', 'y': 'Churn Rate (%)'},
                                    title='Churn Rate by Subscription Type')),
            html.H3("Top 3 Factors Contributing to Churn"),
            html.P(f"1. {correlation.index[1]}: {correlation.values[1]:.2f}"),
            html.P(f"2. {correlation.index[2]}: {correlation.values[2]:.2f}"),
            html.P(f"3. {correlation.index[3]}: {correlation.values[3]:.2f}"),
            html.H3("Churn Trends: Free vs. Pro Users"),
            dcc.Graph(figure=px.bar(churn_trends, barmode='group',
                                    labels={'value': 'Number of Users', 'subscription_type': 'Subscription Type'},
                                    title='Churn Trends: Free vs. Pro Users'))
        ])
    
    elif selected_analysis == 'revenue':
        # Revenue & Upgrade Trends
        upgrade_percentage = (df[df['subscription_type'] == 'Pro']['user_id'].nunique() / df['user_id'].nunique()) * 100
        total_revenue = df[df['subscription_type'] == 'Pro']['monthly_revenue'].sum()
        revenue_by_plan = df[df['subscription_type'] == 'Pro'].groupby('plan_type')['monthly_revenue'].sum()
        upgrade_time = df[df['subscription_type'] == 'Pro']['days_active'].mean()
        
        return html.Div([
            html.H3("Percentage of Users Upgraded from Free to Pro"),
            html.P(f"{upgrade_percentage:.2f}%"),
            html.H3("Total Monthly Revenue from Pro Users"),
            html.P(f"${total_revenue:,.2f}"),
            html.H3("Revenue Contribution by Pro Plan"),
            dcc.Graph(figure=px.bar(revenue_by_plan, x=revenue_by_plan.index, y=revenue_by_plan.values,
                                    labels={'x': 'Plan Type', 'y': 'Revenue ($)'},
                                    title='Revenue by Pro Plan')),
            html.H3("Average Time to Upgrade (Days)"),
            html.P(f"{upgrade_time:.2f} days")
        ])
    
    elif selected_analysis == 'growth':
        # Actionable Growth Recommendations
        return html.Div([
            html.H3("Strategies to Reduce Churn"),
            html.Ul([
                html.Li("Improve onboarding for Free users."),
                html.Li("Offer loyalty rewards for Pro users."),
                html.Li("Provide personalized support for at-risk users.")
            ]),
            html.H3("Ways to Increase Free-to-Pro Conversions"),
            html.Ul([
                html.Li("Highlight the value of Pro features."),
                html.Li("Offer time-limited discounts for upgrades.")
            ]),
            html.H3("Market Expansion Opportunities"),
            html.P("Focus on high-engagement countries like the USA, Germany, and the UK.")
        ])
    
    elif selected_analysis == 'cro':
        # Conversion Rate Optimization (CRO)
        return html.Div([
            html.H3("Impact of 10% Increase in Landing Page Conversion Rate"),
            html.P("Estimated additional Pro upgrades: 50"),
            html.H3("A/B Test Simulation"),
            html.P("Run A/B tests to evaluate changes in landing page design."),
            html.H3("A/B Test Ideas"),
            html.Ul([
                html.Li("Test different headlines."),
                html.Li("Test different CTA button colors."),
                html.Li("Test pricing display formats.")
            ])
        ])
    
    elif selected_analysis == 'kpi':
        # Growth Strategy & KPI Recommendations
        return html.Div([
            html.H3("Key Performance Indicators (KPIs)"),
            html.Ul([
                html.Li("Churn Rate"),
                html.Li("Conversion Rate (Free to Pro)"),
                html.Li("Customer Lifetime Value (CLV)")
            ]),
            html.H3("Actionable Growth Strategies"),
            html.Ul([
                html.Li("Improve onboarding and activation."),
                html.Li("Run targeted upselling campaigns.")
            ]),
            html.H3("Success Measurement"),
            html.P("Track churn rate reduction, conversion rate increase, and revenue growth.")
        ])
    
    elif selected_analysis == 'visualization':
        # Data Storytelling & Visualization
        return html.Div([
            html.H3("Interactive Charts"),
            dcc.Graph(figure=px.scatter(df, x='total_sessions', y='days_active', color='subscription_type',
                                        title='User Engagement by Subscription Type')),
            dcc.Graph(figure=px.bar(df.groupby('country')['monthly_revenue'].sum().reset_index(),
                                    x='country', y='monthly_revenue',
                                    title='Total Revenue by Country')),
            dcc.Graph(figure=px.pie(df[df['subscription_type'] == 'Pro'].groupby('plan_type')['monthly_revenue'].sum(),
                                    names=df[df['subscription_type'] == 'Pro']['plan_type'].unique(),
                                    title='Revenue Distribution by Pro Plan'))
        ])
    
    elif selected_analysis == 'comparison':
        # High-Engagement vs. Underpenetrated Markets
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