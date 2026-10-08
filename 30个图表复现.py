# -*- coding: utf-8 -*-
"""
=============================================================
 第二章 图表：30个可视化图表 Python 复现脚本
 仅依赖：pandas / numpy / matplotlib（你的 datavis 环境已装好）
 运行：python 30个图表复现.py
 输出：fig01.png ~ fig30.png（生成在脚本所在文件夹）
=============================================================
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

# ---------- 0. 文件路径（默认桌面，找不到会提示） ----------
DESKTOP = "C:/Users/wangziwen/Desktop"
FILE1 = f"{DESKTOP}/第二章 图表(前15).xlsx"   # 图 1~15
FILE2 = f"{DESKTOP}/第二章 图表(后15).xlsx"   # 图 16~30

# 测试用：如果设置了 CHART_DATA_DIR 环境变量，则从该目录读（云环境自检用）
if os.environ.get("CHART_DATA_DIR"):
    FILE1 = os.path.join(os.environ["CHART_DATA_DIR"], "第二章 图表(前15).xlsx")
    FILE2 = os.path.join(os.environ["CHART_DATA_DIR"], "第二章 图表(后15).xlsx")

# ---------- 1. 全局样式 ----------
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110

BLUE = "#4A90D9"
RED  = "#E15759"
GRAY = "#BFBFBF"
PALETTE = ["#4A90D9", "#E15759", "#59A14F", "#F28E2B", "#B07AA1", "#76B7B2"]

# ---------- 2. 工具函数 ----------
def save_fig(fig, name):
    fig.savefig(name, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("OK  ->", name)

def find_sheet(path, name):
    """按sheet名查找（容忍末尾空格/全角半角括号差异）"""
    xl = pd.ExcelFile(path)
    if name in xl.sheet_names:
        return name
    for n in xl.sheet_names:
        if n.strip() == name.strip():
            return n
    raise KeyError(f"文件 {path} 里没有sheet: {name}，实际有: {xl.sheet_names}")

def load_sheet(path, sheet):
    """读sheet：删除全空行列，第1行为表头，返回DataFrame"""
    df = pd.read_excel(path, sheet_name=find_sheet(path, sheet), header=None)
    df = df.replace(r"^\s*$", np.nan, regex=True)
    df = df.dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)
    headers = [str(v) if v is not None else f"col{i}" for i, v in enumerate(df.iloc[0].tolist())]
    data = df.iloc[1:].copy().reset_index(drop=True)
    data.columns = headers
    return data

def gradient_bars(ax, x, y, cmap_name="Blues", width=0.6, layers=26):
    """垂直渐变柱形：底部深、顶部浅"""
    cmap = plt.get_cmap(cmap_name)
    for xi, yi in zip(x, y):
        for k in range(layers):
            h = yi / layers
            color = cmap(1.0 - 0.75 * k / layers)
            ax.bar(xi, h, bottom=k * h, width=width, color=color,
                   edgecolor="none", align="center")

def rounded_gradient_bars(ax, x, y, cmap_name="Blues", width=0.62, layers=26):
    """圆角 + 垂直渐变柱形"""
    cmap = plt.get_cmap(cmap_name)
    for xi, yi in zip(x, y):
        r = min(0.28, yi * 0.45)
        box = FancyBboxPatch((xi - width / 2, 0), width, yi,
                             boxstyle=f"round,pad=0,rounding_size={r}",
                             fc="none", ec="none")
        ax.add_patch(box)
        for k in range(layers):
            h = yi / layers
            rect = Rectangle((xi - width / 2 + 0.004, k * h + 0.004),
                             width - 0.008, h - 0.004,
                             fc=cmap(1.0 - 0.75 * k / layers), ec="none")
            rect.set_clip_path(box)
            ax.add_patch(rect)

def catmull_rom(x, y, n=120):
    """Catmull-Rom样条平滑（不依赖scipy）"""
    pts = np.array([x, y], dtype=float).T
    m = len(pts)
    if m < 3:
        return x, y
    t = np.arange(m)
    t_new = np.linspace(0, m - 1, n)
    out = []
    for i in range(m - 1):
        p0 = pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(i + 2, m - 1)]
        seg = np.zeros((n // (m - 1) + 2, 2))
        for j in range(len(seg)):
            u = j / (len(seg) - 1)
            u2, u3 = u * u, u * u * u
            seg[j] = 0.5 * ((2 * p1) + (-p0 + p2) * u +
                            (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 +
                            (-p0 + 3 * p1 - 3 * p2 + p3) * u3)
        out.append(seg[:-1])
    out.append(np.array([pts[-1]]))
    sm = np.vstack(out)
    return sm[:, 0], sm[:, 1]

def draw_liquid(ax, value, phase=0.0):
    """水球图：圆形+波浪填充"""
    ax.set_aspect("equal")
    ax.axis("off")
    circle = Circle((0, 0), 1.0, fc="#EAF3FC", ec="#6FA8DC", lw=4, zorder=1)
    ax.add_patch(circle)
    xs = np.linspace(-1.2, 1.2, 500)
    level = -1 + 2 * value
    y_wave = level + 0.10 * np.sin(5 * np.pi * xs + phase) + 0.05 * np.sin(8 * np.pi * xs + 2 * phase)
    poly_pts = np.vstack([np.vstack([xs, y_wave]).T, [1.2, -1.3], [-1.2, -1.3]])
    poly = Polygon(poly_pts, fc="#6FA8DC", ec="none", zorder=2)
    poly.set_clip_path(circle)
    ax.add_patch(poly)
    line, = ax.plot(xs, y_wave, color="#4A90D9", lw=2, zorder=3)
    line.set_clip_path(circle)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.text(0, level + 0.20, f"{value*100:.0f}%", ha="center", va="center",
            fontsize=34, fontweight="bold", color="#2E5F8A", zorder=4)

def draw_gauge(ax, value, maxv=100):
    """仪表盘：半圆刻度 + 指针"""
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    N = 180
    theta = np.linspace(0, np.pi, N)
    width = np.pi / N * 0.95
    ax.bar(theta, np.ones(N), width=width, bottom=0.8, color="#E8EEF6",
           edgecolor="white", linewidth=0.6)
    nv = max(1, int(N * value / maxv))
    vtheta = np.linspace(0, np.pi * value / maxv, nv)
    ax.bar(vtheta, np.ones(nv), width=width, bottom=0.8, color=BLUE,
           edgecolor="white", linewidth=0.6)
    ang = np.pi * value / maxv
    ax.plot([0, ang], [0, 0.8], color="#333333", lw=3)
    ax.scatter([0], [0], s=70, color="#333333", zorder=5)
    for tick in [0, 25, 50, 75, 100]:
        ax.text(np.pi * tick / maxv, 1.10, str(tick), ha="center", va="center", fontsize=11)
    ax.text(ang, 0.52, f"{value:.0f}", ha="center", fontsize=22,
            fontweight="bold", color=RED)
    ax.set_ylim(0, 1.25)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["polar"].set_visible(False)

def rose_chart(ax, labels, values, ring=False, base=0.25, scale=2.0):
    """南丁格尔玫瑰图（极坐标柱）"""
    n = len(labels)
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    width = 2 * np.pi / n
    vals = np.array(values) * scale
    if ring:
        ax.bar(theta, vals, width=width, bottom=base, color=PALETTE[:n],
               edgecolor="white", linewidth=2)
    else:
        ax.bar(theta, vals, width=width, color=PALETTE[:n],
               edgecolor="white", linewidth=2)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(theta)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticklabels([])
    ax.grid(True, alpha=0.3)

def pct(v):
    return f"{v*100:+.1f}%"

# ============================================================
#  图 1~15（第二章 图表(前15).xlsx）
# ============================================================
def fig01():
    df = load_sheet(FILE1, "1 渐变柱形图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    gradient_bars(ax, np.arange(len(labels)), vals)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_title("1 渐变柱形图")
    for i, v in enumerate(vals):
        ax.text(i, v + 40, f"{v:.0f}", ha="center", va="bottom")
    ax.margins(y=0.18)
    save_fig(fig, "fig01_渐变柱形图.png")

def fig02():
    df = load_sheet(FILE1, "2 带均值柱形图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    mean_v = pd.to_numeric(df.iloc[:, 2]).mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(np.arange(len(labels)), vals, width=0.6, color=BLUE)
    ax.axhline(mean_v, color=RED, linestyle="--", lw=1.5,
               label=f"均值 {mean_v:.1f}")
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_title("2 带均值柱形图")
    ax.legend()
    for i, v in enumerate(vals):
        ax.text(i, v + 40, f"{v:.0f}", ha="center", va="bottom")
    ax.margins(y=0.18)
    save_fig(fig, "fig02_带均值柱形图.png")

def fig03():
    df = load_sheet(FILE1, "3 渐变圆角柱形图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    rounded_gradient_bars(ax, np.arange(len(labels)), vals)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_title("3 渐变圆角柱形图")
    for i, v in enumerate(vals):
        ax.text(i, v + 15, f"{v:.0f}", ha="center", va="bottom")
    ax.margins(y=0.18)
    save_fig(fig, "fig03_渐变圆角柱形图.png")

def fig04():
    df = load_sheet(FILE1, "4 标注柱形图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(np.arange(len(labels)), vals, width=0.55, color=BLUE)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_title("4 标注柱形图")
    for i, v in enumerate(vals):
        ax.text(i, v + 80, f"{v:,.0f}", ha="center", va="bottom")
    ax.margins(y=0.18)
    save_fig(fig, "fig04_标注柱形图.png")

def fig05():
    df = load_sheet(FILE1, "5 层叠柱形图")
    labels = df.iloc[:, 0].tolist()
    sales = pd.to_numeric(df.iloc[:, 1]).values
    profit = pd.to_numeric(df.iloc[:, 2]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    ax.bar(x, sales, width=0.55, color=BLUE, label="销售额")
    ax.bar(x, profit, width=0.55, bottom=sales, color="#7FB3E6", label="利润额")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("5 层叠柱形图")
    ax.legend()
    for i, (s, p) in enumerate(zip(sales, profit)):
        ax.text(i, s / 2, f"{s:,.0f}", ha="center", va="center", color="white", fontsize=9)
        ax.text(i, s + p / 2, f"{p:,.0f}", ha="center", va="center", color="white", fontsize=9)
    ax.margins(y=0.15)
    save_fig(fig, "fig05_层叠柱形图.png")

def fig06():
    df = load_sheet(FILE1, "6 蝴蝶图")
    labels = df.iloc[:, 0].tolist()
    v2022 = pd.to_numeric(df.iloc[:, 2]).values
    v2021 = pd.to_numeric(df.iloc[:, 4]).values
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(labels))
    ax.barh(y, -v2021, height=0.55, color="#9CC3E5", label="2021年销量")
    ax.barh(y, v2022, height=0.55, color=BLUE, label="2022年销量")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.axvline(0, color="gray", lw=0.8)
    ax.set_title("6 蝴蝶图")
    ax.legend()
    ax.margins(x=0.1)
    save_fig(fig, "fig06_蝴蝶图.png")

def fig07():
    df = load_sheet(FILE1, "7 蝴蝶图")
    labels = df.iloc[:, 0].tolist()
    v2022 = pd.to_numeric(df.iloc[:, 1]).values
    v2021 = pd.to_numeric(df.iloc[:, 2]).values
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(labels))
    ax.barh(y, -v2021, height=0.5, color="#9CC3E5", label="2021年")
    ax.barh(y, v2022, height=0.5, color=BLUE, label="2022年")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.axvline(0, color="gray", lw=0.8)
    ax.set_title("7 蝴蝶图")
    ax.legend()
    for i, v in enumerate(v2022):
        ax.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=9)
    for i, v in enumerate(v2021):
        ax.text(-v - 0.01, i, f"{v:.2f}", ha="right", va="center", fontsize=9)
    ax.margins(x=0.15)
    save_fig(fig, "fig07_蝴蝶图.png")

def fig08():
    df = load_sheet(FILE1, "8 数值百分比")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    yoy = pd.to_numeric(df.iloc[:, 4]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(np.arange(len(labels)), vals, width=0.55, color=BLUE)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_title("8 数值百分比")
    for i, (v, yv) in enumerate(zip(vals, yoy)):
        ax.text(i, v + 60, f"{yv*100:.1f}%", ha="center", va="bottom", color=RED)
    ax.margins(y=0.18)
    save_fig(fig, "fig08_数值百分比.png")

def fig09():
    df = load_sheet(FILE1, "9 对比柱形图")
    labels = df.iloc[:, 0].tolist()
    v2021 = pd.to_numeric(df.iloc[:, 1]).values
    v2022 = pd.to_numeric(df.iloc[:, 2]).values
    diff = pd.to_numeric(df.iloc[:, 3]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, v2021, width=w, color="#9CC3E5", label="2021销量")
    ax.bar(x + w / 2, v2022, width=w, color=BLUE, label="2022销量")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("9 对比柱形图")
    ax.legend()
    for i, d in enumerate(diff):
        ax.text(i, max(v2021[i], v2022[i]) + 80, f"差值{d:,.0f}",
                ha="center", va="bottom", fontsize=9, color=RED)
    ax.margins(y=0.22)
    save_fig(fig, "fig09_对比柱形图.png")

def fig10():
    df = load_sheet(FILE1, "10 甘特图")
    names = df.iloc[:, 0].tolist()
    start = pd.to_datetime(df.iloc[:, 1])
    days = pd.to_numeric(df.iloc[:, 4]).values
    comp = pd.to_numeric(df.iloc[:, 3]).values
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(names))[::-1]
    ax.barh(y, days, left=mdates.date2num(start), height=0.5, color=BLUE)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.set_title("10 甘特图")
    for yy, s, d, c in zip(y, start, days, comp):
        ax.text(mdates.date2num(s) + d + 0.5, yy, f"{c:.0%}", va="center", fontsize=9)
    ax.margins(x=0.2)
    save_fig(fig, "fig10_甘特图.png")

def fig11():
    df = load_sheet(FILE1, "11 平滑折线图")
    labels = [f"{r[0]}{r[1]}" for r in df.iloc[:, :2].values.tolist()]
    vals = pd.to_numeric(df.iloc[:, 2]).values
    x = np.arange(len(vals))
    sx, sy = catmull_rom(x, vals)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(sx, sy, color=BLUE, lw=2)
    ax.scatter(x, vals, color=RED, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("11 平滑折线图")
    ax.margins(y=0.15)
    save_fig(fig, "fig11_平滑折线图.png")

def fig12():
    df = load_sheet(FILE1, "12 菱形走势图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    x = np.arange(len(vals))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, vals, color=BLUE, lw=2, marker="D", markersize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("12 菱形走势图")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.015, f"{v*100:.1f}%", ha="center", va="bottom")
    ax.set_ylim(0, max(vals) * 1.25)
    save_fig(fig, "fig12_菱形走势图.png")

def fig13():
    df = load_sheet(FILE1, "13 对比折线图")
    labels = df.iloc[:, 0].tolist()
    v2021 = pd.to_numeric(df.iloc[:, 1]).values
    v2022 = pd.to_numeric(df.iloc[:, 2]).values
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, v2021, color="#9CC3E5", marker="o", lw=2, label="2021年")
    ax.plot(x, v2022, color=RED, marker="o", lw=2, label="2022年")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("13 对比折线图")
    ax.legend()
    ax.margins(y=0.15)
    save_fig(fig, "fig13_对比折线图.png")

def fig14():
    df = load_sheet(FILE1, "14 单值圆环图")
    value = float(df["完成率"].iloc[0])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie([value, 1 - value], colors=[BLUE, "#E8EEF6"], startangle=90,
           counterclock=False, wedgeprops=dict(width=0.32, edgecolor="white"))
    ax.text(0, 0, f"{value*100:.0f}%", ha="center", va="center", fontsize=26, fontweight="bold")
    ax.set_title("14 单值圆环图")
    ax.axis("equal")
    save_fig(fig, "fig14_单值圆环图.png")

def fig15():
    df = load_sheet(FILE1, "15 水球图")
    value = float(df["完成率"].iloc[0])
    fig, ax = plt.subplots(figsize=(6, 5))
    draw_liquid(ax, value)
    ax.set_title("15 水球图")
    save_fig(fig, "fig15_水球图.png")

# ============================================================
#  图 16~30（第二章 图表(后15).xlsx）
# ============================================================
def fig16():
    df = load_sheet(FILE2, "16 波浪水球图")
    value = float(df["完成率"].iloc[0])
    fig, ax = plt.subplots(figsize=(6, 5))
    draw_liquid(ax, value, phase=1.2)
    ax.set_title("16 波浪水球图")
    save_fig(fig, "fig16_波浪水球图.png")

def fig17():
    df = load_sheet(FILE2, "17 玉玦图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    gaps = pd.to_numeric(df.iloc[:, 2]).values
    sizes = np.r_[vals, gaps.sum()]
    colors = PALETTE[:len(labels)] + ["white"]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, colors=colors, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.34, edgecolor="white"),
           labels=labels + [""], labeldistance=1.15)
    ax.set_title("17 玉玦图")
    ax.axis("equal")
    save_fig(fig, "fig17_玉玦图.png")

def fig18():
    df = load_sheet(FILE2, "18 跑道图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    gap = pd.to_numeric(df.iloc[:, 2]).values
    total = vals.sum()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.pie(list(vals) + [gap[0]], colors=PALETTE[:len(labels)] + ["#E8EEF6"],
           startangle=90, counterclock=False,
           wedgeprops=dict(width=0.35, edgecolor="white"),
           labels=labels + [""], labeldistance=1.1)
    ax.text(0, 0, f"{total:,.0f}", ha="center", va="center",
            fontsize=22, fontweight="bold", color="#333")
    ax.text(0, -0.22, "总人数", ha="center", va="center", fontsize=12, color="#777")
    ax.set_title("18 跑道图")
    ax.axis("equal")
    save_fig(fig, "fig18_跑道图.png")

def fig19():
    df = load_sheet(FILE2, "19 南丁格尔圆饼图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection="polar"))
    rose_chart(ax, labels, vals)
    ax.set_title("19 南丁格尔圆饼图")
    save_fig(fig, "fig19_南丁格尔圆饼图.png")

def fig20():
    df = load_sheet(FILE2, "20 南丁格尔圆环图")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection="polar"))
    rose_chart(ax, labels, vals, ring=True, base=0.3)
    ax.set_title("20 南丁格尔圆环图")
    save_fig(fig, "fig20_南丁格尔圆环图.png")

def fig20b():
    df = load_sheet(FILE2, "20 南丁格尔（PPT）")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection="polar"))
    rose_chart(ax, labels, vals, ring=True, base=0.25)
    ax.set_title("20 南丁格尔（PPT）")
    save_fig(fig, "fig20b_南丁格尔PPT.png")

def fig22():
    df = load_sheet(FILE2, "22 仪表盘图")
    col = "指针数值" if "指针数值" in df.columns else df.columns[-1]
    value = float(df[col].iloc[0])
    fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(projection="polar"))
    draw_gauge(ax, value)
    ax.set_title("22 仪表盘图")
    save_fig(fig, "fig22_仪表盘图.png")

def fig23():
    df = load_sheet(FILE2, "23 柱形折线图")
    labels = df.iloc[:, 0].tolist()
    sales = pd.to_numeric(df.iloc[:, 1]).values
    yoy = pd.to_numeric(df.iloc[:, 2]).values
    x = np.arange(len(labels))
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(x, sales, width=0.5, color=BLUE, label="销售量")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("销售量")
    ax2 = ax1.twinx()
    ax2.plot(x, yoy * 100, color=RED, marker="o", lw=2, label="同比(%)")
    ax2.set_ylabel("同比(%)")
    ax2.set_ylim(0, max(yoy * 100) * 1.4)
    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lab1 + lab2, loc="upper left")
    ax1.set_title("23 柱形折线图")
    save_fig(fig, "fig23_柱形折线图.png")

def fig24():
    df = load_sheet(FILE2, "24 目标柱形图")
    labels = df.iloc[:, 0].tolist()
    actual = pd.to_numeric(df.iloc[:, 1]).values
    target = pd.to_numeric(df.iloc[:, 2]).values
    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - w / 2, actual, width=w, color=BLUE, label="实际销量")
    ax.bar(x + w / 2, target, width=w, color="#9CC3E5", label="目标销量")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("24 目标柱形图")
    ax.legend()
    for i, (a, t) in enumerate(zip(actual, target)):
        ax.text(i - w / 2, a + 15, f"{a:.0f}", ha="center", va="bottom", fontsize=9)
        ax.text(i + w / 2, t + 15, f"{t:.0f}", ha="center", va="bottom", fontsize=9)
    ax.margins(y=0.15)
    save_fig(fig, "fig24_目标柱形图.png")

def fig25():
    df = load_sheet(FILE2, "25 子弹图")
    labels = df.iloc[:, 0].tolist()
    actual = pd.to_numeric(df.iloc[:, 1]).values
    target = pd.to_numeric(df.iloc[:, 2]).values
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(labels))[::-1]
    for i, (a, t) in enumerate(zip(actual, target)):
        yy = y[i]
        ax.barh(yy, t * 1.25, height=0.5, color="#EDEDED")
        ax.barh(yy, a, height=0.32, color=BLUE)
        ax.plot([t, t], [yy - 0.28, yy + 0.28], color="#333", lw=2.5)
        ax.text(t * 1.25, yy, f"目标{t:.0f}", va="center", ha="left", fontsize=9, color="#666")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_title("25 子弹图")
    ax.margins(x=0.15)
    save_fig(fig, "fig25_子弹图.png")

def fig26():
    df = load_sheet(FILE2, "26 柱形圆")
    labels = df.iloc[:, 0].tolist()
    vals = pd.to_numeric(df.iloc[:, 1]).values
    cap = pd.to_numeric(df.iloc[:, 2]).values[0]
    yoy = pd.to_numeric(df.iloc[:, 3]).values
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    ax.bar(x, vals, width=0.55, color=BLUE)
    ax.axhline(cap, color=RED, linestyle="--", lw=1.5, label=f"参考线 {cap:,.0f}")
    for i, (v, yv) in enumerate(zip(vals, yoy)):
        ax.scatter(i, v, s=70, color="white", edgecolor=RED, zorder=3)
        ax.text(i, v + 80, f"{yv*100:+.0f}%", ha="center", va="bottom", color=RED)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("26 柱形圆")
    ax.legend()
    ax.margins(y=0.18)
    save_fig(fig, "fig26_柱形圆.png")

def fig27():
    df = load_sheet(FILE2, "27 簇状柱形折线图")
    labels = df.iloc[:, 0].tolist()
    v2022 = pd.to_numeric(df.iloc[:, 1]).values
    v2021 = pd.to_numeric(df.iloc[:, 2]).values
    yoy = pd.to_numeric(df.iloc[:, 3]).values
    x = np.arange(len(labels))
    w = 0.35
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(x - w / 2, v2022, width=w, color=BLUE, label="2022销量")
    ax1.bar(x + w / 2, v2021, width=w, color="#9CC3E5", label="2021销量")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("销量")
    ax2 = ax1.twinx()
    ax2.plot(x, yoy * 100, color=RED, marker="o", lw=2, label="同比(%)")
    ax2.set_ylabel("同比(%)")
    ax2.set_ylim(0, max(yoy * 100) * 1.5)
    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lab1 + lab2, loc="upper left")
    ax1.set_title("27 簇状柱形折线图")
    save_fig(fig, "fig27_簇状柱形折线图.png")

def fig28():
    df = load_sheet(FILE2, "28 复合柱形图")
    labels = df.iloc[:, 0].tolist()
    monthly = pd.to_numeric(df.iloc[:, 1]).values
    quarter = pd.to_numeric(df.iloc[:, 2]).values
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, quarter, width=0.8, color="#C8DCF0", label="季度销量")
    ax.bar(x, monthly, width=0.42, color=BLUE, label="月度销量")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("28 复合柱形图")
    ax.legend()
    for i, (m, q) in enumerate(zip(monthly, quarter)):
        ax.text(i, m + 60, f"{m:,.0f}", ha="center", va="bottom", fontsize=9)
    ax.margins(y=0.15)
    save_fig(fig, "fig28_复合柱形图.png")

def fig29():
    df = load_sheet(FILE2, "29 滑珠图")
    labels = df.iloc[:, 0].tolist()
    rate = pd.to_numeric(df.iloc[:, 1]).values
    rest = pd.to_numeric(df.iloc[:, 2]).values
    y = np.arange(len(labels))[::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (r, s) in enumerate(zip(rate, rest)):
        ax.plot([s, r], [y[i], y[i]], color="#A0A0A0", lw=2, zorder=1)
    ax.scatter(rest, y, s=140, color="#C8C8C8", zorder=3, label="未完成占比")
    ax.scatter(rate, y, s=140, color=BLUE, zorder=3, label="完成率")
    for i, r in enumerate(rate):
        ax.text(r + 0.02, y[i], f"{r*100:.0f}%", va="center", fontsize=10, color=BLUE)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_title("29 滑珠图")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1.15)
    save_fig(fig, "fig29_滑珠图.png")

def fig30():
    df = load_sheet(FILE2, "30 对比滑珠图")
    labels = df.iloc[:, 0].tolist()
    v2022 = pd.to_numeric(df.iloc[:, 1]).values
    v2021 = pd.to_numeric(df.iloc[:, 2]).values
    y = np.arange(len(labels))[::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (a, b) in enumerate(zip(v2022, v2021)):
        ax.plot([b, a], [y[i], y[i]], color="#A0A0A0", lw=2, zorder=1)
    ax.scatter(v2021, y, s=140, color="#9CC3E5", zorder=3, label="2021完成率")
    ax.scatter(v2022, y, s=140, color=BLUE, zorder=3, label="2022完成率")
    for i, v in enumerate(v2022):
        ax.text(v + 0.02, y[i], f"{v*100:.0f}%", va="center", fontsize=10, color=BLUE)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_title("30 对比滑珠图")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1.15)
    save_fig(fig, "fig30_对比滑珠图.png")

# ============================================================
#  执行入口
# ============================================================
FIGS = [
    ("01渐变柱形图", fig01), ("02带均值柱形图", fig02), ("03渐变圆角柱形图", fig03),
    ("04标注柱形图", fig04), ("05层叠柱形图", fig05), ("06蝴蝶图", fig06),
    ("07蝴蝶图", fig07), ("08数值百分比", fig08), ("09对比柱形图", fig09),
    ("10甘特图", fig10), ("11平滑折线图", fig11), ("12菱形走势图", fig12),
    ("13对比折线图", fig13), ("14单值圆环图", fig14), ("15水球图", fig15),
    ("16波浪水球图", fig16), ("17玉玦图", fig17), ("18跑道图", fig18),
    ("19南丁格尔圆饼图", fig19), ("20南丁格尔圆环图", fig20), ("20南丁格尔PPT", fig20b),
    ("22仪表盘图", fig22), ("23柱形折线图", fig23), ("24目标柱形图", fig24),
    ("25子弹图", fig25), ("26柱形圆", fig26), ("27簇状柱形折线图", fig27),
    ("28复合柱形图", fig28), ("29滑珠图", fig29), ("30对比滑珠图", fig30),
]

def run_all():
    ok = 0
    for name, fn in FIGS:
        try:
            fn()
            ok += 1
        except Exception as e:
            print(f"[失败] {name}: {e}")
    print(f"\n完成 {ok}/{len(FIGS)} 张。失败的图请把报错发给我。")

if __name__ == "__main__":
    run_all()
