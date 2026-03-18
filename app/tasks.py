"""
Celery タスク定義
"""
import time
import logging
from app.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_item_async(self, item_id: int, user_id: int):
    """アイテムの非同期処理タスク（例：レポート生成、通知送信等）"""
    try:
        logger.info(f"🔄 非同期処理開始: item_id={item_id}, user_id={user_id}")
        time.sleep(2)  # 重い処理のシミュレーション
        result = {
            "status": "completed",
            "item_id": item_id,
            "processed_by": user_id,
            "message": "処理が完了しました",
        }
        logger.info(f"✅ 非同期処理完了: {result}")
        return result
    except Exception as exc:
        logger.error(f"❌ 非同期処理エラー: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def send_notification(user_email: str, subject: str, body: str):
    """通知送信タスク（メール等）"""
    logger.info(f"📧 通知送信: {user_email} - {subject}")
    # 実際のメール送信ロジックをここに追加
    return {"sent_to": user_email, "subject": subject}


@celery_app.task
def cleanup_expired_tokens():
    """期限切れトークンのクリーンアップ（定期実行）"""
    logger.info("🧹 期限切れトークンクリーンアップ開始")
    return {"cleaned": True}
