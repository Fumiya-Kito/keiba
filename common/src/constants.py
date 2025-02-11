from pathlib import Path

# プロジェクトルートを定義
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 各ディレクトリ定数をプロジェクトルート基準で定義
RACE_DETAIL_HTML_DIR = PROJECT_ROOT / "data" / "html" / "race"
HORSE_DETAIL_HTML_DIR = PROJECT_ROOT / "data" / "html" / "horse"
RACE_RESULTS_RAWDF_DIR = PROJECT_ROOT / "data" / "rawdf" / "results"
RACE_DETAIL_ID_DIR = PROJECT_ROOT / "data" / "pkl" / "race_id"
