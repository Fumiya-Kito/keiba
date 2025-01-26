import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup

def create_results(html_path_list: list[Path]) -> pd.DataFrame:
  """
  レースページのHTMLを読み込んでレース結果テーブルに加工

  Args:
    html_path_list (list[str]): HTMLのパス(pathをreadしてHTMLを取り出す)
  Return:
    results (list[pd.DataFrame]): 全HTMLの表をUnionしたもの
  """
  dfs = {}
  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      race_id = html_path.stem
      html = f.read()
      df = pd.read_html(html)[0]
      soup = BeautifulSoup(html, "lxml").find(
        "table", class_="race_table_01 nk_tb_common"
      )
      # horse_id列を追加
      horse_id_list = get_ids_in_table(soup_table=soup, target="horse", id_length=10)
      df["horse_id"] = horse_id_list  
      
      # ジョッキーIDを取得 
      jockey_id_list = get_ids_in_table(soup_table=soup, target="jockey", id_length=5)
      df["jockey_id"] = jockey_id_list
      
      # 調教師IDを取得 
      trainer_id_list = get_ids_in_table(soup_table=soup, target="trainer", id_length=5)
      df["trainer_id"] = trainer_id_list
      
      # オーナーIDを取得 
      owner_id_list = get_ids_in_table(soup_table=soup, target="owner", id_length=6)
      df["owner_id"] = owner_id_list
      
      # index列追加
      df.index = [race_id] * len(df) # race_idをindexに(list * int = 繰り返しになる)
      dfs[race_id] = df
    
  # valueだけ繋げる
  concat_df = pd.concat(dfs.values())
  concat_df.index.name = "race_id"
  return concat_df



def get_ids_in_table(soup_table: BeautifulSoup, target: str, id_length: int) -> list[str]:
  target_a_list = soup_table.find_all("a", href=re.compile(rf"^/{target}/"))
  target_id_list = []
  for a in target_a_list:
    target_id = re.findall(rf"\d{{{id_length}}}", a["href"])[0]
    target_id_list.append(target_id)
  return target_id_list