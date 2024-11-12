import dash
# Importa Bootstrap Components para Dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
# Templates de plolty
import plotly.io as pio
import pandas as pd

# Establece el tema oscuro para gráficos de Plotly
pio.templates.default = "plotly_dark"

url = 'https://datos.cdmx.gob.mx/dataset/909a033e-9a2c-41c7-a10e-ab1bd92a8095/resource/7cc6ff61-6178-4ba6-b39f-1f9eb3def57b/download/2023-06-26-wifi_gratuito_en_postes_c5.csv'
df = pd.read_csv(url, encoding="latin1")

# Tratamiento de datos
df.loc[df["Alcaldía"] == "Miguel Hidalgo", "Alcaldía"] = "MIGUEL HIDALGO"
df.loc[df["Alcaldía"] == "Cuauhtémoc", "Alcaldía"] = "CUAUHTÉMOC"
df.loc[df["Alcaldía"] == "La Magdalena Contreras", "Alcaldía"] = "LA MAGDALENA CONTRERAS"

point_access = point_access = df.groupby("Alcaldía")["Puntos_de_acceso"].sum().sort_values(ascending=False).reset_index(name='Puntos_de_acceso').copy()

# Inicia la aplicación de Dash con un tema oscuro de Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG]
)
server= app.server
# Estilos personalizados para tema oscuro
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("Postes de la CDMX", style={'textAlign': 'center', 'color': '#FFFFFF'}),
        html.H6("Ejemplo de Dash con Tema Oscuro y Bootstrap", style={'textAlign': 'center', 'color': '#FFFFFF'}),
        # Parte 1
        dbc.Row([
            dbc.Col(
                html.H5("Conteo de Alcaldías", style={'textAlign': 'center', 'color': '#FFFFFF'}),
            width=6),
            dbc.Col(
                html.H5("Distribución de Puntos de Acceso Wi-Fi por Alcaldía", style={'textAlign': 'center', 'color': '#FFFFFF'}),
            width=6),
        ]),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in point_access.columns],
                    data=point_access.to_dict('records'),
                    page_size=10,
                    style_table={'width': '50%', 'margin': 'auto'},
                    style_header={
                        'backgroundColor': '#333333',
                        'color': '#FFFFFF',
                        'fontWeight': 'bold',
                        'border': '1px solid #444444'
                    },
                    style_cell={
                        'backgroundColor': '#121212',
                        'color': '#FFFFFF',
                        'textAlign': 'center',
                        'border': '1px solid #444444',
                        'padding': '10px'
                    },
                ),
                width=6
            ),
            dbc.Col(
                dcc.Graph(
                    id='scatter-plot',
                    figure=px.scatter(
                        df,
                        x="Longitud",
                        y="Latitud",
                        color="Alcaldía",
                        color_continuous_scale='viridis',
                        opacity=0.6,
                        hover_data={'Colonia': True}
                    ).update_layout(
                        template="plotly_dark",
                        title={
                            'y': 0.95,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                            'font_size': 18
                        },
                        xaxis_title="Longitud",
                        yaxis_title="Latitud",
                        legend_title_text="Alcaldías",
                        margin=dict(l=50, r=50, t=80, b=50),
                        font_color='#FFFFFF',
                    )
                ),
                width=6
            ),
        ]),
        # Parte 2
        # Dropdown de Alcaldías
        dbc.Row([
            dbc.Col(width=3),
            dbc.Col(
                dcc.Dropdown(
                    id='alcaldia-dropdown',
                    options=[{'label': alc, 'value': alc} for alc in df['Alcaldía'].unique()],
                    placeholder='Selecciona una Alcaldía',
                    style={'color': 'black'},
                ),
                width=6
            ),
            dbc.Col(width=3),
        ]),

        # Dropdown de Colonias
        dbc.Row([
            dbc.Col(width=3),
            dbc.Col(
                dcc.Dropdown(
                    id='colonia-dropdown',
                    options=[],
                    placeholder='Selecciona una Colonia',
                    style={'color': 'black'},
                ),
                width=6,
            ),
            dbc.Col(width=3),
        ]),
        # Gráfico del mapa
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='map', style={'height': '80vh'}),
                width=12
            )
        )
    ],
    style={
        # Fondo oscuro para toda la aplicación
        'backgroundColor': '#121212',
        'color': '#FFFFFF',
        'padding': '20px'
    }
)

# Callback para actualizar las colonias según la alcaldía seleccionada
@app.callback(
    Output('colonia-dropdown', 'options'),
    Input('alcaldia-dropdown', 'value')
)
def set_colonia_options(selected_alcaldia):
    if not selected_alcaldia:
        return []

    filtered_df = df[df['Alcaldía'] == selected_alcaldia]
    return [{'label': col, 'value': col} for col in filtered_df['Colonia'].unique()]

# Callback para actualizar el mapa según la colonia seleccionada
@app.callback(
    Output('map', 'figure'),
    Input('alcaldia-dropdown', 'value'),
    Input('colonia-dropdown', 'value')
)
def update_map(selected_alcaldia, selected_colonia):
    mapbox_style = 'carto-positron'
    try:
        filtered_df = df[(df['Alcaldía'] == selected_alcaldia) & (df['Colonia'] == selected_colonia)]

        if filtered_df.empty:
            return px.scatter_mapbox(
                pd.DataFrame(data={}),
                lat=[],
                lon=[],
                title=f"La data selecionada no genera resultados. Intenta con otros datos",
                mapbox_style=mapbox_style,
                zoom=12,
                # Centro de la Ciudad de México como ejemplo
                center={"lat": 19.4326, "lon": -99.1332}
            )

        fig = px.scatter_mapbox(
            filtered_df,
            lat='Latitud',
            lon='Longitud',
            hover_name='Colonia',
            title=f"Mapa de {selected_colonia} en {selected_alcaldia}",
            mapbox_style=mapbox_style,
            zoom=12,
            center={'lat': filtered_df['Latitud'].mean(), 'lon': filtered_df['Longitud'].mean()}
        )
    except:
        fig = px.scatter_mapbox(
            pd.DataFrame(data={}),
            lat=[],
            lon=[],
            title=f"No se han selecionado data en los dropdowns.<br>O los dropdowns selecionados no generaron datos",
            mapbox_style=mapbox_style,
            zoom=12,
            # Centro de la Ciudad de México como ejemplo
            center={"lat": 19.4326, "lon": -99.1332}
        )
    return fig

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
