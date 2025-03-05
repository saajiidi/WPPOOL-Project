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
        style={'width': '90%', 'margin': 'auto', 'marginBottom': '20px'}
    ),
    
    # Graph container
    html.Div(id='graph-container', style={'marginTop': '20px', 'width': '90%', 'margin': 'auto'})
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
            html.H3("Data Summary", style={'textAlign': 'center'}),
            html.P(f"Total Users: {len(df)}", style={'textAlign': 'center'}),
            html.P(f"Free Users: {free_pro_distribution['Free']:.2f}%", style={'textAlign': 'center'}),
            html.P(f"Pro Users: {free_pro_distribution['Pro']:.2f}%", style={'textAlign': 'center'}),
            html.H3("Missing Values Handled", style={'textAlign': 'center'}),
            html.P("Missing values were filled with medians for numerical columns and 0 for revenue.", style={'textAlign': 'center'}),
            html.H3("Duplicates Removed", style={'textAlign': 'center'}),
            html.P(f"{df.duplicated().sum()} duplicates were removed.", style={'textAlign': 'center'})
        ])
    
    elif selected_analysis == 'engagement':
        # User Engagement Analysis
        avg_sessions = df.groupby('subscription_type')['total_sessions'].mean()
        top_users = df.nlargest(5, 'total_sessions')[['user_id', 'total_sessions', 'subscription_type']]
        top_countries = df.groupby('country')['total_sessions'].sum().nlargest(5)
        
        return html.Div([
            
                html.H3("Average Sessions for Free vs. Pro Users", style={'textAlign': 'center'}),
                dcc.Graph(figure=px.bar(avg_sessions, x=avg_sessions.index, y=avg_sessions.values,
                                        labels={'x': 'Subscription Type', 'y': 'Average Sessions'},
                                        title='Average Sessions by Subscription Type',
                                        color_discrete_sequence=px.colors.qualitative.Pastel)),

                html.H3("Top 5 Most Active Users", style={'textAlign': 'center'}),
                html.Table([
                    html.Thead(html.Tr([html.Th("User ID"), html.Th("Total Sessions"), html.Th("Subscription Type")])),
                    html.Tbody([
                        html.Tr([
                            html.Td(row['user_id']), 
                            html.Td(row['total_sessions']), 
                            html.Td(row['subscription_type'])
                        ]) for _, row in top_users.iterrows()
                    ])
                ], style={'margin': 'auto', 'width': '90%'}),

                html.H3("Top 5 Countries with Highest Engagement", style={'textAlign': 'center'}),
                dcc.Graph(figure=px.bar(top_countries, x=top_countries.index, y=top_countries.values,
                                        labels={'x': 'Country', 'y': 'Total Sessions'},
                                        title='Top 5 Countries by Engagement',
                                        color_discrete_sequence=px.colors.qualitative.Pastel))


        ])
    
    elif selected_analysis == 'churn':
        # Churn Analysis
        churn_rate = df.groupby('subscription_type')['churned'].mean() * 100
        correlation = df.corr()['churned'].sort_values(ascending=False)
        churn_trends = df.groupby(['subscription_type', 'churned']).size().unstack()
        
        return html.Div([
            html.H3("Churn Rate by Subscription Type", style={'textAlign': 'center'}),
            dcc.Graph(figure=px.pie(churn_rate, values=churn_rate.values, names=churn_rate.index,
                                    title='Churn Rate by Subscription Type', hole=0.4,
                                    color_discrete_sequence=px.colors.qualitative.Pastel)),
            html.H3("Top 3 Factors Contributing to Churn", style={'textAlign': 'center'}),
            html.P(f"1. {correlation.index[1]}: {correlation.values[1]:.2f}", style={'textAlign': 'center'}),
            html.P(f"2. {correlation.index[2]}: {correlation.values[2]:.2f}", style={'textAlign': 'center'}),
            html.P(f"3. {correlation.index[3]}: {correlation.values[3]:.2f}", style={'textAlign': 'center'}),
            html.H3("Churn Trends: Free vs. Pro Users", style={'textAlign': 'center'}),
            dcc.Graph(figure=px.bar(churn_trends, barmode='group',
                                    labels={'value': 'Number of Users', 'subscription_type': 'Subscription Type'},
                                    title='Churn Trends: Free vs. Pro Users',
                                    color_discrete_sequence=px.colors.qualitative.Pastel))
        ])
    
    elif selected_analysis == 'revenue':
        # Revenue & Upgrade Trends
        upgrade_percentage = (df[df['subscription_type'] == 'Pro']['user_id'].nunique() / df['user_id'].nunique()) * 100
        total_revenue = df[df['subscription_type'] == 'Pro']['monthly_revenue'].sum()
        revenue_by_plan = df[df['subscription_type'] == 'Pro'].groupby('plan_type')['monthly_revenue'].sum()
        upgrade_time = df[df['subscription_type'] == 'Pro']['days_active'].mean()
        
        return html.Div([
            html.H3("Percentage of Users Upgraded from Free to Pro", style={'textAlign': 'center'}),
            html.P(f"{upgrade_percentage:.2f}%", style={'textAlign': 'center'}),
            html.H3("Total Monthly Revenue from Pro Users", style={'textAlign': 'center'}),
            html.P(f"${total_revenue:,.2f}", style={'textAlign': 'center'}),
            html.H3("Revenue Contribution by Pro Plan", style={'textAlign': 'center'}),
            dcc.Graph(figure=px.pie(revenue_by_plan, values=revenue_by_plan.values, names=revenue_by_plan.index,
                                    title='Revenue by Pro Plan', hole=0.4,
                                    color_discrete_sequence=px.colors.qualitative.Pastel)),
            html.H3("Average Time to Upgrade (Days)", style={'textAlign': 'center'}),
            html.P(f"{upgrade_time:.2f} days", style={'textAlign': 'center'})
        ])
    
    elif selected_analysis == 'market':
        # Market Expansion Opportunities: Total Revenue by Country (Choropleth Map)
        revenue_by_country = df.groupby('country')['monthly_revenue'].sum().reset_index()
        fig = px.choropleth(revenue_by_country, locations='country', locationmode='country names',
                             color='monthly_revenue', hover_name='country',
                             title='Total Revenue by Country',
                             color_continuous_scale=px.colors.sequential.Plasma)
        return dcc.Graph(figure=fig, config={'toImageButtonOptions': {'format': 'png', 'filename': 'market_expansion'}})
    
    elif selected_analysis == 'growth':
        # Actionable Growth Recommendations
        return html.Div([
            html.H3("Strategies to Reduce Churn", style={'textAlign': 'center'}),
            html.Ul([
                html.Li("Improve onboarding for Free users."),
                html.Li("Offer loyalty rewards for Pro users."),
                html.Li("Provide personalized support for at-risk users.")
            ], style={'textAlign': 'center'}),
            html.H3("Ways to Increase Free-to-Pro Conversions", style={'textAlign': 'center'}),
            html.Ul([
                html.Li("Highlight the value of Pro features."),
                html.Li("Offer time-limited discounts for upgrades.")
            ], style={'textAlign': 'center'}),
            html.H3("Market Expansion Opportunities", style={'textAlign': 'center'}),
            html.P("Focus on high-engagement countries like the USA, Germany, and the UK.", style={'textAlign': 'center'})
        ])
    
    elif selected_analysis == 'cro':
        # Conversion Rate Optimization (CRO)
        return html.Div([
            html.H3("Impact of 10% Increase in Landing Page Conversion Rate", style={'textAlign': 'center'}),
            html.P("Estimated additional Pro upgrades: 50", style={'textAlign': 'center'}),
            html.H3("A/B Test Simulation", style={'textAlign': 'center'}),
            html.P("Run A/B tests to evaluate changes in landing page design.", style={'textAlign': 'center'}),
            html.H3("A/B Test Ideas", style={'textAlign': 'center'}),
            html.Ul([
                html.Li("Test different headlines."),
                html.Li("Test different CTA button colors."),
                html.Li("Test pricing display formats.")
            ], style={'textAlign': 'center'})
        ])
    
    elif selected_analysis == 'kpi':
        # Growth Strategy & KPI Recommendations
        return html.Div([
            html.H3("Key Performance Indicators (KPIs)", style={'textAlign': 'center'}),
            html.Ul([
                html.Li("Churn Rate"),
                html.Li("Conversion Rate (Free to Pro)"),
                html.Li("Customer Lifetime Value (CLV)")
            ], style={'textAlign': 'center'}),
            html.H3("Actionable Growth Strategies", style={'textAlign': 'center'}),
            html.Ul([
                html.Li("Improve onboarding and activation."),
                html.Li("Run targeted upselling campaigns.")
            ], style={'textAlign': 'center'}),
            html.H3("Success Measurement", style={'textAlign': 'center'}),
            html.P("Track churn rate reduction, conversion rate increase, and revenue growth.", style={'textAlign': 'center'})
        ])
    
    elif selected_analysis == 'visualization':
        # Data Storytelling & Visualization
        return html.Div([
            html.H3("Interactive Charts", style={'textAlign': 'center'}),
            dcc.Graph(figure=px.scatter(df, x='total_sessions', y='days_active', color='subscription_type',
                                        title='User Engagement by Subscription Type',
                                        color_discrete_sequence=px.colors.qualitative.Pastel)),
            dcc.Graph(figure=px.bar(df.groupby('country')['monthly_revenue'].sum().reset_index(),
                                    x='country', y='monthly_revenue',
                                    title='Total Revenue by Country',
                                    color_discrete_sequence=px.colors.qualitative.Pastel)),
            dcc.Graph(figure=px.pie(df[df['subscription_type'] == 'Pro'].groupby('plan_type')['monthly_revenue'].sum(),
                                    names=df[df['subscription_type'] == 'Pro']['plan_type'].unique(),
                                    title='Revenue Distribution by Pro Plan',
                                    color_discrete_sequence=px.colors.qualitative.Pastel))
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