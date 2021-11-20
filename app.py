from flask import request
import dash
import os
import dash_auth
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State


USERNAME_PASSWORD_PAIRS = [
    ['sasha', 'Abcd1234'],
    ['developer', 'Abcd_12$4'],
    ['chris', 'Abcd1234'],
    ['sebio', 'Abcd1234'],
    ['alan', 'Abcd1234'],
    ['aaron', 'Abcd1234'],
    ['sam', 'Abcd1234'],
    ['Sasha', 'Abcd1234'],
    ['Developer', 'Abcd_12$4'],
    ['Chris', 'Abcd1234'],
    ['Sebio', 'Abcd1234'],
    ['Alan', 'Abcd1234'],
    ['Aaron', 'Abcd1234'],
    ['Sam', 'Abcd1234'],
]


def get_client_list(username='generic'):
    export_config = [
        # Client Video  Campaign Start Date     Export file
        # ['Sebio', 'V618', '2021-09-12', '/Users/sasha/Downloads/PersonalVideos/Reports/Sebio_python_report.xlsx'],
        ['Izzi', 'V679', '2021-10-12', '/Users/sasha/Downloads/PersonalVideos/Reports/Izzi_python_report.xlsx'],
        ['Bimbo', 'V675', '2021-08-15', '/Users/sasha/Downloads/PersonalVideos/Reports/Bimbo_python_report.xlsx'],
        # ['Knorr', 'V666', '2021-06-06 00:14:24', '/Users/sasha/Downloads/PersonalVideos/Reports/Knorr_python_report.xlsx'],
        # ['MamiChula', 'V650', '2021-01-01 00:14:24', '/Users/sasha/Downloads/PersonalVideos/Reports/MamiChula_python_report.xlsx'],
        ['CVD', 'V677', '2021-09-20 00:14:24', '/Users/sasha/Downloads/PersonalVideos/Reports/CVD_python_report.xlsx'],
        ['Oppo', 'V676', '2021-08-15', '/Users/sasha/Downloads/PersonalVideos/Reports/Oppo_python_report.xlsx']
    ]

    list_to_return = export_config
    if username == 'sebio':
        list_to_return.append(['Sebio', 'V618', '2021-09-12', '/Users/sasha/Downloads/PersonalVideos/Reports/Sebio_python_report.xlsx'])
        return list_to_return
    else:
        return list_to_return


app = dash.Dash(__name__, title='QRrabbit Dashboard',
                external_stylesheets=["https://fonts.googleapis.com", "https://fonts.gstatic.com",
                                      "https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap"],
                meta_tags=[{'id': "myViewport", "name": "viewport", "content": "width=device-width, initial-scale=1"}],
                suppress_callback_exceptions=True
                )


# if not os.environ.get('DEBUG'):
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

server = app.server
