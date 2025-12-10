from .base import BaseMetric

class SHS(BaseMetric):
    json_pth = "stockTotqySttus"
    label = "SHS"

    def parse(self, data: dict):
        if not data or data.get("status") != "000":
            return None
        for it in (data.get("list") or []):
            se = (it.get("se") or "").strip()
            if any(k in se for k in ["보통주", "보통주식", "의결권 있는 주식"]):
                val = it.get("istc_totqy")
                try:
                    return int(str(val).replace(",", "").strip()) if val else None
                except Exception:
                    return None
        return None