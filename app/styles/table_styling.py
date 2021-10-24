from dash import html

from .color_fader import custom_discrete_sequence


def highlight_max_value(df):
    """
    Return a list of conditional styles highlighting the max value in each column of a dataframe in a datatable.

    :param pandas.Dataframe df: A pandas dataframe
    :return list: List of conditional styles
    """
    if 'id' in df:
        numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    else:
        numeric_columns = df.select_dtypes('number')
    max_across_numeric_columns = numeric_columns.max()
    styles = []
    for col in max_across_numeric_columns.keys():
        styles.append({
            'if': {
                'filter_query': '{{{col}}} = {value}'.format(
                    col=col, value=max_across_numeric_columns[col]
                ),
                'column_id': col
            },
            'backgroundColor': '#ff0000',
            'color': 'white'
        })
    return styles


def highlight_min_value(df):
    """
    Return a list of conditional styles highlighting the min value in each column of a dataframe in a datatable.

    :param pandas.Dataframe df: A pandas dataframe
    :return list: List of datatable conditional styles
    """
    if 'id' in df:
        numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    else:
        numeric_columns = df.select_dtypes('number')
    min_across_numeric_columns = numeric_columns.min()
    styles = []
    for col in min_across_numeric_columns.keys():
        styles.append({
            'if': {
                'filter_query': '{{{col}}} = {value}'.format(
                    col=col, value=min_across_numeric_columns[col]
                ),
                'column_id': col
            },
            'backgroundColor': '#00910f',
            'color': 'white'
        })
    return styles


def every_other_rows(df):
    """
    Returns a conditional style changing the color of odd rows in a datatable.

    :param pandas.Dataframe df: A pandas dataframe
    :return dict: Datatable conditional style.
    """
    return {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(78, 78, 78)',
    }


def discrete_background_color_bins(df, n_bins=5, columns='all'):
    """
    Generate a color gradient for a column in a datatable.

    :param pandas.Dataframe df: A pandas dataframe
    :param int n_bins: Number of different colors
    :param list columns: Columns to apply the formatting to
    :return list: List of datatable conditional styles
    """
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = custom_discrete_sequence(n_bins)[i - 1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return styles
