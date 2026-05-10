"""Plot 30-day trend: users vs engagement rate vs rebuffer %."""
import json
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime

with open("/tmp/30d-trend.json") as f:
    rows = json.load(f)

dates = [datetime.fromisoformat(r["date"]) for r in rows]
users = [r["users"] for r in rows]
eng = [r["eng_rate"] for r in rows]
rebuf = [r["rebuffer"] for r in rows]

plt.style.use("dark_background")
fig, ax1 = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor("#0a0a0a")
ax1.set_facecolor("#0a0a0a")

# Left axis: Users
color_users = "#6c63ff"
ax1.plot(dates, users, color=color_users, linewidth=2.5, marker="o",
         markersize=5, label="Daily Active Users", zorder=3)
ax1.set_ylabel("Daily Active Users", color=color_users, fontsize=12, fontweight="bold")
ax1.tick_params(axis="y", labelcolor=color_users)
ax1.tick_params(axis="x", colors="#aaaaaa")
ax1.grid(True, alpha=0.15, color="#444444", linestyle="--")
ax1.spines["top"].set_color("#333333")
ax1.spines["right"].set_color("#333333")
ax1.spines["bottom"].set_color("#333333")
ax1.spines["left"].set_color("#333333")

# Right axis: % metrics
ax2 = ax1.twinx()
color_eng = "#4ade80"
color_rebuf = "#f87171"
ax2.plot(dates, eng, color=color_eng, linewidth=2.5, marker="s",
         markersize=5, label="Engagement Rate (%)", zorder=3)
ax2.plot(dates, rebuf, color=color_rebuf, linewidth=2.5, marker="^",
         markersize=5, label="Rebuffer (%)", zorder=3)
ax2.set_ylabel("Percent (%)", color="#cccccc", fontsize=12, fontweight="bold")
ax2.tick_params(axis="y", labelcolor="#cccccc")

# Title + legend
fig.suptitle("VURT 30-Day Trend: Users vs Engagement vs Rebuffer",
             color="white", fontsize=16, fontweight="bold", y=0.98)
ax1.set_title(f"{rows[0]['date']} → {rows[-1]['date']}",
              color="#888888", fontsize=11, pad=8)

# Combined legend
l1, lab1 = ax1.get_legend_handles_labels()
l2, lab2 = ax2.get_legend_handles_labels()
leg = ax1.legend(l1 + l2, lab1 + lab2, loc="upper left",
                 facecolor="#111111", edgecolor="#333333",
                 labelcolor="white", fontsize=10)

# Date formatting
ax1.xaxis.set_major_formatter(DateFormatter("%m/%d"))
fig.autofmt_xdate(rotation=45)

plt.tight_layout()
out = "/home/workspace/Documents/VURT-30d-trend.png"
plt.savefig(out, dpi=140, facecolor="#0a0a0a", bbox_inches="tight")
print(f"Saved {out}")
