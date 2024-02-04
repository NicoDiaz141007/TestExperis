import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Cargar los datos desde los archivos CSV
costs_df = pd.read_csv('costs_2022.csv')
revenues_df = pd.read_csv('revenue_2022.csv')

#Se identifican que algunas lineas de negocio del data set Revenues son las mismas que en Costs por eso se modifican para encontrar una intesercción de datos.
revenues_df["Line Of Business"] = revenues_df["Line Of Business"].replace({'Company Signature Revenue':'Company Signature','Company Beyond Revenue':'Company Beyond'}, regex=True)

#Se identifican las listas de negocios de Revenues y Costs
businessList = list(set(revenues_df["Line Of Business"].unique()) & set(costs_df["Line Of Business"].unique()))
onlyRevenueList = np.setdiff1d(revenues_df["Line Of Business"].unique(), costs_df["Line Of Business"].unique())
onlyCostList = np.setdiff1d(costs_df["Line Of Business"].unique(), revenues_df["Line Of Business"].unique())


# Remover los símbolos de dólar y las comas de los valores monetarios y convertirlos a números
columns_to_convert = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Total']

for df in [costs_df,revenues_df]:
    for column in columns_to_convert:
        df[column] = df[column].replace({'$': '', ',': '', '[^0-9.]': ''}, regex=True).astype(float)

# Normalizar los valores utilizando Min-Max Scaling
scaler = MinMaxScaler()

for df in [costs_df,revenues_df]:
    df[columns_to_convert] = scaler.fit_transform(df[columns_to_convert])


# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el diseño del Dashboard
app.layout = html.Div([
    html.H1("Comparación de Revenues y Costs de servicios"),
    html.Div([
        html.Label("Seleccione las lineas de negocio:"),
        dcc.Dropdown(
            id='lineas-negocio-dropdown',
            options=[
                {'label': linea, 'value': linea} for linea in np.concatenate((businessList, onlyRevenueList, onlyCostList))
            ],
            value=[],
            multi=True
        )
    ]),
    dcc.Graph(id='lineas-negocio-grafico')
])


#Definicion de una funcion para actulizar el gráfico
@app.callback(
    Output('lineas-negocio-grafico', 'figure'),
    [Input('lineas-negocio-dropdown', 'value')]
)

def actulizar_grafico(lineas_seleccionadas):
    meses_abreviados = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig = go.Figure()
    revenue_lines = list(set(lineas_seleccionadas) & set(revenues_df["Line Of Business"].unique()))
    if len(revenue_lines) > 0:    
        ingresos_trace = go.Scatter(
            x=meses_abreviados  ,
            y=revenues_df[revenues_df['Line Of Business'].isin(lineas_seleccionadas)][meses_abreviados].sum().tolist(),
            mode='lines',
            name=f'Ingresos - {revenue_lines}'
        )
        fig.add_trace(ingresos_trace)
    cost_lines = list(set(lineas_seleccionadas) & set(costs_df["Line Of Business"].unique()))
    if len(cost_lines) > 0:
        costos_trace = go.Scatter(
            x=meses_abreviados,
            y=costs_df[costs_df['Line Of Business'].isin(lineas_seleccionadas)][meses_abreviados].sum().tolist(),
            mode='lines',
            name=f'Costos - {cost_lines}'
        )  
        fig.add_trace(costos_trace)
        
    fig.update_layout(
        title='Evolución de Ingresos y Costos de Servicios',
        xaxis=dict(title='Mes', tickvals=list(range(1, 13)), ticktext=meses_abreviados),
        yaxis=dict(title='Valor'),
        hovermode='closest',
        showlegend=True,
    )

    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True)
