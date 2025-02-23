from pathlib import Path
import pandas as pd


def process_results(
    input_dir: Path,
    output_dir: Path,
    savefile_name: str,
    sex_mapping: dict = None,
) -> pd.DataFrame:
  """
  レース結果rawDFをinput_dirから読み込みoutput_dirに保存する

  Args:
    input_dir (str): レース結果rawdf(csvfile)があるディレクトリ
    output_dir (str): 出力先ディレクトリ
    savefile_name (str): 保存ファイル名
    sex_mapping (dict): 牡, 牝, セのラベルエンコーディング用
  Return:
    results (list[pd.DataFrame]): 全HTMLの表をUnionしたもの
  """
  # csv取得
  df = pd.read_csv(input_dir / savefile_name, sep="\t")
  # 順位
  df["rank"] = pd.to_numeric(df["着順"], errors="coerce")
  df.dropna(subset=["rank"], inplace=True)
  df["rank"] = df["rank"].astype(int)
  # 性別
  df["sex"] = df["性齢"].str[0].map(sex_mapping)
  df["age"] = df["性齢"].str[1:].astype(int)
  df["weight"] = df["馬体重"].str.extract(r"(\d+)").astype(int)
  df["weight_diff"] = df["馬体重"].str.extract(r"\((.+)\)").astype(int)
  df["weight_diff"] = pd.to_numeric(df["weight_diff"], errors="coerce")
  df["win_odds"] = df["単勝"].astype(float)
  df["popularity"] = df["人気"].astype(int)
  df["impost"] = df["斤量"].astype(float)
  df["bracket_number"] = df["枠番"].astype(int)
  df["post_position"] = df["馬番"].astype(int)
  # 各レース馬番順にソートする、「着順」順によるリーク防止
  df = df.sort_values(["race_id", "post_position"])


  # 使用する列を選択
  df = df[
    [
      "race_id",
      "horse_id",
      "jockey_id",
      "trainer_id",
      "owner_id",
      "rank",
      "bracket_number",
      "post_position",
      "sex",
      "age",
      "weight",
      "weight_diff",
      "win_odds",
      "popularity",
      "impost"
    ]
  ]

  df.columns = df.columns.str.replace(r"\s+", "", regex=True)
  output_dir.mkdir(parents=True, exist_ok=True)
  df.to_csv(output_dir / savefile_name, sep="\t", index=False)

  return df



def process_horse_results(
    input_dir: Path,
    output_dir: Path,
    savefile_name: str,
    race_type_mapping: dict,
    weather_mapping: dict,
    ground_state_mapping: dict,
    race_class_mapping: dict,
) -> pd.DataFrame:
  """

  Args:
  Return:
  """
  # csv取得
  df = pd.read_csv(input_dir / savefile_name, sep="\t")
  # 順位
  df["rank"] = pd.to_numeric(df["着順"], errors="coerce")
  df.dropna(subset=["rank"], inplace=True)
  # 日付
  df["date"] = pd.to_datetime(df["日付"])
  df["weather"] = df["天気"].map(weather_mapping)
  df["race_type"] = df["距離"].str[0].map(race_type_mapping)
  df["course_length"] = df["距離"].str.extract(r"(\d+)").astype(int)
  df["ground_state"] = df["馬場"].map(ground_state_mapping)
  df["rank_diff"] = df["着差"].map(lambda x: 0 if x < 0 else x)
  df["prize"] = df["賞金"].fillna(0)
  regex_race_class = "|".join(race_class_mapping.keys())
  df["race_class"] = (
    df["レース名"].str.extract(rf"({regex_race_class})")[0].map(race_class_mapping)
  )
  df.rename(columns={"頭数": "n_horses"}, inplace=True)

  # 使用する列を選択
  df = df[
    [
      "horse_id",
      "date",
      "rank",
      "prize",
      "rank_diff",
      "weather",
      "race_type",
      "course_length",
      "ground_state",
      "race_class",
      "n_horses"
    ]
  ]

  df.columns = df.columns.str.replace(r"\s+", "", regex=True)
  output_dir.mkdir(parents=True, exist_ok=True)
  df.to_csv(output_dir / savefile_name, sep="\t", index=False)

  return df