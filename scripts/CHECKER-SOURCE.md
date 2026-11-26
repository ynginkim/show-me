# 검사 키트 출처

meta-harness `6c453008c3cb7a2edea82fea634963d43b7ffe35`의 `skills/check-skillset/scripts/`에서 2026-11-26에 복사했다. CI 설정은 meta-harness `aca7488`(2026-11-26, action을 v7로 올린 커밋)의 `skills/scaffold-skillset/assets/check.yml`이다. 이 사본은 고치지 않았다. 갱신할 때는 정본과 diff를 검토하고 `python3 scripts/selftest.py`로 오류 주입 검사를 다시 실행한다.

```json
{
  "check.py": "24cb1401310b10f29612f55c2cf5d3286e5e708bed7f6cb8659291b7125be280",
  "selftest.py": "d8a9af469ae173ffaa0cac91e55b51562e8a421b92b19dbc64474538a50b7c0f",
  "install_smoke.py": "961f6b13d0e1aeb2ecedd98da88bf2cb4666530c3eee71df5200ea3e28a8440c"
}
```
