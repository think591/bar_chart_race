
# 以 pandas 模組載入 taiwan_presidential_election_2024.db 資料

import sqlite3
import pandas as pd

connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
sql_query = """
SELECT polling_places.county,
       polling_places.polling_place,
       candidates.candidate,
       SUM(votes.votes) AS sum_votes      -- 得票數加總
  FROM votes
  JOIN candidates
    ON votes.candidate_id = candidates.id
  JOIN polling_places
    ON votes.polling_place_id = polling_places.id
 GROUP BY polling_places.county,
          polling_places.polling_place,
          candidates.candidate;
"""
votes_by_county_polling_place_candidate = pd.read_sql(sql_query, con=connection)
connection.close()

print(votes_by_county_polling_place_candidate.head())



# 以 pandas 模組載入 113全國投開票所完成時間.xlsx
#* skiprows=[0, 1, 2]: 略過試算表的前三列不要載入。
#* 安裝 openpyxl

votes_collected = pd.read_excel("data/113全國投開票所完成時間.xlsx", skiprows=[0, 1, 2])
votes_collected.columns = ["county", "town", "polling_place", "collected_at", "number_of_voters"]
votes_collected = votes_collected[["county", "polling_place", "collected_at"]]
print(votes_collected)


# 連結候選人得票數與投開票所完成時間
#* 以 county 與 polling_place 作為連接鍵。
#* 以候選人得票數作為左資料表採用 LEFT JOIN

merged = pd.merge(votes_by_county_polling_place_candidate, votes_collected,
                  left_on=["county", "polling_place"], right_on=["county", "polling_place"],
                  how="left")
merged


# 以候選人和完成時間做為分組依據加總票數

votes_by_collected_at_candidate = merged.groupby(["collected_at", "candidate"])["sum_votes"].sum().reset_index()
print(votes_by_collected_at_candidate)


# 以候選人作為分組依據累計加總票數
#* 使用 cumsum()（cumulative sum）方法。

cum_sum = votes_by_collected_at_candidate.groupby("candidate")["sum_votes"].cumsum()
votes_by_collected_at_candidate["cumulative_sum_votes"] = cum_sum
print(votes_by_collected_at_candidate.head(10))

# 調整日期時間格式為 ISO-8601
#* 定義調整格式的函數 adjust_datetime_format() 並以 map() 方法應用。
#* 使用 pd.to_datetime() 函數將文字格式轉為日期時間格式。

def adjust_datetime_format(x: str):
    date_part, time_part = x.split()             # split 預設 分割符 是“空白”
    date_part = "2024-01-13"
    datetime_iso_8601 = f"{date_part} {time_part}"
    return datetime_iso_8601

#* 文字格式的更新
votes_by_collected_at_candidate["collected_at"] = votes_by_collected_at_candidate["collected_at"].map(adjust_datetime_format)
#* 資料格式的更新
votes_by_collected_at_candidate["collected_at"] = pd.to_datetime(votes_by_collected_at_candidate["collected_at"])

print(votes_by_collected_at_candidate)


# 以 pandas 模組載入 covid_19.db 資料
#* 篩選日期小於 2020-12-31 的資料，因為在這個時間點以前確診人數前 10 的國家排名比較有變化。

connection = sqlite3.connect("data/covid_19.db")
sql_query = """
SELECT reported_on,
       country,
       confirmed
  FROM time_series
 WHERE reported_on <= '2020-12-31';
"""
covid_19_confirmed = pd.read_sql(sql_query, con=connection)
connection.close()
print(covid_19_confirmed)


# 將每個日期前 10 大累積確診的國家找出來
#* 使用 nlargest() 方法。
#* 來源：https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.SeriesGroupBy.nlargest.html

#* print(covid_19_confirmed.groupby("reported_on")["confirmed"].nlargest(10))

#* reset_index() 後，欄位命名為 level_1
#* print(covid_19_confirmed.groupby("reported_on")["confirmed"].nlargest(10).reset_index()["level_1"].values)
nlargest_index = covid_19_confirmed.groupby("reported_on")["confirmed"].nlargest(10).reset_index()["level_1"].values
#* location
covid_19_confirmed = covid_19_confirmed.loc[nlargest_index, :].reset_index(drop=True)

print(covid_19_confirmed.head(10))
print(covid_19_confirmed.tail(10))


# 整理程式碼為一個類別 CreateBarChartRaceData
class CreateBarChartRaceData:

    def adjust_datetime_format(self, x):
        date_part, time_part = x.split()
        date_part = "2024-01-13"
        datetime_iso_8601 = f"{date_part} {time_part}"
        return datetime_iso_8601
    
    def create_cumulative_votes_by_time_candidate(self):
        connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
        sql_query = """
        SELECT polling_places.county,
               polling_places.polling_place,
               candidates.candidate,
               SUM(votes.votes) AS sum_votes
          FROM votes
          JOIN candidates
            ON votes.candidate_id = candidates.id
          JOIN polling_places
            ON votes.polling_place_id = polling_places.id
         GROUP BY polling_places.county,
                  polling_places.polling_place,
                  candidates.candidate;
        """
        votes_by_county_polling_place_candidate = pd.read_sql(sql_query, con=connection)
        connection.close()
        votes_collected = pd.read_excel("data/113全國投開票所完成時間.xlsx", skiprows=[0, 1, 2])
        votes_collected.columns = ["county", "town", "polling_place", "collected_at", "number_of_voters"]
        votes_collected = votes_collected[["county", "polling_place", "collected_at"]]
        merged = pd.merge(votes_by_county_polling_place_candidate, votes_collected,
                  left_on=["county", "polling_place"], right_on=["county", "polling_place"], how="left")
        votes_by_collected_at_candidate = merged.groupby(["collected_at", "candidate"])["sum_votes"].sum().reset_index()
        cum_sum = votes_by_collected_at_candidate.groupby("candidate")["sum_votes"].cumsum()
        votes_by_collected_at_candidate["cumulative_sum_votes"] = cum_sum
        votes_by_collected_at_candidate["collected_at"] = votes_by_collected_at_candidate["collected_at"].map(self.adjust_datetime_format)
        votes_by_collected_at_candidate["collected_at"] = pd.to_datetime(votes_by_collected_at_candidate["collected_at"])
        return votes_by_collected_at_candidate
    
    def create_covid_19_confirmed(self):
        connection = sqlite3.connect("data/covid_19.db")
        sql_query = """
        SELECT reported_on,
               country,
               confirmed
          FROM time_series
         WHERE reported_on <= '2020-12-31';
        """
        covid_19_confirmed = pd.read_sql(sql_query, con=connection)
        connection.close()
        nlargest_index = covid_19_confirmed.groupby("reported_on")["confirmed"].nlargest(10).reset_index()["level_1"].values
        covid_19_confirmed = covid_19_confirmed.loc[nlargest_index, :].reset_index(drop=True)
        return covid_19_confirmed
    

# 檢查類別 CreateBarChartRaceData 能否順利運行

create_bar_chart_race_data = CreateBarChartRaceData()
cumulative_votes_by_time_candidate = create_bar_chart_race_data.create_cumulative_votes_by_time_candidate()
covid_19_confirmed = create_bar_chart_race_data.create_covid_19_confirmed()
print(cumulative_votes_by_time_candidate)
print(covid_19_confirmed)