import pandas as pd
import plotly.graph_objects as go
import pandas as pd

from loguru import logger

from scrape_rate.config import DATA_DIR, TIME0
from scrape_rate.utils import get_dataframes, get_labels


def plot_rates() -> None:
    styles = ['plotly', 'plotly_dark']
    
    now = pd.Timestamp.now()
    ranges = {'day': [now - pd.Timedelta(days=1) + pd.Timedelta(hours=9), now], 
              'week': [now - pd.Timedelta(weeks=1), now],
              'month': [now - pd.Timedelta(weeks=4), now],
              '': [pd.Timestamp(TIME0), now],}
    for style in styles:
        for period, range in ranges.items():
            plot_in_style((period, range), style)


def plot_in_style(range, style: str) -> None:
    df, labels_df = get_dataframes(data_dir=DATA_DIR), get_labels(DATA_DIR, loan_period=30, repayment_freedom='Nej')
    
    fig = go.Figure()
    for column in df.columns:
        if column in labels_df['fundName'].tolist():
            fig.add_trace(go.Scatter(x=df.index, y=df[column],
                                     mode='lines+markers',
                                     name=column.split()[0],
                                     text=df[column],
                                     hoverinfo='y'))

            fig.add_annotation(x=df.index[-1], y=df[column].iloc[-1], text=df[column].iloc[-1])
            if range[0] == 'day':
                today = pd.Timestamp('today').normalize()
                today_rows = df[df.index.date == today.date()]
                first_row_today = today_rows.iloc[0] if not today_rows.empty else None
                fig.add_annotation(x=pd.Timestamp(first_row_today.name), y=first_row_today[column], text=first_row_today[column])

    fig.update_layout(
        title='Interest rate over the past ' + range[0],
        xaxis_title='Date',
        yaxis_title='Rate',
        xaxis=dict(
            tickformat='%Y-%m-%d' if range[0] != 'day' else '%H:%M',
            showgrid=True,
            zeroline=False,
        ),
        legend_title='Rates',
        template=style
    )

    fig.update_xaxes(range=range[1])
    fig.update_traces(marker=dict(size=1), hoverlabel=dict(bgcolor="white", font_size=13, font_family="Rockwell"))

    fig_path = DATA_DIR / f"plots/rates_{range[0]}_{style}"
    fig.write_html(fig_path.with_suffix('.html'))
    fig.write_image(fig_path.with_suffix('.png'))
    # fig.show()

    logger.info(f"Rates plotted to {fig_path}") 
