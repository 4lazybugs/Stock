from datetime import date as _date
from .base import BaseMetric
import requests

class NI(BaseMetric):
    json_pth = "fnlttSinglAcntAll"
    label = "NI"

    @staticmethod
    def map_reprt_by_date(d: _date) -> tuple[str, str]:
        # 전년도 연간 고정
        return str(d.year - 1), "11014"

    # ❗ NI 전용: CFS 실패 시 FS도 시도 (연간 성공률↑)
    def _request(self, corp_code: str, by: str, rc: str, sort: str = "date"):
        url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
        base = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bsns_year": by,
            "reprt_code": rc,
            "sort": sort,
        }
        for fs in ("CFS", "FS"):
            params = dict(base, fs_div=fs)
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            if j.get("status") == "000" and j.get("list"):
                return j
        return j  # 마지막 응답 반환

    # ❗ BaseMetric의 폴백 체인을 쓰지 않고, 연간만(필요시 3Q) 시도
    def fetch_with_fallback(self, corp_code: str, date: _date):
        tried = []
        by = str(date.year - 1)

        # 1) 연간
        data = self._request(corp_code, by, "11014")
        tried.append((by, "11014", data.get("status"), len(data.get("list", []))))
        v = self.parse(data)
        if v is not None:
            print(f"{date} | {self.json_pth} best-pick -> {v} (by={by}, rc=11014)")
            return v, by, "11014", tried

        # 2) (옵션) 전년 3Q만 폴백
        data = self._request(corp_code, by, "11013")
        tried.append((by, "11013", data.get("status"), len(data.get("list", []))))
        v = self.parse(data)
        if v is not None:
            print(f"{date} | {self.json_pth} fallback -> {v} (by={by}, rc=11013)")
            return v, by, "11013", tried

        print(f"{date} | {self.json_pth} FAIL (no annual/3Q) tried={tried}")
        return None, by, "11014", tried

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
            "netincome",
            "ifrs-full_profitloss",
            "ifrs-full_profitlossattributabletoownersofparent",
        }
        nm_exact = {
            "당기순이익",
            "지배기업소유주지분순이익",
            "지배주주귀속당기순이익",
            "netincome",
            "profitfortheperiod",
            "profit(loss)",
        }
        nm_contains = {
            "지배주주",
            "지배기업소유주", "소유주지분",
            "ownersofparent",
            "attributabletoownersofparent",
            "연결당기순이익",
        }

        def looks_like_ni(it):
            aid = norm(it.get("account_id"))
            nm  = norm(it.get("account_nm"))
            if aid in id_exact: return True
            if nm in nm_exact:  return True
            if any(k in nm for k in nm_contains): return True
            return False

        # 후보 추출
        cand = [it for it in rows if looks_like_ni(it)]
        if not cand:
            # 디버그: 어떤 라인들이 오는지 보고 싶으면 잠깐 열어두세요
            # print([it.get("account_id"), it.get("account_nm")] for it in rows[:20])
            return None

        # 스코어: CFS>FS, owners-of-parent 가점, id정확/이름정확/포함 순
        def score(it):
            s = 0
            fs_div = (it.get("fs_div") or "").upper()  # CFS/FS
            nm_raw = it.get("account_nm") or ""
            aid = norm(it.get("account_id"))
            nm  = norm(nm_raw)

            if fs_div == "CFS": s += 10
            if "비지배" in nm_raw: s -= 5
            if "지배" in nm_raw: s += 4
            if "ownersofparent" in nm: s += 4

            if aid in id_exact: s += 6
            if nm in nm_exact: s += 4
            elif any(k in nm for k in nm_contains): s += 2

            # CIS(포괄손익) 약간 가점
            if (it.get("sj_div") or "").upper() == "CIS": s += 1
            return s

        best = max(cand, key=score)

        # 기말 우선, 없으면 add
        v = self.to_float(best.get("thstrm_amount"))
        if v is None:
            v = self.to_float(best.get("thstrm_add_amount"))
        return v