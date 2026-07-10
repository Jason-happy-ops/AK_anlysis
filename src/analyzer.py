from matplotlib import spines, ticker
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False









class StockAnalyzer:
    """
    股票分析器：连接数据库，提供走势画图功能。
    """

    def __init__(self, db_url: str = None):
          # 连接数据库，排查异常
        try:
            self.engine = create_engine("mysql+pymysql://root:@localhost:3306/stock?charset=utf8mb4")
            print("数据库连接成功！")
        except Exception as e:
            print(f"数据库连接失败：{e}")
    
    
    
    def draw_trend(self, stock_code: str, stock_name: str = "",
                   output_dir: str = "output") -> str:
        """
        画单只股票近一年走势+均线+成交量副图。
        :param stock_code: 股票代码
        :param stock_name: 股票名称
        :param output_dir: 图片保存文件夹
        :return: 保存的文件路径
        """
        os.makedirs(output_dir, exist_ok=True)

        # 取近一年数据
        sql = f"""
       SELECT trade_date, close_price, volume
        FROM stock_price
        WHERE stock_code = '{stock_code}'
        AND trade_date >= DATE_SUB((
        SELECT MAX(trade_date)
        FROM stock_price
        WHERE stock_code = '
        {stock_code}'), INTERVAL 1 YEAR)
        ORDER BY trade_date
        """
        df = pd.read_sql(sql, self.engine)

        if df.empty:
            raise ValueError(f"stock_code {stock_code} has no data")

        df["trade_date"] = pd.to_datetime(df["trade_date"])

        # 均线
        df["MA5"] = df["close_price"].rolling(window=5).mean()
        df["MA20"] = df["close_price"].rolling(window=20).mean()
        df["MA60"] = df["close_price"].rolling(window=60).mean()

        # 上图价格 下图成交量
        fig, (ax1, ax2) = plt.subplots(
            2, 1,
            figsize=(14, 8),
            gridspec_kw={"height_ratios": [3, 1]},
            dpi=120,
        )

        # --- 价格+均线 ---
        ax1.plot(
            df["trade_date"], df["close_price"],
            label="close_price",
            color="#1a1a1a",
            linewidth=1.5,
            zorder=3,
        )
        ax1.plot(
            df["trade_date"], df["MA5"],
            label="MA5",
            color="#e67e22",
            linewidth=0.8,
            alpha=0.85,
        )
        ax1.plot(
            df["trade_date"], df["MA20"],
            label="MA20",
            color="#2980b9",
            linewidth=1.0,
            alpha=0.85,
        )
        ax1.plot(
            df["trade_date"], df["MA60"],
            label="MA60",
            color="#c0392b",
            linewidth=1.2,
            alpha=0.85,
            linestyle="--",
        )

        # 极值标注
        max_idx = df["close_price"].idxmax()
        min_idx = df["close_price"].idxmin()

        ax1.scatter(
            df.loc[max_idx, "trade_date"],
            df.loc[max_idx, "close_price"],
            color="#e74c3c",
            s=60,
            zorder=5,
            edgecolors="white",
            linewidth=1,
        )
        #图表添加注释 最高点
        ax1.annotate(
            f'high {df.loc[max_idx, "close_price"]:.1f}',
            xy=(
                df.loc[max_idx, "trade_date"],
                df.loc[max_idx, "close_price"],
            ),
            xytext=(12, 18),
            textcoords="offset points",
            fontsize=8,
            color="#e74c3c",
            arrowprops=dict(arrowstyle="-", color="#e74c3c", lw=0.8),
        )

        ax1.scatter(
            df.loc[min_idx, "trade_date"],
            df.loc[min_idx, "close_price"],
            color="#27ae60",
            s=60,
            zorder=5,
            edgecolors="white",
            linewidth=1,
        )
        #图表添加注释 最低点
        ax1.annotate(
            f'low {df.loc[min_idx, "close_price"]:.1f}',
            xy=(
                df.loc[min_idx, "trade_date"],
                df.loc[min_idx, "close_price"],
            ),
            xytext=(12, -22),
            textcoords="offset points",
            fontsize=8,
            color="#27ae60",
            arrowprops=dict(arrowstyle="-", color="#27ae60", lw=0.8),
        )

        # 日期刻度
        ax1.xaxis.set_major_locator(
            mdates.MonthLocator(interval=1)
        )
        ax1.xaxis.set_major_formatter(
            mdates.DateFormatter("%Y-%m")
        )
        plt.setp(
            ax1.xaxis.get_majorticklabels(),
            rotation=30,
            ha="right",
        )

        title_name = stock_name if stock_name else stock_code
        ax1.set_title(
            f"{title_name} ({stock_code}) 1Y Trend",
            fontsize=13,
            fontweight="bold",
            loc="left",
            pad=15,
        )
        ax1.legend(loc="upper left", fontsize=8)
        ax1.grid(True, alpha=0.25, linestyle="--")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # --- 成交量 ---
        colors = [
            "#e83825"
            if df["close_price"].iloc[i]
            < df["close_price"].iloc[i - 1]
            else "#26cd6b"
            for i in range(1, len(df))
        ]
        ax2.bar(
            df["trade_date"].iloc[1:],
            df["volume"].iloc[1:],
            color=colors,
            alpha=0.7,
            width=1.5,
        )
        ax2.set_ylabel("volume", fontsize=9)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.grid(True, alpha=0.2, linestyle="--")

        # 保存
        plt.tight_layout()
        filepath = os.path.join(output_dir, f"{stock_code}_trend.png")
        plt.savefig(
            filepath,
            dpi=150,
            bbox_inches="tight",
            facecolor="white",
        )
        plt.close()

        return filepath


# 使用示例
if __name__ == "__main__":
    analyzer = StockAnalyzer()
    path = analyzer.draw_trend(
        "512480", "半导体ETF", output_dir="output"
    )
    print(f"saved: {path}")