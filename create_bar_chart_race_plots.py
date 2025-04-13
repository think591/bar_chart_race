##### 概念驗證 #####

#* 引入數據
from create_bar_chart_race_data import CreateBarChartRaceData

create_bar_chart_race_data = CreateBarChartRaceData()
cumulative_votes_by_time_candidate = create_bar_chart_race_data.create_cumulative_votes_by_time_candidate()
covid_19_confirmed = create_bar_chart_race_data.create_covid_19_confirmed()
print(cumulative_votes_by_time_candidate)
print(covid_19_confirmed)


# 投開票完成時間：使用 plotly.express 模組

import plotly.express as px
import pandas as pd

early_collected = cumulative_votes_by_time_candidate[cumulative_votes_by_time_candidate["collected_at"] < pd.to_datetime("2024-01-13 17:30:00")]
print(early_collected)

max_cumulative_votes = early_collected["cumulative_sum_votes"].max()
print(max_cumulative_votes)

fig = px.bar(early_collected,
             x="cumulative_sum_votes", y="candidate", color="candidate",
             animation_frame="collected_at", animation_group="candidate",   # animation_frame 時間軸， animation_group 分組依據
             range_x=[0, max_cumulative_votes])                             # 固定 軸的 數值
fig.show()



# 2020 年 Covid 19 確診人數：使用 plotly.express 模組

max_confirmed = covid_19_confirmed["confirmed"].max()

fig = px.bar(covid_19_confirmed,
             x="confirmed", y="country", color="country", 
             animation_frame="reported_on", animation_group="country",
             range_x=[0, max_confirmed])
fig.update_yaxes(categoryorder="total ascending")
fig.show()


##### 成品 #####

# 使用開源模組 raceplotly 模組讓成品的效果更好 : pip install raceplotly
#* 加快動畫播放的速度。
#* 讓領先互換的轉換更平順。

# 投開票完成時間：使用 raceplotly 模組
#* item_column: 指定類別變數。
#* value_column: 指定數值變數。
#* time_column: 指定日期時間變數。
#* top_entries: 預設為 10。
#* frame_duration: 每幀動畫停留的毫秒數。

from raceplotly.plots import barplot

vote_raceplot = barplot(early_collected, item_column="candidate", value_column="cumulative_sum_votes",
                        time_column="collected_at", top_entries=3)
fig = vote_raceplot.plot(item_label = "Votes collected by candidate", value_label="Number of votes",
                         frame_duration=50)
fig.write_html("bar_chart_race_votes.html")



# 2020 年 Covid 19 確診人數：使用 raceplotly 模組

confirmed_raceplot = barplot(covid_19_confirmed, item_column="country", value_column="confirmed",
                             time_column="reported_on")
fig = confirmed_raceplot.plot(item_label = "Confirmed by country", value_label="Number of cases",
                              frame_duration=50)
fig.write_html("bar_chart_race_confirmed.html")
