import os
import requests
from datetime import date as _date

# -----------------------
# BaseMetric (DART 호출/폴백 내장)
# -----------------------
class BaseMetric:
    json_pth: str = ""          # ex) "fnlttSinglAcntAll", "stockTotqySttus"
    label: str = "VAL"          # 출력 컬럼명
    prefer_latest: bool = True  # 최신 보고서 우선(11014 > 11013 > 11012 > 11011)

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("DART_API_KEY", "REPLACE_WITH_REAL_KEY")
        assert self.json_pth, "Subclass must set json_pth"
        assert self.label, "Subclass must set label"

    # ✅ 공통 팩토리(클래스 메서드)
    @classmethod
    def create(cls, metric_cls: type["BaseMetric"], *args, **kwargs) -> "BaseMetric":
        if not issubclass(metric_cls, BaseMetric):
            raise TypeError(f"{metric_cls.__name__} is not a subclass of BaseMetric")
        return metric_cls(*args, **kwargs)

    # 🔹 숫자 파싱 유틸(정적 메서드로 내장)
    @staticmethod
    def to_float(s):
        if s in (None, "", "-"):
            return None
        s = str(s).replace(",", "").strip()
        if s.startswith("(") and s.endswith(")"):
            s = "-" + s[1:-1]
        try:
            return float(s)
        except Exception:
            return None

    # 🔹 날짜 → (사업연도, 보고서코드) 매핑(정적 메서드로 내장)
    @staticmethod
    def map_reprt_by_date(d: _date) -> tuple[str, str]:
        """
        날짜 → (사업연도, 보고서코드) 매핑, DART 정기공시 제출기한 기준(결산 12/31 가정)
        11011=1분기, 11012=반기, 11013=3분기, 11014=사업보고서
        """
        y, m, day = d.year, d.month, d.day

        # 1/1 ~ 3/31: 전년도 연간 사업보고서(1~12월 누적)
        if (m < 4) or (m == 4 and day == 0):  
            return str(y - 1), "11014"
        # 4/1 ~ 5/15: 전년도 연간 사업보고서(1~12월 누적)
        if (m == 4) or (m == 5 and day <= 15):
            return str(y - 1), "11014"
        # 5/16 ~ 8/14: 당해년도 1분기 보고서(1~3월 누적)
        if (m == 5 and day >= 16) or (m in (6, 7)) or (m == 8 and day <= 14):
            return str(y), "11011"
        # 8/15 ~ 11/14: 당해년도 반기 보고서(1~6월 누적)
        if (m == 8 and day >= 15) or (m in (9, 10)) or (m == 11 and day <= 14):
            return str(y), "11012"
        # 11/15 ~ 12/31: 당해년도 3분기보고서(1~9월 누적)
        return str(y), "11013"

    # 서브클래스가 구현
    def parse(self, data: dict):
        raise NotImplementedError

    # 공통 요청
    def _request(self, corp_code: str, by: str, rc: str, sort: str = "date"):
        url = f"https://opendart.fss.or.kr/api/{self.json_pth}.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bsns_year": by,
            "reprt_code": rc,
            "sort": sort,
        }
        if "fnlttSinglAcntAll" in self.json_pth:
            params.setdefault("fs_div", "CFS")
        resp = requests.get(url, params=params, timeout=300)
        resp.raise_for_status()
        return resp.json()

    # 공통 폴백 + 최신성 선택
    def fetch_with_fallback(self, corp_code: str, date: _date):
        def try_once(by, rc):
            data = self._request(corp_code, by, rc)
            val = self.parse(data)
            return val, by, rc

        by0, rc0 = self.map_reprt_by_date(date)   # 날짜→목표 (연도, 보고서코드)
        tried = []
        candidates = []

        # 0) 목표 정확 조합 먼저
        val, by_ok, rc_ok = try_once(by0, rc0)
        tried.append((by_ok, rc_ok))
        if val is not None:
            candidates.append((val, by_ok, rc_ok))

        # 코드 위상(1Q<2Q<3Q<사업보고서)
        rc_rank = {"11011": 1, "11012": 2, "11013": 3, "11014": 4}
        tgt_rank = rc_rank[rc0]

        # 1) 같은 해에서 '목표 코드보다 늦지 않은' 코드만 시도 (= rc_rank <= tgt_rank)
        same_year_order = ["11013", "11012", "11011"]  # 뒤에서 필터로 컷
        for rc in same_year_order:
            if rc == rc0:
                continue
            if rc_rank[rc] > tgt_rank:   # 목표보다 '더 늦은' 분기는 금지
                continue
            val, by_ok, rc_ok = try_once(by0, rc)
            tried.append((by_ok, rc_ok))
            if val is not None:
                candidates.append((val, by_ok, rc_ok))

        # 2) 전년 사업보고서(11014)만 허용
        val, by_ok, rc_ok = try_once(str(date.year - 1), "11014")
        tried.append((by_ok, rc_ok))
        if val is not None:
            candidates.append((val, by_ok, rc_ok))

        if not candidates:
            print(f"{date} | {self.json_pth} FAIL (no value) tried={tried}")
            return None, by0, rc0, tried

        # 3) 최종 선택: '목표 시점'을 넘지 않는 후보만 남기고 그 중 가장 최근
        def not_later_than_target(by, rc):
            by = int(by); by0_i = int(by0)
            if by < by0_i:
                return True
            if by > by0_i:
                return False
            return rc_rank[rc] <= tgt_rank

        allowed = [(v, by, rc) for (v, by, rc) in candidates if not_later_than_target(by, rc)]
        if not allowed:
            print(f"{date} | {self.json_pth} FAIL (only later reports found) tried={tried}")
            return None, by0, rc0, tried

        best = max(allowed, key=lambda x: (int(x[1]), rc_rank[x[2]]))
        val, by_ok, rc_ok = best
        print(f"{date} | {self.json_pth} best-pick -> {val} (by={by_ok}, rc={rc_ok})")
        return val, by_ok, rc_ok, tried