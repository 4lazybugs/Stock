import os
import requests
from requests.exceptions import Timeout, RequestException 
import time
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
        11012=반기, 11013=1분기, 11014=3분기, 11011=사업보고서
        """
        y, m, day = d.year, d.month, d.day

        # 1분기 보고서(1~3월 누적)
        if (m >= 1 and m <= 3):  
            return str(y), "11013"
        # 반기 보고서(1~6월 누적)
        if (m >= 4 and m <= 6):
            return str(y), "11012"
        # 3분기 보고서(1~9월 누적)
        if (m >= 7 and m <= 9):
            return str(y), "11014"
        # 사업보고서 (1~12월 누적)
        if (m >= 10 and m <= 12):
            return str(y), "11011" 
            # 당해년도 사업보고서는 익년 3월에 공시되나 busns_year=str(y)이므로 str(y+1) 안해도 됨


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

        last_exc = None
        max_retry = 10
        retry_delay = 0.1

        for attempt in range(1, max_retry + 1):
            try:
                # ⬇ 여기서 3초 동안 응답 없으면 Timeout 발생
                resp = requests.get(url, params=params, timeout=0.1)
                resp.raise_for_status()
                return resp.json()

            except (Timeout, RequestException) as e:
                # ✅ 에러 종류 상관 없이 전부 재시도
                last_exc = e
                print(
                    f"[Retry] attempt {attempt}/{max_retry} "
                    f"(corp={corp_code}, by={by}, rc={rc})"
                )

                if attempt == max_retry:
                    # 마지막 시도까지 실패하면 그대로 예외 올림
                    raise last_exc

                time.sleep(retry_delay)

    # 공통 폴백 + 최신성 선택
    def fetch_with_fallback(self, corp_code: str, date: _date):
        def try_once(by, rc): # by: business year, rc: report code
            data = self._request(corp_code, by, rc)
            val = self.parse(data)
            return val, by, rc

        by0, rc0 = self.map_reprt_by_date(date)   # 날짜→목표 (연도, 보고서코드)
        debug_info = []

        val, by_ok, rc_ok = try_once(by0, rc0)
        
        if val is not None:
            debug_info.append((val, by_ok, rc_ok))
        if val is None:
            print(f"{date} | {self.json_pth} FAIL to find data for {date.year}")
            return val, by_ok, rc_ok, debug_info

        print(f"{date} | {self.json_pth} found {val} (by={by_ok}, rc={rc_ok})")
        return val, by_ok, rc_ok, debug_info