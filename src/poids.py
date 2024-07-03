import time
from datetime import datetime, timedelta, date
import re
from typing import NamedTuple, Dict, Sequence, Any
from pathlib import Path
from unidecode import unidecode
import pprint as pp


from typeguard import typechecked
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
from pandas.core.indexes.datetimes import DatetimeIndex

from python_libraries.File import (
    dump_data_to_file,
    load_file_to_data,
    dump_df_to_xlsx,
    load_xlsx_to_df,
)

################################################################################

DATA_FILE = Path("Data", "poids.xlsx")
ALPHA = 0.3
ROLLING_SCOPE = 7

################################################################################


def main():
    df = make_df()
    data = df["Poids"]
    data = make_complete_time_series(data=data)
    data = data.interpolate(method="time")
    data.info()
    print(data)
    fig = make_fig(data=data)
    plt.show()


################################################################################


def make_data_curve(*, ax, data, label):
    data = data.rolling(ROLLING_SCOPE).mean()
    ax.plot(data, label=label, color="blue")
    ##
    ax.label_outer()
    ax.legend(
        loc="lower center",
    )


################################################################################


def make_complete_time_series(*, data: pd.Series) -> pd.Series:
    assert isinstance(data.index, DatetimeIndex), data
    min_date = data.index.min()
    max_date = data.index.max()
    print(f"{min_date = }, {max_date = }")
    time_range = pd.date_range(start=min_date, end=max_date, freq="D", normalize=True)
    new_data = pd.Series(index=time_range, data=None)
    new_data[data.index] = data
    return new_data


################################################################################


def make_fig(*, data: pd.Series) -> Figure:
    fig, (ax0) = plt.subplots(
        1,
        sharex=True,
        sharey=True,
    )
    fig.autofmt_xdate()
    ax0.grid(True)
    ax0.set_ylim(bottom=88, top=92)
    ##
    title = "Poids"
    ax0.set_title(title)
    ##
    mean = data.mean()
    std = data.std()
    ax0.set_ylim(bottom=mean - 2 * std, top=mean + 2 * std)
    ##
    ax0.axhline(mean, color="green")
    ax0.axhline(mean + std, color="orange")
    ax0.axhline(mean - std, color="orange")
    ##
    label = f"Poids quotidien. Moyenne: {mean:.1f}, écart-type: {std:.2f}"
    make_data_curve(ax=ax0, data=data, label=label)
    ##
    return fig


################################################################################


def make_df() -> pd.DataFrame:
    df = pd.read_excel(
        DATA_FILE,
        dtype={"Date": "datetime64[ns]", "Poids": "float", "Commentaire": "string"},
        engine="openpyxl",
    )
    df = df.set_index("Date", drop=True)
    df = df.sort_index()
    df.info()
    ##
    today_string = date.today().isoformat()
    dataname = f"poids_{today_string}"
    dump_df_to_xlsx(df, dataname=dataname)
    return df


################################################################################

main()
