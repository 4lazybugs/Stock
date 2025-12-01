from datetime import date as _date
from .base import BaseMetric
import requests

class NI(BaseMetric):
    json_pth = "fnlttSinglAcntAll"
    label = "NI"

    def parse(self, data: dict):
        if not data or data.get("status") != "000":
            return None

        rows = (data.get("list") or [])
        # IS/CIS만 사용
        rows = [it for it in rows if (it.get("sj_div") in ("IS", "CIS"))]

        def norm(s: str) -> str:
            return "".join((s or "").split()).lower()

        # 매칭 키워드
        id_exact = {
            "ifrs-full_ProfitLossAttributableToOwnersOfParent",
            "ifrs_ProfitLossAttributableToOwnersOfParent",
        }
        nm_exact = {
            "지배기업 소유주지분",
            "지배기업소유주지분",
            "지배기업의 소유주에게 귀속되는 당기순이익(손실)"
        }

        id_exact = {norm(s) for s in id_exact}
        nm_exact = {norm(s) for s in nm_exact}
        best = None

        for it in rows:
            aid = norm(it.get("account_id"))
            nm  = norm(it.get("account_nm"))

            if (aid in id_exact and nm in nm_exact):
                best = it
                break  # 더 볼 필요 없이 확정

            else: 
                best = None

        # 지배기업소유주지분 즉, 당기순이익 return
        v = self.to_float(best.get("thstrm_amount"))
        return v