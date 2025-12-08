from .base import BaseMetric

class SHS(BaseMetric):
    json_pth = "stockTotqySttus"
    label = "SHS"

    def parse(self, data: dict):
        if not data or data.get("status") != "000":
            return None
        for it in (data.get("list") or []):
            se = (it.get("se") or "").strip()
            if ("보통주" in se) or ("보통주식" in se):
                val = it.get("istc_totqy")
                try:
                    return int(str(val).replace(",", "").strip()) if val else None
                except Exception:
                    return None
        return None