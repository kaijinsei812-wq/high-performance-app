"""
Prometheus メトリクス収集
prometheus-fastapi-instrumentatorで自動計装 + カスタムメトリクス追加
"""
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge

# カスタムメトリクス
user_registrations_total = Counter(
    "user_registrations_total",
    "登録ユーザー総数"
)

login_failures_total = Counter(
    "login_failures_total",
    "ログイン失敗回数"
)

items_created_total = Counter(
    "items_created_total",
    "作成アイテム総数"
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Redisキャッシュヒット数"
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Redisキャッシュミス数"
)

active_db_connections = Gauge(
    "active_db_connections",
    "アクティブなDBコネクション数"
)


def setup_metrics(app):
    """FastAPIアプリにPrometheusメトリクスを設定する"""
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/metrics"],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    ).instrument(app).expose(app, endpoint="/metrics")
    return app
