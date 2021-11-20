from dash import html
from dash import dcc
import os
from dash.dependencies import Input, Output, State
from app import app, server
from apps import PlotLiveData


app.layout = html.Div([
    html.Img(id='logo', src='/assets/QRrabbit_logo_R1-white-BlueEye.svg'),
    html.H1(f"Dashboard Analytics - QRrabbit Internal"),
    html.Div([
        dcc.Link('main', href='/apps/'),
        dcc.Link('realtime', href='/apps/realtime/')
    ], className="nav-menu"),
    dcc.Location(id='url', refresh=False),  # pathname= read url name
    html.Div(id='page-content', children=[]),
    dcc.Store(id='data_store',
              data={},
              # clear_data=True,
              storage_type='local')
  ]
)


@app.callback(Output('page-content', component_property='children'),
              Input('url', component_property='pathname'))
def display_page(pathname):
    if pathname == '/':
        return PlotLiveData.layout
    if pathname == '/apps/realtime/':
        return PlotLiveData.layout
    elif pathname == '/apps/':
        return PlotLiveData.layout
    else:
        return "404"


if __name__ == '__main__':
    # export_to_excel(df)
    app.run_server(debug=bool(os.environ.get('DEBUG')))  #, host='0.0.0.0')
