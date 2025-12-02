from .base import BaseMetric

class AST(BaseMetric):
    json_pth = "fnlttSinglAcntAll"
    label = "AST"   # Total Assets

    def parse(self, data: dict):
        if not data or data.get("status") != "000":
            return None

        rows = (data.get("list") or [])
        # 재무상태표(BS)에서만 필터링
        rows = [it for it in rows if it.get("sj_div") == "BS"]

        # 정확 매칭: account_id
        id_exact = {
            "totalassets",
            "assets",
            "assetstotal",
        }

        # 정확 매칭: account_nm
        nm_exact = {
            "자산총계",
            "총자산",
            "total assets",
            "assets",
        }

        def norm(s: str) -> str:
            return (s or "").strip().replace(" ", "").lower()

        def looks_like_assets(it):
            aid = norm(it.get("account_id"))
            nm  = norm(it.get("account_nm"))
            if aid in id_exact:
                return True
            if nm in nm_exact:
                return True
            return False

        # 기말값(thstrm_amount) 우선, 없으면 thstrm_add_amount
        for it in rows:
            if not looks_like_assets(it):
                continue
            v = self.to_float(it.get("thstrm_amount"))
            if v is None:
                v = self.to_float(it.get("thstrm_add_amount"))
            if v is not None:
                return v

        return None
