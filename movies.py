import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# static dataset about movies
# make sure its in the same directory
movies = pd.read_csv("movies.csv")

# missing values handled 
movies['rating'] = movies['rating'].fillna('Missing')

# Dash app
app = dash.Dash(__name__)
server = app.server

# my custom styles
styles = {
    'instructions': {
        'backgroundColor': '#fff',
        'padding': '15px',
        'borderRadius': '5px',
        'border': '1px solid #ddd',
        'marginBottom': '20px',
        'fontFamily': 'Arial, sans-serif',
        'color': '#333'
    },
    'heading': {'textAlign': 'center', 
                'color': '#2c3e50', 
                'fontFamily': 'Arial, sans-serif',
                'marginBottom': '20px'
    },
    'core': {'width': '24%', 
             'display': 'inline-block', 
             'fontFamily': 'Arial, sans-serif',
             'padding': '10px', 
              'color': '#333',
             'verticalAlign': 'top'
    }
}

# Layout
app.layout = html.Div([
    
    # Heading
    html.H1("Movies Industry Analysis", style=styles['heading']),
    
    # Narrative/Instructions to gguide the user
    html.Div([
        html.H3("Welcome to the Movies Industry Analysis Dashboard!"),
        html.P("This interactive application allows you to explore "
               "trends in the movie industry from 1986 to 2016. "
                "You can filter the data by genre, year range, age rating, and "
                "director to analyze revenue, IMDb ratings, "
                "and budget vs. gross revenue trends."),
        html.P("Use the filters below to customize your analysis and explore the visualizations."),
    ], style=styles['instructions']),
        
    # Core components
    html.Div([
        html.Div([
            html.Label("Select Genre:",style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': g, 'value': g} for g in movies['genre'].unique()],
                value='Action',
                clearable=False
            ),
        ], style=styles['core']),
        
        html.Div([
            html.Label("Choose Rating Type:",style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='rating-radio',
                options=[{'label': r, 'value': r} for r in movies['rating'].unique()],
                value='PG-13',
                inline=True
            ),
        ], style=styles['core']),
        
        html.Div([
            html.Label("Filter by Director (Optional):",style={'fontWeight': 'bold'}),
            dcc.Input(id='director-input', type='text', placeholder='Enter director name')
        ], style=styles['core']),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'flexWrap': 'wrap'}),
    
    html.Div([
        html.Label("Select Year Range:",style={'fontWeight': 'bold', 
                                               'fontFamily': 'Arial, sans-serif',
                                               'color': '#333'}),
        dcc.RangeSlider(
            id='year-slider',
            min=movies['year'].min(),
            max=movies['year'].max(),
            value=[2000, 2016],
            marks={str(year): str(year) for year in range(movies['year'].min(), movies['year'].max()+1, 5)},
            step=1
        ),
    ], style={'width': '90%', 'margin': 'auto', 'padding': '20px'}),
    
    # -- graphs styles
    html.Div([
        dcc.Graph(id='revenue-trend', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='rating-distribution', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='budget-vs-gross', style={'width': '33%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'center', 'flexWrap': 'wrap'})
])

# Callbacks for interactivity
@app.callback(
    [Output('revenue-trend', 'figure'),
     Output('rating-distribution', 'figure'),
     Output('budget-vs-gross', 'figure')],
    [Input('genre-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('rating-radio', 'value'),
     Input('director-input', 'value')]
)

def update_graphs(selected_genre, year_range, selected_rating, director_name):
    filtered_data = movies[(movies['genre'] == selected_genre) &
                           (movies['year'].between(year_range[0], year_range[1])) &
                           (movies['rating'] == selected_rating)]
    
    if director_name:
        filtered_data = filtered_data[filtered_data['director'].str.contains(director_name, case=False, na=False)]
    
    # Revenue trend plot
    revenue_fig = px.line(filtered_data.groupby('year')['gross'].sum().reset_index(),
                           x='year', y='gross', title='Total Revenue Trend')
    
    # Rating distribution plot
    rating_fig = px.histogram(filtered_data, x='score', title='Distribution of IMDb Ratings')
    
    # Budget vs Gross Revenue scatter plot with movie name in tooltip
    budget_gross_fig = px.scatter(filtered_data, x='budget', y='gross', color='score',
                                  size='votes', title='Budget vs Gross Revenue',
                                  hover_data=['name'])
    
    return revenue_fig, rating_fig, budget_gross_fig

if __name__ == '__main__':
    app.run_server(debug=True)
