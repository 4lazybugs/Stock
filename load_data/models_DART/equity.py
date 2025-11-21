from .base import BaseMetric

class EQU(BaseMetric):
    json_pth = "fnlttSinglAcntAll"
    label = "EQU"

    def parse(self, data: dict):
        if not data or data.get("status") != "000":
            return None

        rows = (data.get("list") or [])
        # ✅ 재무상태표만 (자본총계는 BS 항목)
        rows = [it for it in rows if (it.get("sj_div") == "BS")]

        # ✅ 정확 매칭 세트 (정규화 후 비교)
        id_exact = {
            "totalequity",
            "equity",
        }
        nm_exact = {
            "자본총계",
            "지배기업소유주지분",
            "total equity",
            "equity attributable to owners of parent",
            "equity",
        }

        def norm(s: str) -> str:
            return (s or "").strip().replace(" ", "").lower()

        def looks_like_equity(it):
            aid = norm(it.get("account_id"))
            nm  = norm(it.get("account_nm"))
            if aid in id_exact: return True
            if nm in nm_exact:  return True
            return False

        # ✅ 기말값 우선(thstrm_amount), 없으면 보조값(thstrm_add_amount)
        for it in rows:
            if not looks_like_equity(it):
                continue
            v = self.to_float(it.get("thstrm_amount"))
            if v is None:
                v = self.to_float(it.get("thstrm_add_amount"))
            if v is not None:
                return v

        return None
