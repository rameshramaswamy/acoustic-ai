import boto3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("DR-Manager")
logging.basicConfig(level=logging.INFO)

class DRManager:
    def __init__(self, region="us-east-1"):
        self.rds = boto3.client('rds', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)

    def trigger_db_snapshot(self, db_instance_id):
        """Manually triggers a snapshot before major updates."""
        snapshot_id = f"manual-dr-{db_instance_id}-{datetime.now().strftime('%Y%m%d-%H%M')}"
        try:
            self.rds.create_db_snapshot(
                DBSnapshotIdentifier=snapshot_id,
                DBInstanceIdentifier=db_instance_id
            )
            logger.info(f"📸 Snapshot started: {snapshot_id}")
            return snapshot_id
        except Exception as e:
            logger.error(f"❌ Snapshot failed: {e}")
            return None

    def verify_s3_versioning(self, bucket_name):
        """Ensures Raw Audio bucket has versioning enabled (Anti-Ransomware)."""
        try:
            response = self.s3.get_bucket_versioning(Bucket=bucket_name)
            status = response.get('Status')
            
            if status == 'Enabled':
                logger.info(f"✅ Bucket {bucket_name} is DR-Ready (Versioning Enabled)")
                return True
            else:
                logger.warning(f"⚠️ Bucket {bucket_name} NOT Protected! Status: {status}")
                return False
        except Exception as e:
            logger.error(f"❌ Check failed: {e}")
            return False

if __name__ == "__main__":
    dr = DRManager()
    # Replace with real IDs from Phase 1
    dr.verify_s3_versioning("sound-dd-raw-production") 
    # dr.trigger_db_snapshot("sound-dd-postgres")