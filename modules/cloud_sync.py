"""
Cloud Sync Module - Supabase Integration
Sinkronisasi data portfolio & journal ke cloud
Memungkinkan akses dari device manapun
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


class CloudSync:
    """Cloud synchronization dengan Supabase"""
    
    def __init__(
        self,
        supabase_url: str = "",
        supabase_key: str = "",
        client: Any = None,
    ):
        """
        Initialize Supabase connection
        
        Args:
            supabase_url: URL Supabase project
            supabase_key: API Key Supabase
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = None
        self.is_connected = False

        # Allow injecting an already-authenticated Supabase client (recommended)
        if client is not None:
            self.client = client
            self.is_connected = True
            return
        
        # Try to initialize Supabase client
        if supabase_url and supabase_key:
            self._init_supabase()
    
    def _init_supabase(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client
            self.client = create_client(self.supabase_url, self.supabase_key)
            self.is_connected = True
            print("✅ Supabase connected")
        except ImportError:
            print("⚠️ supabase package not installed. Install with: pip install supabase")
            self.is_connected = False
        except Exception as e:
            print(f"❌ Failed to connect Supabase: {e}")
            self.is_connected = False
    
    def sync_portfolio(self, user_id: int, portfolio_data: List[Dict]) -> bool:
        """Sync portfolio data to cloud"""
        if not self.is_connected:
            print("⚠️ Cloud sync not connected")
            return False
        
        try:
            # Prepare data
            for item in portfolio_data:
                item['user_id'] = user_id
                item['synced_at'] = datetime.now().isoformat()
            
            # Upsert to Supabase
            self.client.table('portfolio').upsert(portfolio_data).execute()
            
            print(f"✅ Synced {len(portfolio_data)} portfolio items to cloud")
            return True
        except Exception as e:
            print(f"❌ Sync portfolio error: {e}")
            return False
    
    def sync_journal(self, user_id: int, journal_data: List[Dict]) -> bool:
        """Sync journal entries to cloud"""
        if not self.is_connected:
            print("⚠️ Cloud sync not connected")
            return False
        
        try:
            # Prepare data
            for item in journal_data:
                item['user_id'] = user_id
                item['synced_at'] = datetime.now().isoformat()
            
            # Upsert to Supabase
            self.client.table('journal').upsert(journal_data).execute()
            
            print(f"✅ Synced {len(journal_data)} journal entries to cloud")
            return True
        except Exception as e:
            print(f"❌ Sync journal error: {e}")
            return False
    
    def get_portfolio_from_cloud(self, user_id: int) -> Optional[List[Dict]]:
        """Fetch portfolio data from cloud"""
        if not self.is_connected:
            print("⚠️ Cloud sync not connected")
            return None
        
        try:
            response = self.client.table('portfolio').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"❌ Failed to fetch portfolio from cloud: {e}")
            return None
    
    def get_journal_from_cloud(self, user_id: int, limit: int = 1000) -> Optional[List[Dict]]:
        """Fetch journal data from cloud"""
        if not self.is_connected:
            print("⚠️ Cloud sync not connected")
            return None
        
        try:
            response = (
                self.client.table('journal')
                .select('*')
                .eq('user_id', user_id)
                .order('date', desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"❌ Failed to fetch journal from cloud: {e}")
            return None
    
    def delete_cloud_data(self, user_id: int) -> bool:
        """Delete user data from cloud (account deletion)"""
        if not self.is_connected:
            return False
        
        try:
            # Delete portfolio
            self.client.table('portfolio').delete().eq('user_id', user_id).execute()
            # Delete journal
            self.client.table('journal').delete().eq('user_id', user_id).execute()
            
            print(f"✅ Deleted cloud data for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting cloud data: {e}")
            return False

    # ===== Blob-based sync (recommended for local-only apps) =====
    def save_user_blob(self, user_id: str, payload: Dict) -> bool:
        """Save all user data as a single JSON blob to `user_data` table.

        Table expected: user_data(user_id uuid primary key, data jsonb, updated_at timestamptz)
        """
        if not self.is_connected:
            print("⚠️ Cloud sync not connected")
            return False

        try:
            row = {
                "user_id": user_id,
                "data": payload,
                "updated_at": datetime.now().isoformat(),
            }
            # Upsert by primary key user_id
            self.client.table("user_data").upsert([row]).execute()
            return True
        except Exception as e:
            print(f"❌ Save user blob error: {e}")
            return False

    def load_user_blob(self, user_id: str) -> Optional[Dict]:
        """Load user data blob from `user_data` table."""
        if not self.is_connected:
            print("⚠️ Cloud sync not connected")
            return None

        try:
            resp = (
                self.client.table("user_data")
                .select("data,updated_at")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            rows = getattr(resp, "data", None)
            if not rows:
                return None
            if isinstance(rows, list):
                return rows[0]
            if isinstance(rows, dict):
                return rows
            return None
        except Exception as e:
            print(f"❌ Load user blob error: {e}")
            return None


class LocalSync:
    """Local file-based sync sebagai fallback"""
    
    def __init__(self, sync_dir: str = 'data/sync'):
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(parents=True, exist_ok=True)
    
    def save_sync_checkpoint(self, user_id: int, data: Dict) -> bool:
        """Save sync checkpoint locally"""
        try:
            checkpoint_file = self.sync_dir / f"sync_checkpoint_{user_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump({
                    'user_id': user_id,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"❌ Error saving sync checkpoint: {e}")
            return False
    
    def load_sync_checkpoint(self, user_id: int) -> Optional[Dict]:
        """Load sync checkpoint"""
        try:
            checkpoint_file = self.sync_dir / f"sync_checkpoint_{user_id}.json"
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"❌ Error loading sync checkpoint: {e}")
            return None


class SyncManager:
    """Manages sync between local and cloud storage"""
    
    def __init__(self, cloud_sync: Optional[CloudSync] = None):
        self.cloud = cloud_sync
        self.local = LocalSync()
        self.last_sync = None
    
    def full_sync(self, user_id: int, portfolio_data: List[Dict], journal_data: List[Dict]) -> bool:
        """Perform full sync of all user data"""
        success = True
        
        # Try cloud sync first
        if self.cloud and self.cloud.is_connected:
            success &= self.cloud.sync_portfolio(user_id, portfolio_data)
            success &= self.cloud.sync_journal(user_id, journal_data)
        
        # Always save local checkpoint
        checkpoint = {
            'portfolio': portfolio_data,
            'journal': journal_data
        }
        success &= self.local.save_sync_checkpoint(user_id, checkpoint)
        
        if success:
            self.last_sync = datetime.now()
            print(f"✅ Sync completed at {self.last_sync}")
        
        return success
    
    def restore_from_cloud(self, user_id: int) -> Optional[Dict]:
        """Restore data from cloud for new device"""
        if not self.cloud or not self.cloud.is_connected:
            print("⚠️ Cloud sync not available. Using local data if exists.")
            return None
        
        try:
            portfolio = self.cloud.get_portfolio_from_cloud(user_id)
            journal = self.cloud.get_journal_from_cloud(user_id)
            
            if portfolio is not None or journal is not None:
                print("✅ Data restored from cloud")
                return {
                    'portfolio': portfolio or [],
                    'journal': journal or []
                }
        except Exception as e:
            print(f"❌ Error restoring from cloud: {e}")
        
        return None
