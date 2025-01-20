import pandas as pd
from pathlib import Path
from tqdm import tqdm


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
      df.index = [race_id] * len(df) # race_idをindexに(list * int = 繰り返しになる)
      dfs[race_id] = df
    
  # valueだけ繋げる
  concat_df = pd.concat(dfs.values())
  concat_df.index.name = "race_id"
  return concat_df