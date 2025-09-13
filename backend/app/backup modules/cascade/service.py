import json
from app.db.supabase_client import supabase
from app.modules.cascade import schemas
from postgrest.exceptions import APIError

class CascadeService:
    def __init__(self):
        self.table = "module_cascade"

    def get_settings(self) -> schemas.CascadeSettings:
        try:
            res = (
                supabase.table(self.table)
                .select("*")
                .eq("setting_name", "ajax_scroll_auto")
                .maybe_single()
                .execute()
            )
        except APIError:
            # Default if network/API error occurs
            return schemas.CascadeSettings(ajax_scroll_auto=True)

        if res and res.data:
            # Parse JSON string safely
            setting_value = res.data.get('setting_value')
            if isinstance(setting_value, str):
                setting_value = json.loads(setting_value)
            return schemas.CascadeSettings(ajax_scroll_auto=setting_value.get('enabled', True))

        # Default if no row exists
        return schemas.CascadeSettings(ajax_scroll_auto=True)

    def update_settings(self, settings: schemas.CascadeSettings) -> schemas.CascadeSettings:
        # Upsert the 'ajax_scroll_auto' setting in the database
        data = {
            "key": "ajax_scroll_auto",
            "setting_name": "ajax_scroll_auto",
            "setting_value": {"enabled": settings.ajax_scroll_auto}
        }
        res = (
            supabase.table(self.table)
            .upsert(data, on_conflict="setting_name")
            .execute()
        )

        # Supabase may return string, so parse it safely
        setting_value = res.data[0].get('setting_value')
        if isinstance(setting_value, str):
            setting_value = json.loads(setting_value)

        return schemas.CascadeSettings(ajax_scroll_auto=setting_value.get('enabled', True))
