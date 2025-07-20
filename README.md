# Archive Backend

`archive-be`는 YouTube 영상을 아카이브하기 위한 FastAPI 기반 백엔드입니다. 이메일 인증을 통한 회원가입과 쿠키 기반 세션 로그인을 제공하며, 영상 다운로드 상태를 웹소켓으로 실시간 전송합니다.

## 주요 기능

- **회원 관리**: 이메일 OTP 인증 후 회원가입, 로그인/로그아웃, 비밀번호 재설정
- **카테고리 관리**: 메인/서브 카테고리를 생성하고 수정·삭제
- **게시글 관리**: YouTube 단일 영상 혹은 플레이리스트를 등록하여 비동기로 다운로드
- **목록 조회**: 사용자별 전체 게시글 또는 카테고리별 게시글 목록 조회
- **실시간 상태 알림**: 다운로드 진행 상황을 `/ws` 웹소켓 엔드포인트로 전달

## 실행 방법

### 환경 변수

다음 값을 `.env` 파일에 설정해야 합니다.

```
POSTGRESQL_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
SMTP_USER=example@gmail.com
SMTP_PASSWORD=your_smtp_password
EMAIL_FROM=example@gmail.com
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
SESSION_EXPIRE_SECONDS=3600
BE_URL=http://localhost:2456
```

### Docker로 실행

1. `docker compose up --build` 명령으로 FastAPI 앱과 Redis를 실행합니다.
2. 서버는 기본적으로 `2456` 포트에서 동작하며 `/videos` 경로로 다운로드된 영상을 제공합니다.

### 로컬 개발

Poetry가 설치되어 있다면 다음 명령으로 의존성을 설치하고 서버를 실행할 수 있습니다.

```bash
poetry install
uvicorn app.main:app --reload --port 2456
```

## 프로젝트 구조

- `app/main.py` – FastAPI 애플리케이션 진입점
- `app/router/` – 회원, 로그인, 카테고리, 게시글 관련 API 라우터
- `app/services/` – 비즈니스 로직 및 웹소켓 관리
- `app/db/` – SQLAlchemy 연결 및 쿼리 정의
- `app/core/` – 설정 및 세션, Redis 관리 코드
- `docker-compose.yaml` – 개발용 Docker 설정 (FastAPI + Redis)
- `.github/workflows/deploy.yml` – 원격 서버로 배포하는 GitHub Actions 예시

## 추가 정보

동영상 다운로드는 [yt-dlp](https://github.com/yt-dlp/yt-dlp)를 이용해 비동기로 진행되며, 작업 결과는 Redis 세션을 통해 인증된 사용자에게 웹소켓으로 전송됩니다. 파일은 컨테이너 내부 `/app/video_storage` 디렉터리에 저장되며, `/videos` 경로로 정적 제공됩니다.
