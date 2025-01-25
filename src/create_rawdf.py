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
      # horse_id列を追加
      horse_table_soup = BeautifulSoup(html, "lxml").find(
        "table", class_="race_table_01 nk_tb_common"
      )
      horse_id_list = get_ids_in_table(soup_table=horse_table_soup, target="horse")
      df["horse_id"] = horse_id_list  
      
      # index列追加
      df.index = [race_id] * len(df) # race_idをindexに(list * int = 繰り返しになる)
      dfs[race_id] = df
    
  # valueだけ繋げる
  concat_df = pd.concat(dfs.values())
  concat_df.index.name = "race_id"
  return concat_df



def get_ids_in_table(soup_table: BeautifulSoup, target: str) -> list[str]:
  target_a_list = soup_table.find_all("a", href=re.compile(rf"^/{target}/"))
  target_id_list = []
  for a in target_a_list:
    target_id = re.findall(r"\d{10}", a["href"])[0]
    target_id_list.append(target_id)
  return target_id_list