#!/usr/bin/python
import os
import sys
from app import app, get_client_list

from datetime import timedelta, datetime

from time import perf_counter as clock, sleep
import mariadb
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import plotly.graph_objects as go
import base64
import plotly.express as px
from flask import request

# import xlsxwriter


MARIADBPASS = os.environ.get('MARIADB_PROD_PASS')
MARIADBHOST = os.environ.get('MARIADB_PRODDB_HOST')
MARIADBDBNAME = os.environ.get('MARIADB_PROD_DB_NAME')
MARIADBUSERNAME = os.environ.get('MARIADB_PROD_USER')

connections = 0
previous_url = None

logged_in_user = 'sasha'


class Db:
    """
    Main database for the application
    """

    # config = configparser.ConfigParser()
    # config.read('/app/config/conf.ini')
    # db_config = config['db']
    try:
        conn_pool = mariadb.ConnectionPool(
            user=f"{MARIADBUSERNAME}",
            password=f"{MARIADBPASS}",
            host=f"{MARIADBHOST}",
            database=f"{MARIADBDBNAME}",
            # port=int(db_config['port']),
            pool_name='Pool1',  # db_config['pool_name'],
            pool_size=5,  # int(db_config['pool_size']),
        )
    except mariadb.PoolError as e:
        print(f'Error creating connection pool: {e}')
        # logger.error(f'Error creating connection pool: {e}')
        sys.exit(1)

    def get_pool(self):
        return self.conn_pool if self.conn_pool is not None else self.create_pool()

    def __get_connection__(self):
        """
        Returns a db connection
        """

        global connections
        try:
            pconn = self.conn_pool.get_connection()
            pconn.autocommit = True
            # print(f"Receiving connection. Auto commit: {pconn.autocommit}")
            connections += 1
            # print(f"New Connection. Open Connections: {connections}")
            # logger.debug(f"New Connection. Open Connections: {connections}")
        except mariadb.PoolError as e:
            print(f"Error getting pool connection: {e}")
            # logger.error(f'Error getting pool connection: {e}')
            # exit(1)
            pconn = self.ــcreate_connectionــ()
            pconn.autocommit = True
            connections += 1
            # logger.debug(f'Created normal connection following failed pool access. Connections: {connections}')
        return pconn

    def ــcreate_connectionــ(self):
        """
        Creates a new connection. Use this when getting a
         pool connection fails
        """
        # db_config = self.db_config
        return mariadb.connect(
            user=f"{MARIADBUSERNAME}",
            password=f"{MARIADBPASS}",
            host=f"{MARIADBHOST}",
            database=f"{MARIADBDBNAME}",
            # port=int(db_config['port']),
        )

    def exec_sql(self, sql, values=None):
        global connections
        pconn = self.__get_connection__()
        try:
            cur = pconn.cursor()
            # print(f'Sql: {sql}')
            # print(f'values: {values}')
            cur.execute(sql, values)
            # pconn.commit()
            # Is this a select operation?
            if sql.startswith('SELECT') or sql.startswith('Select') or sql.startswith('select'):
                columns = cur.description
                result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                          cur.fetchall()]
                # result = cur.fetchall()  # Return a result set for select operations
            else:
                result = True

            pconn.close()
            connections -= 1
            # print(f'connection closed: connections: {connections}')
            # logger.debug(f'connection closed: connections: {connections}')
            # return True #Return true for insert, update, and delete operations
            return result
        except mariadb.Error as e:
            print(f"Error performing database operations: {e}")
            # pconn.rollback()
            pconn.close()
            connections -= 1
            print(f'connection closed: connections: {connections}')
            return False


db = Db()

if os.environ.get('DEBUG'):
    debug = True
else:
    debug = False

# class Connect:
#     def __init__(self):
#         # self.conn = mariadb.connect(
#         #     user=f"{MARIADBUSERNAME}",
#         #     password=f"{MARIADBPASS}",
#         #     host=f"{MARIADBHOST}",
#         #     database=f"{MARIADBDBNAME}")
#
#         # prefill all the descriptions:
#         # if not self.names_lookup:
#         where = export_config[0][1][1:]
#         for descr in export_config:
#             where += ' or video_id = ' + descr[1][1:]
#         Connect.get_description(self, where)
#
#     def conn(self):
#         return self.conn
#
#     # def __exit__(self, exc_type, exc_val, exc_tb):
#     # self.conn().close()
#
#     def get_lookup_query(self):
#         return '''SELECT t.slug as id, t.name as descr FROM qrrabbit.variations t WHERE video_id = '''
#
#     @staticmethod
#     def get_description(cls, id):
#         names_lookup = {}
#         # conn = ""
#         already_extracted_descriptions = ""
#
#         if id[0] == 'V':
#             id = id[1:]
#         # if not self.names_lookup:
#         if already_extracted_descriptions.find(id) < 0:
#             sql = f"{cls.get_lookup_query()} {id};"
#
#             lookup_tmp = db.exec_sql(sql)
#             # lookup_tmp = pd.read_sql(sql, self.conn)
#
#             # if lookup_tmp.empty:
#             #     sleep(0.1)
#             #     lookup_tmp = pd.read_sql(sql, self.conn)
#
#             df_lookup = pd.DataFrame(lookup_tmp)
#             if not df_lookup.empty:
#                 df_lookup.columns = ['id', 'descr']
#                 names_lookup.update(df_lookup[['id', 'descr']].set_index('id')['descr'].to_dict())
#                 # self.names_lookup.update(df_lookup[['id', 'descr']].set_index('id')['descr'].to_dict())
#             else:
#                 return ""
#
#             already_extracted_descriptions += id
#
#             return names_lookup
#         else:
#             return names_lookup


colors = {
    'background': '#335',
    'text': '#fff',
    'background-color': '#335',
}

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

COLUMNS = ['video_id', 'Id', 'Browser', 'Ip address', 'Operation system', 'Scanned at', 'Screen size',
           'Video time position',
           'Country', 'Region', 'City', 'Latitude', 'Longitude']
columns_to_rename = dict(ip_address="Ip address", os="Operation system", scanned_at="Scanned at",
                         screen_resolution="Screen size", video_time_position="Video time position")

latest_timestamp_extracted = ""
global_dataset = None

layout = html.Div([
    html.Div([  # wrapper for one Row
        html.Div([  # wrapper for LED displays
            daq.LEDDisplay(
                id='total_counter',
                value='0',
                label="Total Scans",
                color="#2222FF", className='dark-theme-control', backgroundColor='#115'),
            daq.LEDDisplay(
                id='todays_counter',
                value=0,
                label="Scans Since",
                color="#2222FF", className='dark-theme-control', backgroundColor='#115'),
            daq.LEDDisplay(
                id='since_updated',
                value=0,
                label="Since last updated",
                size=14,
                backgroundColor='#115',
            ),
            html.Span([
                html.P('Days to go back'),
                daq.Slider(
                    # label='Days to go back',
                    id='days_limiter',
                    min=1,
                    max=10,
                    value=1,
                    # size=350,
                    handleLabel={"showCurrentValue": True,
                                 "label": "Days"},
                    step=1
                )
            ], className='days_slider_block'),
        ], className="led_display"),
        html.Div([  # wrapper for one Box
            html.Div([  # wrapper for Toggle Switches
                # daq.ToggleSwitch(
                #     id='daily_hourly_grouping',
                #     label=['Daily', 'Hourly'],
                #     value=False,
                #     style={'text-align': 'center'}
                # ),
                daq.ToggleSwitch(
                    id='output_stacked_grouped',
                    label=['Stack', 'Group'],
                    value=True,
                    style={'text-align': 'center'}
                ),

                daq.ToggleSwitch(
                    id='realtime_toggle',
                    label=['Static', 'Realtime'],
                    value=False,
                    style={'text-align': 'center'}
                ),
                dcc.Markdown(id='display_from'),
                dcc.Markdown(id='display_to'),
                html.Pre(id='relayout-data'),
            ], className='toggles'
            ),
            html.Div([
                html.Div([
                    daq.Gauge(
                        id='gauge_lev_of_details',
                        label="Chart's Level of Details",
                        value=0,
                        size=170,
                        # min=-1,
                        max=3,
                        # showCurrentValue=True,
                        scale={'start': 0, 'interval': 1, 'labelInterval': 1},
                        units={'day': 0, 'hour': 1, 'minute': 3, 'second': 4},
                        color={"gradient": True, "ranges": {"green": [0, 1], "yellow": [1, 2], "red": [2, 3]}}
                    ),
                    dcc.Slider(
                        id='frequency_slider_control',
                        min=0,
                        max=1,
                        step=1,
                        value=0,
                        marks={0: 'Daily', 1: 'Hourly', 2: 'Minutes', 3: 'Seconds'}
                    ),
                ]),
            ], className='gauges'),
        ], className="gauges_and_toggles"),
        html.Div([
            html.P("Select Account to filter the graph",
                   className="account_selector_title"),
            dcc.Dropdown(id='account_picker',
                         options=[],  # account_options,
                         clearable=False,
                         value=get_client_list()[0][1],  # 'V679',  # export_config[0][1]  # value=df['video_id'].max()
                         ),
            # className="btn btn-primary dropdown-toggle"),

        ], className="account_selector"),
    ], className="container", ),
    html.Div([

        html.Hr(),
        # html.Div([
        #     html.P("Percistent Day-Range Filter",
        #            className="day_range_filter"),
        #     dcc.RangeSlider(
        #         id='day_ranges',
        #         min=0,  # format(df.index.min().date()),
        #         max=(df.index.max().date() - df.index.min().date()).days,
        #         value=[0, (df.index.max().date() - df.index.min().date()).days],
        #         allowCross=False,
        #         marks={
        #             0: {'label': f'Start: {str(df.index.min().date())}',
        #                 'style': {'left-margin': '10px', 'padding': '20px', 'color': '#77b0b1'}},
        #             25: {'label': '25%'},
        #             50: {'label': '50%'},
        #             75: {'label': '75%'},
        #             100: {'label': f'Latest: {str(df.index.max().date())}', 'style': {'color': '#f50'}}
        #         }
        #     ),
        # ], className="range_slider"),
    ], className="percistent_range_filter_group"),

    dcc.Graph(id='chart1', config={'displaylogo': False,
                                   # 'showAxisDragHandles': True,
                                   # 'showAxisRangeEntryBoxes': True,
                                   }  # , legend={
              # 'bgcolor': 'rgba(0,0,0,0)',
              # 'orientation': "h",
              # 'yanchor': "bottom",
              # 'y': '-0.15',
              # 'xanchor': "left",
              # 'x': '0'
              # },
              ),
    html.Br(),
    dcc.Checklist(
        id='tick',
        options=[{'label': 'Enable Visual Zoom',
                  'value': 'linear'}],
        value=['linear']
    ),
    html.Br(),
    dcc.Graph(id='chart2', config={'displaylogo': False,
                                   'showAxisDragHandles': True,
                                   'showAxisRangeEntryBoxes': True,
                                   }  # , legend={
              ),
    html.Br(),
    dcc.Interval(
        id='fetch_interval',
        interval=1000 * 10,
        n_intervals=0,
        disabled=False,
        # max_intervals=1000
    )
])


#     rolling average = resampled_hourly_pre.rolling(window=14).mean()


@app.callback(Output('fetch_interval', 'disabled'),
              Input('realtime_toggle', 'value')
              )
def realtime_toggle(toggle_switch):
    return not toggle_switch


def print_elapsed_time(module_name, written_records, elapsed):
    """ Print module run times in a consistent format. """
    print("%s   for %-8s extracted %s entries in %2.2f sec" % (
        datetime.now().time(), module_name, written_records, elapsed))


def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return 'data:image/svg+xml,{}'.format(encoded.decode())


def fetch_data(selected_account='679'):
    global latest_timestamp_extracted
    # global df
    global global_dataset

    start_time = clock()

    if not latest_timestamp_extracted:
        # if len(export_config) == 1:
        where_video_id = f"where video_id='{selected_account}'"  # and scanned_at > '{export_config[0][2]}';"
        # where_video_id = f"where video_id='{export_config[0][1]}' and scanned_at > '{export_config[0][2]}';"
        # else:
        #     where_video_id = "where (video_id='"
        #     for client in export_config:
        #         where_video_id += f"{client[1]}' and scanned_at > '{client[2]}') or (video_id='"
        #     where_video_id = where_video_id[:len(where_video_id) - 14]
    else:
        # if len(export_config) == 1:
        where_video_id = f"where video_id='{selected_account}' and scanned_at > '{latest_timestamp_extracted}';"
        # where_video_id = f"where video_id='{export_config[0][1]}' and scanned_at > '{latest_timestamp_extracted}';"
        # else:
        #     where_video_id = "where (video_id='"
        #     for client in export_config:
        #         where_video_id += f"{client[1]}' or video_id='"
        #     where_video_id = where_video_id[:len(where_video_id) - 14]
        #     where_video_id += f") and scanned_at > '{latest_timestamp_extracted}';"

    # compound_sql = f"select \
    #     video_id, \
    #     variation_id as Id, \
    #     browser as Browser, \
    #     ip_address, \
    #     os, \
    #     scanned_at, \
    #     screen_resolution, \
    #     video_time_position, \
    #    c2.name as Country, \
    #     r.name as Region, \
    #     c.name as City, \
    #     lat as Latitude, \
    #     lng as Longitude \
    # from headers \
    #     join cities c on c.id = headers.city_id \
    #     join regions r on r.id = c.region_id \
    #     join countries c2 on c2.id = r.country_id {where_video_id}"

    compound_sql = f"select video_id, \
        variation_id as Id, scanned_at from headers {where_video_id}"
    # zAfMF and VV238, VV255, VV233, CiQxt, VV253, VV268 were high volume developer's tests

    if not latest_timestamp_extracted:

        global_dataset = db.exec_sql(compound_sql)
        df_internal = pd.DataFrame(global_dataset).set_index('scanned_at').tz_localize(
            'UTC').tz_convert('US/Pacific')
        # df = df_internal.astype(str)

        # print(sys.getsizeof(df.to_dict()))

        # df = pd.read_sql(compound_sql, Connection.conn, index_col='scanned_at', parse_dates=True).sort_values(
        #     'scanned_at').tz_localize('UTC').tz_convert('US/Pacific')
        # Update timestamp marker
        latest_timestamp_extracted = str(df_internal.tail(1).index.tz_convert('UTC').tz_localize(None).array[0])

        elapsed = clock() - start_time
        print_elapsed_time("Several accounts", len(df_internal), elapsed)

    else:
        # print(compound_sql)
        # updated_df = pd.read_sql(compound_sql, Connection.conn, index_col='scanned_at', parse_dates=True).sort_values(
        #     'scanned_at').tz_localize('UTC').tz_convert('US/Pacific')
        global_dataset = db.exec_sql(compound_sql)
        retrieved_records = 0
        if global_dataset:
            updated_df = pd.DataFrame(global_dataset).set_index('scanned_at').tz_localize('UTC').tz_convert(
                'US/Pacific')

            # Update timestamp marker
            # if not updated_df.empty:  # ['Id'].count() > 0:
            latest_timestamp_extracted = str(updated_df.tail(1).index.tz_convert('UTC').tz_localize(None).array[0])
            # df = pd.concat([df, updated_df])
            retrieved_records = updated_df['Id'].count()
        update_message_string = f"Added {retrieved_records} new entries"  # to an existing total of " + len(df)
        elapsed = clock() - start_time
        print_elapsed_time(update_message_string, len(global_dataset), elapsed)

    return global_dataset

    # df_os = df['os'].value_counts(normalize=True)  # <-- counts number of yes and no.
    # df_city = df['City'].value_counts(normalize=True)  # <-- normalization: counts number of yes and no.

    # df['Hourly'] = pd.to_datetime(df['Scanned at'], format="%Y-%d-%m %H") # Didn't drop min and sec
    # df['Hourly'] = df['Scanned at'].dt.floor('H')
    # grp_min = df['Scanned at'].dt.floor('Min')
    # df['Hourly'] = df['Scanned at'].map(lambda x: (x.date, x.hour))
    # df_groupby_hour = df.groupby('Hourly').count()
    # grp_h = df.groupby('Hourly')['Id'].value_counts()

    # or with value_counts(normalize=True) to get % of each

    # dfc = df['Scanned at'].value_counts()

    # grp = df.groupby(df['Scanned at'].dt.time)['Id'].sum()

    # grp = df.groupby(by=[df['Scanned at'].map(lambda x: (x.day, x.hour))])
    # df.groupby(['Scanned at'])['Video time position'].max() # This works

    # df_daily = df.groupby(df['Scanned at'].dt.date)['Id'].count().tolist()  # <-- get daily count
    # df_daily = df.loc['Scanned at'].groupby(df['Scanned at'].dt.date)['Id'].count()  # <-- get daily count


# def export_to_excel(df):
#     df = df.tz_convert('America/Mexico_City').tz_localize(None).sort_values(by='scanned_at')
#     df.reset_index(inplace=True)
#     for client in export_config:
#         video_id = client[1]
#
#         filtered_df = df.loc[df['video_id'] == video_id].drop(['video_id'], axis=1).rename(columns=columns_to_rename)
#         filtered_df.to_excel(
#             '/Users/sasha/Downloads/PersonalVideos/Reports/Panda-Export_' + client[0] + '.xlsx',
#             sheet_name='Result 1', index=False)


# Utility function to read VIDEO_ID and return NAME of the client
def return_account_names(acc_id):
    exp_conf = get_client_list()

    for name in exp_conf:
        if name[1] == acc_id:
            return name[0]


# MAIN **GRAPH** update
@app.callback(
    [
        Output('chart1', 'figure'),
        Output('chart2', 'figure'),
        Output('gauge_lev_of_details', 'value'),
        Output('frequency_slider_control', 'max'),
        Output('total_counter', 'value'),
        Output('display_from', 'children'),
        Output('display_to', 'children'),
    ],
    [
        Input('data_store', 'data'),
        Input('account_picker', 'value'),
        Input('output_stacked_grouped', 'value'),
        # Input('daily_hourly_grouping', 'value'),
        Input('frequency_slider_control', 'value'),
        # Input('day_ranges', 'value'),
        Input("tick", "value"),
        Input('chart1', 'relayoutData'),
    ],
    prevent_initial_call=True
)
def update_figure(data_store, selected_account, stacked, daily_hourly, tick_mode, relayout_data_zoom):
    start_time = clock()

    if selected_account[0] == 'V':
        selected_account = selected_account[1:]

    trace_descriptions = data_store['legends'][selected_account]  # .get(selected_account)

    recreated_df = pd.DataFrame(data_store['dataset'][selected_account])
    recreated_df['scanned_at'] = pd.to_datetime(recreated_df['scanned_at'])
    recreated_df = recreated_df.set_index(['scanned_at'])
    if not selected_account:
        selected_account = app.export_config[0][0]

    # for account in export_config:
    #     if account[0] == selected_account:
    #         selected_account = account[1]
    # if selected_account[0] == 'V':
    #     selected_account = selected_account[1:]

    filtered_df = recreated_df[recreated_df['video_id'] == 'V' + selected_account].tz_localize(None)
    # filtered_df = df[df['video_id'] == selected_account].tz_localize(None)

    total_counter = '{:,}'.format(len(filtered_df)).replace(',', '.')

    #             resampled_hourly_pre = data_to_plot.loc[df['video_id'] == item[1]].resample('H').count()
    #             resampled_hourly = resampled_hourly_pre.rolling(window=14).mean()
    #
    #             counts = resampled_hourly['Id'].values.tolist()
    #             hr = resampled_hourly.index.tolist()
    #
    #             data = [go.Bar(x=hr, y=counts, text=item[0])]
    #             layout = go.Layout(barmode='group')

    # ToDo: Filter on day_ranges FROM and TO - check for accuracy
    # from_day_filter = df.index.min() + timedelta(days=day_ranges[0])

    try:

        if not relayout_data_zoom:
            from_day_string_no_localize = filtered_df.index.min()  # + timedelta(days=day_ranges[0])
            # until_day_filter = df.index.min() + timedelta(days=day_ranges[1])
            until_day_filter_no_localize = filtered_df.index.max()  # + timedelta(days=day_ranges[1])

            df_filtered_by_day_range = filtered_df

        elif relayout_data_zoom.get('xaxis.range[0]') and relayout_data_zoom.get('xaxis.range[0]'):
            if len(relayout_data_zoom.get('xaxis.range[0]')) == 16:
                from_datetime_format = "%Y-%m-%d %H:%M"
            else:
                from_datetime_format = "%Y-%m-%d %H:%M:%S"
            if len(relayout_data_zoom.get('xaxis.range[1]')) == 16:
                to_datetime_format = "%Y-%m-%d %H:%M"
            else:
                to_datetime_format = "%Y-%m-%d %H:%M:%S"

            from_day_string_no_localize = datetime.strptime(
                relayout_data_zoom.get('xaxis.range[0]')[:19], from_datetime_format)
            until_day_filter_no_localize = datetime.strptime(
                relayout_data_zoom.get('xaxis.range[1]')[:19], to_datetime_format)

            from_1 = str(from_day_string_no_localize) if len(relayout_data_zoom.get('xaxis.range[0]')) != 16 else None
            until_1 = str(until_day_filter_no_localize) if len(relayout_data_zoom.get('xaxis.range[1]')) != 16 else None
            df_filtered_by_day_range = filtered_df.loc[from_1:until_1]

        elif not relayout_data_zoom.get('xaxis.range'):
            from_day_string_no_localize = filtered_df.index.min()  # + timedelta(days=day_ranges[0])
            # until_day_filter = df.index.min() + timedelta(days=day_ranges[1])
            until_day_filter_no_localize = filtered_df.index.max()  # + timedelta(days=day_ranges[1])

            df_filtered_by_day_range = filtered_df

        else:
            if len(relayout_data_zoom.get('xaxis.range')[0]) == 16:
                from_datetime_format = "%Y-%m-%d %H:%M"
            else:
                from_datetime_format = "%Y-%m-%d %H:%M:%S"
            if len(relayout_data_zoom.get('xaxis.range')[1]) == 16:
                to_datetime_format = "%Y-%m-%d %H:%M"
            else:
                to_datetime_format = "%Y-%m-%d %H:%M:%S"

            from_day_string_no_localize = datetime.strptime(
                relayout_data_zoom.get('xaxis.range')[0][:19], from_datetime_format)
            until_day_filter_no_localize = datetime.strptime(
                relayout_data_zoom.get('xaxis.range')[1][:19], to_datetime_format)

            df_filtered_by_day_range = filtered_df.loc[
                                       str(from_day_string_no_localize):str(until_day_filter_no_localize)]

    except AttributeError:
        # from_day_string_no_localize = filtered_df.index.min()
        # until_day_filter_no_localize = filtered_df.index.max()
        raise dash.exceptions.PreventUpdate

    filtered_by_hours = int((until_day_filter_no_localize - from_day_string_no_localize) / pd.Timedelta('1 hour'))

    if filtered_by_hours <= 24:  # 1 is in HOURS
        max_frequency = 3
    elif filtered_by_hours <= 48:
        max_frequency = 2
    else:
        max_frequency = 1

    if daily_hourly == 0:
        resample_rate = 'D'
    elif daily_hourly == 1:
        resample_rate = 'H'
    elif (daily_hourly == 2) and (max_frequency > 1):
        resample_rate = 'T'
    elif (daily_hourly == 3) and (max_frequency > 2):
        resample_rate = 'S'
    else:
        resample_rate = 'H'

    if stacked:
        barmode = 'stack'
    else:
        barmode = 'group'

    if ":" in tick_mode:
        tick_mode, screen_size = tick_mode.split(":")

    # df_by_variation = filtered_df['Id'][filtered_df['Id'] == variation].resample(resample_rate).count()

    # test_df = df_filtered_by_day_range.reset_index().set_index(['Id', 'scanned_at'])
    # formatted_df = test_df.reset_index(level='Id')
    # output_df = formatted_df.groupby('Id').resample(resample_rate)['os'].count()

    # test_df = df_filtered_by_day_range[['Id']]
    # groupby_id = df_filtered_by_day_range.groupby(['Id'])

    traces = []
    traces2 = []
    colors_list = px.colors.qualitative.Alphabet
    colors_dict = {}
    # i = 0

    for i, variation in enumerate(df_filtered_by_day_range['Id'].unique()):
        df_by_variation = df_filtered_by_day_range['Id'][df_filtered_by_day_range['Id'] == variation].resample(
            resample_rate).count()
        # df_by_variation_filtered_days = df_by_variation.loc[from_day_string_no_localize:until_day_filter_no_localize]

        # df_filtered_by_day_range['Id'].groupby(lambda d: d.date()).resample('D').count()
        # test_df = df_filtered_by_day_range.reset_index(level='scanned_at')
        # test_df.groupby('Id').resample('D')['scanned_at'].count()

        # group_by = df_by_variation.resample(resample_rate).count().groupby('Id')
        # x_values = output_df.unstack()
        # y_values = output_df.tolist()
        x_values = df_by_variation.index
        y_values = df_by_variation

        descr = trace_descriptions.get(variation, 'none')
        if not descr:
            print('error')

        traces.append(go.Bar(x=x_values, y=y_values, name=descr, marker=dict(color=colors_list[i])))
        colors_dict[descr] = colors_list[i]

    if 'linear' in tick_mode:
        legends_y_offset = -len(traces) / 12 - .3

        if len(traces) > 16:
            legends_y_offset = -2
    else:
        legends_y_offset = -len(traces) / 12

    # title=f"{label} plot for {return_account_names(selected_account)}"
    layout1 = go.Layout(title=None).update(
        barmode=barmode,
        xaxis_tickangle=-45,
        uniformtext_minsize=8,
        height=850,
        margin=dict(
            l=30,
            r=50,
        ),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],

    )

    layout1.update(
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="sans-serif",
                # size=8,
                # color="black"
            ),
            orientation="h",
            yanchor="bottom",
            y=legends_y_offset,
            xanchor="left",
            x=0
        )
    )

    if 'linear' in tick_mode:
        layout1.update(
            xaxis=dict(
                # tickmode='linear',
                # tick0=0.5,
                # dtick=0.75
                # uniformtext_minsize=8,
                # uniformtext_mode='hide',
                rangeslider_visible=True,
                tickformatstops=[
                    dict(dtickrange=[None, 60000], value="%H:%M:%S s\n%b %d"),
                    dict(dtickrange=[60000, 3600000], value="%H:%M m\n%b %d"),
                    dict(dtickrange=[3600000, 86400000], value="%H:%M h\n%b %d"),
                    dict(dtickrange=[86400000, 604800000], value="%b %e"),
                    dict(dtickrange=[604800000, None], value="%e. %b w")
                ]
            )
        )
    layout1.update(uniformtext_minsize=8, uniformtext_mode='hide', showlegend=True,
                   title={
                       'text': f"Total Engagements for<b> {return_account_names('V' + selected_account)}</b> per filtered timeline",
                       'y': 0.93,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'}
                   )  # , showAxisDragHandles=True)

    # Chart 2:
    df_descr = pd.DataFrame(trace_descriptions.items(), columns=['Id', 'descr'])
    df_merged = df_filtered_by_day_range.merge(df_descr, on='Id', how='left').reset_index()

    df_by_variation = df_merged[['descr', 'Id']].value_counts().sort_values(ascending=True).reset_index()
    df_by_variation = df_by_variation.set_axis(['descr', 'Id', 'total'], axis=1, inplace=False)

    traces2.append(go.Bar(x=df_by_variation['total'],
                          y=df_by_variation['descr'],
                          orientation='h',
                          marker=dict(color=list(map(lambda x: colors_dict[x], df_by_variation['descr'].to_list()))),
                          text=str(df_by_variation['total']),
                          texttemplate=df_by_variation['descr'].astype(str) + '   :   ' + df_by_variation[
                              'total'].astype(str),
                          textposition='auto',
                          ))

    layout2 = go.Layout(title=None).update(
        barmode=barmode,
        uniformtext_minsize=8,
        height=200 + 35 * len(df_by_variation),
        margin=dict(
            autoexpand=True,
            l=10,
            r=50,
            pad=20,
        ),
        yaxis={'visible': False, 'showticklabels': False, 'fixedrange': True},
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        xaxis={'fixedrange': True, 'type': 'log'},
    )

    layout2.update(
        title={
            'text': "Total Engagement by Channel",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )

    if debug:
        label1 = str(relayout_data_zoom)
        label2 = "## This is a placeholder for my debug statement"
    else:
        label1 = label2 = ''

    # print_elapsed_time("Refiltered data", 0, clock() - start_time)
    print(str(relayout_data_zoom))
    return {'data': traces, 'layout': layout1}, \
           {'data': traces2, 'layout': layout2}, daily_hourly, max_frequency, total_counter, label1, label2


# REALTIME fetching data from the server
@app.callback(Output('todays_counter', 'value'),
              [
                  # Input('fetch_interval', 'n_intervals'),
                  Input('account_picker', 'value'),
                  Input("days_limiter", "value"),
                  Input('data_store', 'data')
              ], prevent_initial_call=True
              )
def fetch_new_entries(account_picker, days_limiter, data):

    recreated_df = pd.DataFrame(data['dataset'][account_picker[1:]])
    recreated_df['scanned_at'] = pd.to_datetime(recreated_df['scanned_at'])
    recreated_df = recreated_df.set_index(['scanned_at'])

    counter = recreated_df.loc[recreated_df['video_id'] == account_picker].loc[
              format(datetime.now() - timedelta(hours=24 * days_limiter), '%Y-%m-%d %H:%m'):None]['Id'].count()

    return counter


@app.callback(
    Output('data_store', 'data'),
    Output('account_picker', 'options'),
    Input('account_picker', 'value'),
    State('data_store', 'data'),
    Input("fetch_interval", "n_intervals"),
    State('url', 'pathname'),
)
def data_store(value, data, interval, pathname):
    global latest_timestamp_extracted
    global previous_url
    global logged_in_user
    account_options = []

    updated_client_list = get_client_list(request.authorization['username'])

    for video_id in updated_client_list:
        account_name = video_id[0]  # return_account_names(video_id)
        dict_item = {'label': account_name, 'value': video_id[1]}
        if dict_item not in account_options:
            account_options.append(dict_item)

    force_refresh = previous_url != pathname
    previous_url = pathname

    if len(data) == 0:
        latest_timestamp_extracted = ''

    if value[0] == 'V':
        video_id = value[1:]

    if not data:
        data = {}
        data['dataset'] = {}
        data['legends'] = {}
        # data[2] = {}

        dataset = fetch_data(value)

        if len(dataset) == 0:
            raise dash.exceptions.PreventUpdate

        legend_descr_sql = f"SELECT t.slug as id, t.name as descr FROM qrrabbit.variations t WHERE video_id = {video_id};"
        legend_descr_dict = db.exec_sql(legend_descr_sql)

        df_lookup = pd.DataFrame(legend_descr_dict)
        if not df_lookup.empty:  # If query returned nothing
            # df_lookup.columns = ['id', 'descr']
            df_lookup = df_lookup.set_index('id').to_dict()
            # data['legends'] = {}
            data['legends'][video_id] = df_lookup['descr']

        df_updated = pd.DataFrame(dataset)
        df_updated = df_updated.set_index(['scanned_at'])

    else:
        # latest_timestamp_extracted = list(data['dataset']['scanned_at'].items())[-1][1]
        if video_id in data['dataset']:
            latest_sorted = list(data['dataset'][video_id]['scanned_at'].items())
            latest_timestamp_extracted = sorted(latest_sorted, key=lambda scanned: scanned[1])[-1][1]
        else:
            latest_timestamp_extracted = ""

        # if data['legends']:
        dataset = fetch_data(value)

        if video_id in data['dataset']:
            if len(dataset) == 0 or len(dataset) == len(data['dataset'][video_id]):
                if video_id in data['legends']:  # data['legends'].find(value) > 0:
                    # if data['legends'][value]
                    if not force_refresh:
                        raise dash.exceptions.PreventUpdate

        legend_descr_sql = f"SELECT t.slug as id, t.name as descr FROM qrrabbit.variations t WHERE video_id = {video_id};"

        legend_descr_dict = db.exec_sql(legend_descr_sql)

        df_lookup = pd.DataFrame(legend_descr_dict)

        if not df_lookup.empty:  # If query returned nothing
            # df_lookup.columns = ['id', 'descr']
            df_lookup = df_lookup.set_index('id').to_dict()
            if video_id in data['legends']:  # if the query returned the value which is already in data['legends']
                if len(df_lookup['descr']) != len(
                        data['legends'][video_id]):  # if new values are added to the database.
                    del data['legends'][video_id]
                    data['legends'][video_id] = df_lookup['descr']
            else:
                data['legends'][video_id] = df_lookup['descr']

        if dataset:
            df_updated = pd.DataFrame(dataset)
            df_updated = df_updated.set_index(['scanned_at'])

            if video_id in data['dataset']:
                df_stored = pd.DataFrame(data['dataset'][video_id])
                df_stored = df_stored.set_index(['scanned_at'])

                df_updated = pd.concat([df_stored, df_updated])

    array_to_store = []

    if dataset:
        df_for_store = df_updated.reset_index()
        df_for_store["scanned_at"] = df_for_store["scanned_at"].astype(str)

        data['dataset'][video_id] = df_for_store.to_dict()

        # array_to_store.append(df_for_store.to_dict())
    # else:
    # array_to_store.append(data['dataset'])

    # if df_lookup:
    # array_to_store.append(data['legends'])

    # data = df_for_store.to_dict()
    # data.append(df_lookup['descr'])
    # data.append(account_options)

    # print(sys.getsizeof(data))
    # account_options

    if not dataset and not df_lookup:
        raise dash.exceptions.PreventUpdate
    else:
        return data, account_options
