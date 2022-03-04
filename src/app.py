from tkinter.ttk import Style
from dash import Dash, html, dcc, Input, Output
import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd

df = pd.read_csv("../data/clean/movies_clean_df.csv", index_col=0).rename(
    columns={'Major Genre': 'Major_genre',  
    'IMDB Rating': 'IMDB_rating', 'Running Time min': 'Duration'}, inplace=False)

genre = sorted(list(df["Major_genre"].dropna().unique()))
year = sorted(list(df["Year"].dropna().astype(str).unique()))
default_genres = ["Action", "Adventure", "Comedy", "Drama", "Horror", "Romantic Comedy"]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row(
        html.Div(html.Pre(children="Movie Lover",
            style={"text-aligh":"left", "font-size":"300%", "color":"black", 'margin-left': '0px'}),
        style={"backgroundColor": "#94e1f2"})),
    html.Br(),
   dbc.Row([
       dbc.Col([
           #Slider and checklist
           dbc.Card([
               dbc.CardHeader(
                   html.Label("Movie Criterions",
                   style={"font-size":17})),
               dbc.CardBody([
                   dcc.Loading([
           html.Div(
               html.P("Year range"),
                style={'text_aligh': 'left', 'color': '#0f3c63', 'font-family': 'sans-serif'}),
           html.Br(),
           dcc.RangeSlider(
               className="slider_class",
                id="year_range",
                count=1,
                step=1,
                min=1980,
                max=2016,
                value=[2000, 2005],
                marks={1980: {"label": "1980"}, 2016: {"label": "2016"}}
                ),
            html.Br(),
            html.Div(html.P("Select the movie genre"),
            style={'text_aligh': 'left', 'color': '#0f3c63', 'font-family': 'sans-serif'}),
            html.Br(),
            dcc.Checklist(
                id="genre_checklist",                    
                className="genre-container",
                inputClassName="genre-input",
                labelClassName="genre-label",
                options=[{"label": i, "value": i} for i in genre],                        
                value=default_genres,
                labelStyle={"display":"block",
                            "margin-left": "30px"}),
            ])
            ])
            ])
        ]),
    html.Br(), 
    #plot graphs
   dbc.Col(
        html.Iframe(
            id="plot_graphs",
            style={"display": "block",
                    "margin": "auto",
                    "overflow": " hidden", 
                    "width" : "200%", "height":"800px"}
        ))
        ])
])

@app.callback(
    Output('plot_graphs', 'srcDoc'),
    Input('genre_checklist', 'value'),
    Input('year_range', 'value')
)

#plotting function
def plot_graphs(genre, year_range):
    filter_genre = df[df.Major_genre.isin(genre)]

    filter_data = filter_genre.query("Year >= @year_range[0] & Year <= @year_range[1] & Major_genre in @genre").dropna()
    brush = alt.selection_interval()
    click = alt.selection_multi(fields=['Major_genre'])

    scatter = alt.Chart(filter_data, title="IMDB Rating Vs. Duration (in mins)").mark_circle(opacity=0.7).encode(
        x=alt.Y("IMDB_rating", title="IMDB Rating"),
        y=alt.X("Duration", title="Duration (in mins)"),
        color=alt.condition(brush, 'Major_genre', alt.value('lightgray')),
        tooltip=alt.Tooltip(["IMDB_rating", "Duration"]),
        opacity=alt.condition(click, alt.value(0.9), alt.value(0.1))).add_selection(brush)

    bar = alt.Chart(filter_data, title='Gross revenue (box office) by genre').mark_bar().encode(
        x=alt.X('sum(US_Revenue)', axis=alt.Axis(title='Gross Revenue (in millions USD)')),
        y=alt.Y('Major_genre', axis=alt.Axis(title='Major genre')),
        color=alt.Color('Major_genre'))
    barplot = bar.encode(opacity=alt.condition(click, alt.value(0.9), alt.value(0.1)),
       tooltip=alt.Tooltip('sum(US_Revenue)', format="$,.0f")).add_selection(click)

    line = alt.Chart(filter_data, title="Average revenue (box office) by genre").mark_line(point=True).encode(
        y=alt.Y("mean(US_Revenue)", axis=alt.Axis(title='Average Revenue (in millions USD)')),
        x=alt.X("Year:O", axis=alt.Axis(title="Year")),
        color=alt.condition(brush, 'Major_genre', alt.value('lightgray')),
        tooltip=alt.Tooltip('mean(US_Revenue)', format="$,.0f")).add_selection(click)

    chart = (scatter | line) & barplot

    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)