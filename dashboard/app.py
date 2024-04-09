from pathlib import Path
import pandas as pd
import yfinance as yf
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui
from shinywidgets import render_plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Default to the last month
end = pd.Timestamp.now()
start = end - pd.Timedelta(weeks=4)

ui.page_opts(title="Apple AAPL Stock Explorer", fillable=True)
selected_stock = "AAPL" #default selected stock

with ui.sidebar():
    # Search input
    ui.input_date_range("dates", "Select dates", start=start, end=end)
    ui.input_numeric("quantity", "Quantity", min=1, max=100, step=1, value=1)

    # Links and newsfeed section
    ui.h6("Newsfeed and links:")
    ui.a(
        "APPL Google Financial today",
        href="https://www.google.com/search?sca_esv=f16471168e6fc9b9&sca_upv=1&rlz=1C5CHFA_enUS748US748&sxsrf=ACQVn0_zAqWeiIBc3fzp9NY3AiSMHIloog:1712106682380&q=google+finance+AAPL&sa=X&ved=2ahUKEwiaiPu07qSFAxULElkFHQ3ODS0Q7xYoAHoECAkQAg&biw=1598&bih=788&dpr=1",
        style="color: #007bff;",  # Blue color for links
        target="_blank",
      
    )

    ui.a(
        "APPL Bloomberg",
        href="https://www.bloomberg.com/news/articles/2024-04-02/apple-flirts-with-support-levels-after-worst-quarter-in-a-decade?embedded-checkout=true",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "APPL Yahoo Finance Today",
        href="https://finance.yahoo.com/quote/AAPL/",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )

    ui.a(
        "GitHub Source",
        href="https://github.com/drodmay1/cintel-06-custom",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    
    ui.a(
        "GitHub App",
        href="https://github.com/drodmay1/cintel-06-custom/blob/main/dashboard/app.py",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "PyShiny", 
        href="https://shiny.posit.co/py/", 
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
   
with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("dollar-sign")):
        "Current Price"

        @render.ui
        def price():
            close = get_data()["Close"]
            return f"{close.iloc[-1]:.2f}"

    with ui.value_box(showcase=output_ui("change_icon")):
        "Change"

        @render.ui
        def change():
            return f"${get_change():.2f}"

    with ui.value_box(showcase=icon_svg("percent")):
        "Percent Change"

        @render.ui
        def change_percent():
            return f"{get_change_percent():.2f}%"
        
    with ui.value_box(showcase=icon_svg("coins")):
        "Total Value"

        @render.ui
        def total_value():
            data = get_data()
            quantity = input.quantity()
            if data.empty or quantity is None:
                return "N/A"
            else:
                close_price = data["Close"].iloc[-1]
                return f"${close_price * quantity:.2f}"
            
        ui.include_css(Path(__file__).parent / "styles.css")


with ui.layout_columns(col_widths=[9, 3]):
    with ui.card(full_screen=True):
        ui.card_header("Price history and volume")

        @render_plotly
        def price_and_volume():
            data = get_data()

            #C reate a new plotly figure
            fig = go.Figure()

            # Add candlestick trace
            fig.add_trace(
                go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               increasing_line_color='rgba(0,128,0,0.7)',
                               decreasing_line_color='rgba(255,0,0,0.7)',
                               name="Candlestick")
            )

            # Add volume trace as a bar chart
            fig.add_trace(
                go.Bar(x=data.index, y=data['Volume'], name="Volume")
            )

            # Update layout
            fig.update_layout(
                title="Price History and Volume",
                xaxis=dict(title="Date"),
                hovermode="x unified",
                paper_bgcolor='rgba(255,255,255,0.8)',
                plot_bgcolor='rgba(255,255,255,0.8)',
            )

            return fig
        
    
    with ui.card():
        ui.card_header("Latest data")

        @render.data_frame
        def latest_data():
            x = get_data()[:1].T.reset_index()
            x.columns = ["Category", "Value"]
            x["Value"] = x["Value"].apply(lambda v: f"{v:.1f}")
            return x
        
# Reactive calculations

@reactive.calc
def get_ticker():
    return yf.Ticker(selected_stock)

@reactive.calc
def get_data():
    dates = input.dates()
    return get_ticker().history(start=dates[0], end=dates[1])


@reactive.calc
def get_change():
    close = get_data()["Close"]
    return close.iloc[-1] - close.iloc[-2]

@reactive.calc
def get_change_percent():
    close = get_data()["Close"]
    change = close.iloc[-1] - close.iloc[-2]
    return change / close.iloc[-2] * 100

with ui.hold():

    @render.ui
    def change_icon():
        change = get_change()
        icon = icon_svg("arrow-up" if change >= 0 else "arrow-down")
        icon.add_class(f"text-{('success' if change >= 0 else 'danger')}")
        return icon
