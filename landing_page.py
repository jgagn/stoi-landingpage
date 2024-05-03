#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 10:53:20 2024

@author: joelgagnon
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH])


#for interactive plot demo
import pickle
import math
import numpy as np
import plotly.express as px
import pandas as pd

#for absolute path
import os
###################################
#%% Tab 1: Competition Overview ###
###################################
#%% Import Data 
#use absolute path

# Get the absolute path to the directory containing the main app file
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the file
file_path = os.path.join(base_dir, "test_data/EliteCanada2024/srdatabase")


with open(file_path, 'rb') as f:
    database = pickle.load(f)

#for this page, I want to rename the names
top_40 = [
    "Babe Ruth", "Michael Jordan", "Jim Thorpe", "Muhammad Ali", "Wayne Gretzky",
    "Jim Brown", "Joe Louis", "Jesse Owens", "Babe Didrikson-Zaharias", "Wilt Chamberlain",
    "Willie Mays", "Jack Nicklaus", "Ted Williams", "Ty Cobb", "Pele",
    "Bill Russell", "Lou Gehrig", "Hank Aaron", "Joe DiMaggio", "Martina Navratilova",
    "Carl Lewis", "Gordie Howe", "Sugar Ray Robinson", "Larry Bird", "Ben Hogan",
    "Oscar Robertson", "Red Grange", "Walter Payton", "Jackie Robinson", "Rod Laver",
    "Kareem Abdul-Jabbar", "Magic Johnson", "Arnold Palmer", "Sandy Koufax", "Mickey Mantle",
    "Mark Spitz", "Joe Montana", "Jack Dempsey", "Bobby Orr", "Jackie Joyner-Kersee"
]
#loop through and give a display name
i=0
for name in database:
    database[name]['display_name'] = top_40[i]
    i=i+1

# Function to calculate the color based on the score
def get_color(score, max_score):
    if math.isnan(score):
        return 'black'  # or any other default color
    else:
        # Calculate the color based on the score and max score
        color_value = score / max_score
        return color_value

# Function to update the bubble plot
def update_bubble_plot(day, apparatus):
    data = {'x': [], 'y': [], 'size': [], 'name': [], 'score': [], 'color': []}
    max_score = max([stats['Score'] for values in database.values() if day in values for app, stats in values[day].items() if app == apparatus])

    exp = 3  # Adjust this as needed

    for name, values in database.items():
        if day in values:
            for app, stats in values[day].items():
                if app == apparatus:
                    if stats['E'] == 0.0:
                        data['x'].append(np.nan)
                    else:
                        data['x'].append(stats['E'])

                    if stats['D'] == 0.0:
                        data['y'].append(np.nan)
                    else:
                        data['y'].append(stats['D'])

                    data['name'].append(database[name]['display_name'])
                    data['score'].append(stats['Score'])
                    
                    # Make it zero if it's nan
                    if math.isnan(stats['Score']):
                        size = 0.0
                        color = 0.0
                    else:
                        size = stats['Score']
                        color = stats['Score']
                        
                    data['color'].append(get_color(color ** exp, max_score ** exp))
                        
                    size_exp = 1.5
                    if apparatus == "AA":
                        data['size'].append((size / 6) ** size_exp)
                    else:
                        data['size'].append(size ** size_exp)
    return data

# def update_table(day, apparatus, selected_athlete=None):
#     # Filter the database based on selected day and apparatus
#     filtered_data = {name: stats for name, values in database.items() if day in values for app, stats in values[day].items() if app == apparatus}
    
#     # Create DataFrame from filtered data
#     df = pd.DataFrame.from_dict(filtered_data, orient='index')
    
#     # Sort DataFrame by Score in descending order (if tie, sort by E score for now)
#     df = df.sort_values(by=['Score', 'E'], ascending=[False, False])
    
#     # Reset index to include Athlete name as a column
#     df = df.reset_index().rename(columns={'index': 'Athlete name'})
    
#     # Truncate score values to 3 decimal points (do not round)
#     df['D score'] = df['D'].map('{:.3f}'.format)
#     df['E score'] = df['E'].map('{:.3f}'.format)
#     df['Score'] = df['Score'].map('{:.3f}'.format)
    
#     # Add rank column
#     df['Rank'] = df.index + 1
    
#     # Reorder columns
#     df = df[['Rank', 'Athlete name', 'D score', 'E score', 'Score']]
    
#     # Generate HTML table with highlighted row if a selected athlete is provided
#     table_rows = []
#     for i in range(len(df)):
#         row_data = df.iloc[i]
#         background_color = 'yellow' if row_data['Athlete name'] == selected_athlete else 'white'
#         table_row = html.Tr([html.Td(row_data[col], style={'background-color': background_color}) for col in df.columns])
#         table_rows.append(table_row)
    
#     table = html.Table(
#         # Header
#         [html.Tr([html.Th(col) for col in df.columns])] +
#         # Body
#         table_rows
#     )
    
#     return table



#I want to make the drop down selectors take up less width
dropdown_style = {'width': '50%'}  # Adjust the width as needed

# Define layout of the app
overview_layout = html.Div([
    # html.H3('Competition Overview'),
    # dbc.Row([
    dbc.Col([
        html.Div("Competition Day:", style={'marginRight': '10px', 'verticalAlign': 'middle'}),
        dcc.Dropdown(
            id='day-dropdown',
            # options=[{'label': day, 'value': day} for day in next(iter(database.values())).keys()],
            options = [{'label': day, 'value': day} for day in next(iter(database.values())).keys() if day != 'display_name'],
            value=list(next(iter(database.values())).keys())[0],
            style=dropdown_style
        ),
    ], width=6),
    dbc.Col([
        html.Div("Apparatus:", style={'marginRight': '10px', 'verticalAlign': 'middle'}),
        dcc.Dropdown(
            id='apparatus-dropdown',
            options=[{'label': app, 'value': app} for app in ["FX", "PH", "SR", "VT", "PB", "HB", "AA"]],
            value='FX',
            style=dropdown_style
        ),
    ], width=6),
    # ]),
    html.Br(),  # Add line 
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='bubble-plot'),
            width=6,
            # style={'textAlign': 'center'} #doesnt work in my opinion to allign the plot
        ),
        # dbc.Col(
        #     html.Div(id='table-container'),
        #     width=6
        # )
    ])
])


# Define callback to update the bubble plot and table based on selected options
# Define callback to update the bubble plot and table based on selected options
@app.callback(
    [Output('bubble-plot', 'figure'),
     # Output('table-container', 'children')
     ],
    [Input('day-dropdown', 'value'),
     Input('apparatus-dropdown', 'value'),
     # Input('bubble-plot', 'clickData')
     ]  # Add clickData as input
)
def update_plot_and_table(day, apparatus): #, clickData):
    # Update bubble plot
    data = update_bubble_plot(day, apparatus)
    fig = px.scatter(data, x='x', y='y', color='color', size='size', hover_name='name',
                     color_continuous_scale='Viridis', opacity=0.6, hover_data={'name': True, 'x': False, 'y': False, 'size': False})
    fig.update_layout(title="Competition Overview", 
                      xaxis_title="E score", 
                      yaxis_title="D score", 
                      autosize=True,
                      margin=dict(l=40, r=40, t=40, b=40),
                      width=1000, #play with this value until you like it
                      height=600,
                      )
    fig.update_traces(text=data['score'], textposition='top center')  

    # Customize hover template
    hover_template = ("<b>%{hovertext}</b><br>" +
                      "D score: %{y:.3f}<br>" +
                      "E score: %{x:.3f}<br>" +
                      "Score: %{text:.3f}")
    fig.update_traces(hovertemplate=hover_template)
    
    # Update color bar legend
    fig.update_coloraxes(colorbar_title="Score")
    
    # Map color values to score values for color bar tick labels
    color_values = np.linspace(0, 1, 11)  
    max_score = max(data['score'])
    score_values = [value * max_score for value in color_values]  
    
    # Update color bar tick labels
    fig.update_coloraxes(colorbar_tickvals=color_values, colorbar_ticktext=[f"{score:.3f}" for score in score_values])
    
    # If a point is clicked, highlight the corresponding row in the table
    # if clickData:
    #     selected_athlete = clickData['points'][0]['hovertext']
        # table = update_table(day, apparatus, selected_athlete)
    # else:
    #     table = update_table(day, apparatus)
    
    return [fig] #, table



#%% Define the layout of your landing page with blue-ish background
app.layout = dbc.Container( children=[
    html.Div(
        html.Img(src='/assets/logo_cropped.png', height='200px'),  # Adjust the path and height of the image
        style={'textAlign': 'center', 'marginBottom': '20px'}
    ),
    
    html.H1(children='Bring Your Sports Data to Life!', className='display-3 text-center'),
    
    html.Div(children=[
        html.H3("STOI Analytics is modernizing how amateur sports analyze and share data through custom interactive dashboards.", style={'textAlign': 'center'}),
        # html.H5('Request a full Gymnastics Competition Dashboard demo by clicking on the "Request Demo Access" button', style={'textAlign': 'center'}),
        # html.H5("For inquiries for other sports, please email: <b>info@stoianalytics.com</b> and we will be in touch shortly!", style={'textAlign': 'center'}),
        html.H5([
            "Request a full Gymnastics Competition Dashboard demo by clicking on the ",
            html.Span("Request Gymnastics Demo Access", style={'font-weight': 'bold', 'display': 'inline'}),
            " button"
        ], style={'textAlign': 'center'}),
        
        html.H5([
            "For inquiries related to services for other sports, please email: ",
            html.Span("info@stoianalytics.com", style={'font-weight': 'bold', 'display': 'inline'}),
            " and we will be in touch shortly!"
        ], style={'textAlign': 'center'}),
        
        html.Div(
            html.Button('Request Gymnastics Demo Access', id='button-example', n_clicks=0),
            style={'textAlign': 'center', 'color': 'green', 'fontSize': '24px'} # Centering the button
        ),#'background-color': 'green',
        html.Br(),  # Add line 
        # html.Div(style={'height': '20px'}),  # Adding space with CSS
        html.H3("Gymnastics Competition Dashboard Features", style={'textAlign': 'center','color':'black'}),
        html.H5("1. Competition Overview: ", style={'textAlign': 'center','color':'black'}),
        html.P("Quickly View a Snapshot of the results for an entire category",style={'textAlign': 'center','color':'black'}),
        html.P("Easily identify trends, outliers, stand-out performances and overall depth of the program",style={'textAlign': 'center','color':'black'}),
        # overview_layout, #show plot
        html.H5("2. Individual Athlete Analysis: ", style={'textAlign': 'center','color':'black'}),
        html.P("Take a deep dive into individual athlete's scores across multiple days of competition",style={'textAlign': 'center','color':'black'}),
        html.P("Effortlessly identify and communicate overall athlete consistency and medal potential metrics",style={'textAlign': 'center','color':'black'}),
        html.H5("3. Team Scenarios: ", style={'textAlign': 'center','color':'black'}),
        html.P("Explore different various team scenarios through easy-to-use filters",style={'textAlign': 'center','color':'black'}),
        html.P("Make data-backed and transparent decisions for team selections to maximize your team's potential to achieve your objectives",style={'textAlign': 'center','color':'black'}),
        
        
        html.H4("Sample Interactive Plot",style={'textAlign': 'center'}),
        html.H6("The plot below represents a fictious MAG competition where the Difficulty (D) score is plotted on the y-axis and Execution (E) score on the x-axis.",style={'textAlign': 'center'}),
        html.H6("Each bubble represents an athletes score for that particular competition day and apparatus, with the bubble size and colour varying with total Score as shown in the Score legend bar on the right.",style={'textAlign': 'center'}),
        html.H5("Filter Options",style={'textAlign': 'center'}),
        html.H6("Filter the Competition Day to the results you want to view: Day 1, Day 2, Average or Best results.",style={'textAlign': 'center'}),
        html.H6("Filter by Apparatus: Floor Exercise (FX), Pommel Horse (PH), Still Rings (SR), Vault (VT), Parallel Bars (PB), High Bar (HB), or All Around (AA).",style={'textAlign': 'center'}),
        html.H5("Hover Options",style={'textAlign': 'center'}),
        html.H6("Hover over the bubbles in the plot to get detailed Difficulty (D) Score, Execution (E) Score and Total Score for that Athlete.",style={'textAlign': 'center'}),
        html.H6("Hover to the top right of the plot to access additional tools: download image, zoom, pan, box select, lasso select, zoom in, zoom out, autoscale and reset axes.",style={'textAlign': 'center'}),
        html.P("Request access to the full demo to see all the ways STOI Analytics can bring your data to life!",style={'textAlign': 'center'}),
    ], style={'margin': '20px'}),

    # dcc.Graph(
    #     id='example-graph',
    #     figure={
    #         'data': [
    #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
    #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
    #         ],
    #         'layout': {
    #             'title': 'Dash Data Visualization'
    #         }
    #     }
    # ),
    
    overview_layout,

    html.Div(children='''
        for any additional inquiries, please email info@stoianalytics.com
    ''', style={'textAlign': 'center', 'margin': '20px'})
])

#%% Comment out when pushing to pythonanywhere
# if __name__ == '__main__':
#     app.run_server(debug=True)