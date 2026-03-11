from typing import Literal, TypedDict


class TopicSeed(TypedDict):
    category: str
    subcategory: str
    title: str
    difficulty: Literal["beginner", "intermediate", "advanced"]


CURRICULUM: list[TopicSeed] = [
    # ── OS: 프로세스 ──
    {"category": "os", "subcategory": "process", "title": "프로세스 vs 스레드", "difficulty": "beginner"},
    {"category": "os", "subcategory": "process", "title": "Context Switching이 비싼 이유", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "process", "title": "프로세스 간 통신(IPC) 방식 비교", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "process", "title": "fork()와 exec()의 역할 분리", "difficulty": "intermediate"},

    # ── OS: 메모리 ──
    {"category": "os", "subcategory": "memory", "title": "가상 메모리와 페이지 폴트", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "memory", "title": "페이지 교체 알고리즘 비교 (LRU, FIFO, Clock)", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "memory", "title": "메모리 단편화와 해결 전략", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "memory", "title": "스택 메모리 vs 힙 메모리", "difficulty": "beginner"},

    # ── OS: 동시성 ──
    {"category": "os", "subcategory": "concurrency", "title": "데드락 조건 4가지와 회피 전략", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "concurrency", "title": "세마포어 vs 뮤텍스", "difficulty": "intermediate"},
    {"category": "os", "subcategory": "concurrency", "title": "Race Condition과 임계 영역", "difficulty": "beginner"},
    {"category": "os", "subcategory": "concurrency", "title": "CPU 스케줄링 알고리즘 비교", "difficulty": "intermediate"},

    # ── OS: 파일시스템/IO ──
    {"category": "os", "subcategory": "io", "title": "파일 디스크립터와 I/O 모델 (Blocking, Non-blocking, Multiplexing)", "difficulty": "advanced"},
    {"category": "os", "subcategory": "io", "title": "epoll/kqueue가 select보다 빠른 이유", "difficulty": "advanced"},

    # ── 네트워크: TCP/UDP ──
    {"category": "network", "subcategory": "transport", "title": "TCP 3-way handshake가 필요한 이유", "difficulty": "beginner"},
    {"category": "network", "subcategory": "transport", "title": "TCP vs UDP 실무 선택 기준", "difficulty": "beginner"},
    {"category": "network", "subcategory": "transport", "title": "TCP 흐름 제어와 혼잡 제어", "difficulty": "intermediate"},
    {"category": "network", "subcategory": "transport", "title": "TCP TIME_WAIT 상태가 존재하는 이유", "difficulty": "intermediate"},

    # ── 네트워크: HTTP ──
    {"category": "network", "subcategory": "http", "title": "HTTP/1.1 Keep-Alive와 Head-of-Line Blocking", "difficulty": "intermediate"},
    {"category": "network", "subcategory": "http", "title": "HTTP/2 멀티플렉싱이 해결한 문제", "difficulty": "intermediate"},
    {"category": "network", "subcategory": "http", "title": "HTTPS/TLS 핸드셰이크 과정", "difficulty": "intermediate"},
    {"category": "network", "subcategory": "http", "title": "REST API 설계에서 자주 하는 실수", "difficulty": "beginner"},

    # ── 네트워크: 인프라 ──
    {"category": "network", "subcategory": "infra", "title": "DNS 재귀 질의 vs 반복 질의", "difficulty": "beginner"},
    {"category": "network", "subcategory": "infra", "title": "로드밸런서 L4 vs L7", "difficulty": "intermediate"},
    {"category": "network", "subcategory": "infra", "title": "CDN이 동작하는 원리", "difficulty": "beginner"},
    {"category": "network", "subcategory": "infra", "title": "Reverse Proxy vs Forward Proxy", "difficulty": "beginner"},

    # ── 데이터베이스: 인덱스 ──
    {"category": "database", "subcategory": "index", "title": "인덱스가 B+Tree인 이유", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "index", "title": "커버링 인덱스와 인덱스 컨디션 푸시다운", "difficulty": "advanced"},
    {"category": "database", "subcategory": "index", "title": "복합 인덱스 컬럼 순서가 중요한 이유", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "index", "title": "Hash 인덱스 vs B+Tree 인덱스", "difficulty": "intermediate"},

    # ── 데이터베이스: 트랜잭션 ──
    {"category": "database", "subcategory": "transaction", "title": "트랜잭션 격리 수준 4단계", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "transaction", "title": "MVCC 동작 원리", "difficulty": "advanced"},
    {"category": "database", "subcategory": "transaction", "title": "Phantom Read가 발생하는 조건", "difficulty": "advanced"},
    {"category": "database", "subcategory": "transaction", "title": "낙관적 잠금 vs 비관적 잠금", "difficulty": "intermediate"},

    # ── 데이터베이스: 설계/운영 ──
    {"category": "database", "subcategory": "design", "title": "정규화 vs 반정규화 트레이드오프", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "design", "title": "Connection Pool이 필요한 이유", "difficulty": "beginner"},
    {"category": "database", "subcategory": "design", "title": "Replication vs Sharding", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "design", "title": "Slow Query 분석과 실행 계획 읽는 법", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "design", "title": "N+1 문제와 해결 전략", "difficulty": "beginner"},

    # ── 데이터베이스: NoSQL ──
    {"category": "database", "subcategory": "nosql", "title": "NoSQL 유형 비교: Document, Key-Value, Column, Graph", "difficulty": "beginner"},
    {"category": "database", "subcategory": "nosql", "title": "MongoDB의 도큐먼트 모델과 임베딩 vs 레퍼런싱", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "nosql", "title": "Redis 자료구조별 활용 사례", "difficulty": "intermediate"},

    # ── 데이터베이스: 고급 ──
    {"category": "database", "subcategory": "advanced", "title": "WAL(Write-Ahead Logging) 동작 원리", "difficulty": "advanced"},
    {"category": "database", "subcategory": "advanced", "title": "데이터베이스 파티셔닝 전략 (Range, Hash, List)", "difficulty": "intermediate"},
    {"category": "database", "subcategory": "advanced", "title": "Vacuum과 Dead Tuple 관리 (PostgreSQL)", "difficulty": "advanced"},

    # ── 시스템 설계: 기초 ──
    {"category": "system_design", "subcategory": "fundamentals", "title": "CAP 정리와 실무 선택", "difficulty": "intermediate"},
    {"category": "system_design", "subcategory": "fundamentals", "title": "수평 확장 vs 수직 확장", "difficulty": "beginner"},
    {"category": "system_design", "subcategory": "fundamentals", "title": "일관성 해싱(Consistent Hashing)", "difficulty": "advanced"},

    # ── 시스템 설계: 패턴 ──
    {"category": "system_design", "subcategory": "patterns", "title": "Rate Limiting 구현 전략", "difficulty": "intermediate"},
    {"category": "system_design", "subcategory": "patterns", "title": "서킷브레이커 패턴", "difficulty": "intermediate"},
    {"category": "system_design", "subcategory": "patterns", "title": "이벤트 소싱 패턴", "difficulty": "advanced"},
    {"category": "system_design", "subcategory": "patterns", "title": "CQRS는 언제 쓰는가", "difficulty": "advanced"},
    {"category": "system_design", "subcategory": "patterns", "title": "Saga 패턴으로 분산 트랜잭션 처리", "difficulty": "advanced"},
    {"category": "system_design", "subcategory": "patterns", "title": "Bulkhead 패턴과 장애 격리", "difficulty": "intermediate"},

    # ── 시스템 설계: 메시징 ──
    {"category": "system_design", "subcategory": "messaging", "title": "메시지 큐 At-Least-Once vs Exactly-Once", "difficulty": "intermediate"},
    {"category": "system_design", "subcategory": "messaging", "title": "Kafka 파티션과 컨슈머 그룹", "difficulty": "intermediate"},
    {"category": "system_design", "subcategory": "messaging", "title": "Pub/Sub vs Message Queue 차이", "difficulty": "beginner"},

    # ── 시스템 설계: 캐시 ──
    {"category": "system_design", "subcategory": "cache", "title": "캐시 전략: Cache-Aside, Write-Through, Write-Behind", "difficulty": "intermediate"},
    {"category": "system_design", "subcategory": "cache", "title": "캐시 Stampede 문제와 해결법", "difficulty": "advanced"},
    {"category": "system_design", "subcategory": "cache", "title": "Redis가 싱글 스레드인데 빠른 이유", "difficulty": "intermediate"},

    # ── DDD: 전략적 설계 ──
    {"category": "ddd", "subcategory": "strategic", "title": "Bounded Context 나누는 기준", "difficulty": "intermediate"},
    {"category": "ddd", "subcategory": "strategic", "title": "도메인 이벤트 vs 통합 이벤트", "difficulty": "advanced"},
    {"category": "ddd", "subcategory": "strategic", "title": "Anti-Corruption Layer", "difficulty": "advanced"},
    {"category": "ddd", "subcategory": "strategic", "title": "Context Map과 팀 간 협업 패턴", "difficulty": "advanced"},

    # ── DDD: 전술적 설계 ──
    {"category": "ddd", "subcategory": "tactical", "title": "Aggregate 설계 규칙", "difficulty": "intermediate"},
    {"category": "ddd", "subcategory": "tactical", "title": "Value Object를 써야 하는 이유", "difficulty": "beginner"},
    {"category": "ddd", "subcategory": "tactical", "title": "도메인 서비스 vs 애플리케이션 서비스", "difficulty": "intermediate"},
    {"category": "ddd", "subcategory": "tactical", "title": "Repository 패턴의 진짜 의미", "difficulty": "intermediate"},

    # ── DDD: 아키텍처 ──
    {"category": "ddd", "subcategory": "architecture", "title": "헥사고날 아키텍처 실무 적용", "difficulty": "intermediate"},
    {"category": "ddd", "subcategory": "architecture", "title": "클린 아키텍처의 의존성 규칙", "difficulty": "intermediate"},
    {"category": "ddd", "subcategory": "architecture", "title": "레이어드 아키텍처의 한계", "difficulty": "beginner"},

    # ── 자료구조: 기초 ──
    {"category": "data_structure", "subcategory": "basics", "title": "배열 vs 연결 리스트 실무 선택 기준", "difficulty": "beginner"},
    {"category": "data_structure", "subcategory": "basics", "title": "해시 테이블 충돌 해결: Chaining vs Open Addressing", "difficulty": "intermediate"},
    {"category": "data_structure", "subcategory": "basics", "title": "힙(Heap)과 우선순위 큐", "difficulty": "intermediate"},
    {"category": "data_structure", "subcategory": "basics", "title": "트라이(Trie) 자료구조와 활용", "difficulty": "intermediate"},

    # ── 자료구조: 알고리즘 ──
    {"category": "data_structure", "subcategory": "algorithm", "title": "시간 복잡도 O(n log n)이 의미하는 것", "difficulty": "beginner"},
    {"category": "data_structure", "subcategory": "algorithm", "title": "그래프 탐색: BFS vs DFS 선택 기준", "difficulty": "beginner"},
    {"category": "data_structure", "subcategory": "algorithm", "title": "동적 프로그래밍의 핵심: 부분 문제 겹침", "difficulty": "intermediate"},
    {"category": "data_structure", "subcategory": "algorithm", "title": "정렬 알고리즘별 특성과 실무 선택", "difficulty": "beginner"},

    # ── 보안: 웹 ──
    {"category": "security", "subcategory": "web", "title": "XSS 공격 유형과 방어 전략", "difficulty": "beginner"},
    {"category": "security", "subcategory": "web", "title": "CSRF 공격 원리와 토큰 기반 방어", "difficulty": "beginner"},
    {"category": "security", "subcategory": "web", "title": "SQL Injection과 Prepared Statement", "difficulty": "beginner"},
    {"category": "security", "subcategory": "web", "title": "CORS가 존재하는 이유와 동작 원리", "difficulty": "beginner"},
    {"category": "security", "subcategory": "web", "title": "Content Security Policy(CSP)와 보안 헤더", "difficulty": "intermediate"},

    # ── 보안: 인증 ──
    {"category": "security", "subcategory": "auth", "title": "세션 기반 인증 vs 토큰 기반 인증", "difficulty": "beginner"},
    {"category": "security", "subcategory": "auth", "title": "JWT 구조와 보안 취약점", "difficulty": "intermediate"},
    {"category": "security", "subcategory": "auth", "title": "OAuth 2.0 Authorization Code Flow", "difficulty": "intermediate"},
    {"category": "security", "subcategory": "auth", "title": "bcrypt와 비밀번호 해싱 전략", "difficulty": "intermediate"},

    # ── 보안: 암호화 ──
    {"category": "security", "subcategory": "crypto", "title": "대칭키 vs 비대칭키 암호화", "difficulty": "beginner"},
    {"category": "security", "subcategory": "crypto", "title": "해시 함수의 특성과 활용 (SHA, HMAC)", "difficulty": "intermediate"},

    # ── 소프트웨어 공학: 원칙 ──
    {"category": "sw_engineering", "subcategory": "principle", "title": "SOLID 원칙 실무 적용", "difficulty": "intermediate"},
    {"category": "sw_engineering", "subcategory": "principle", "title": "결합도와 응집도", "difficulty": "beginner"},
    {"category": "sw_engineering", "subcategory": "principle", "title": "DRY vs WET vs AHA 원칙", "difficulty": "beginner"},

    # ── 소프트웨어 공학: 패턴 ──
    {"category": "sw_engineering", "subcategory": "pattern", "title": "디자인 패턴: Strategy와 Template Method", "difficulty": "intermediate"},
    {"category": "sw_engineering", "subcategory": "pattern", "title": "디자인 패턴: Observer와 이벤트 시스템", "difficulty": "intermediate"},
    {"category": "sw_engineering", "subcategory": "pattern", "title": "디자인 패턴: Factory와 의존성 역전", "difficulty": "intermediate"},
    {"category": "sw_engineering", "subcategory": "pattern", "title": "디자인 패턴: Decorator와 Proxy", "difficulty": "intermediate"},

    # ── 소프트웨어 공학: 테스트 ──
    {"category": "sw_engineering", "subcategory": "testing", "title": "단위 테스트 vs 통합 테스트 vs E2E 테스트", "difficulty": "beginner"},
    {"category": "sw_engineering", "subcategory": "testing", "title": "테스트 더블: Mock, Stub, Spy의 차이", "difficulty": "intermediate"},
    {"category": "sw_engineering", "subcategory": "testing", "title": "TDD의 Red-Green-Refactor 사이클", "difficulty": "intermediate"},

    # ── 소프트웨어 공학: DevOps ──
    {"category": "sw_engineering", "subcategory": "devops", "title": "CI/CD 파이프라인 설계", "difficulty": "beginner"},
    {"category": "sw_engineering", "subcategory": "devops", "title": "Blue-Green vs Canary vs Rolling 배포", "difficulty": "intermediate"},
    {"category": "sw_engineering", "subcategory": "devops", "title": "컨테이너와 Docker의 동작 원리", "difficulty": "beginner"},
    {"category": "sw_engineering", "subcategory": "devops", "title": "쿠버네티스 Pod, Service, Ingress 기초", "difficulty": "intermediate"},

    # ── 웹: 브라우저 ──
    {"category": "web", "subcategory": "browser", "title": "브라우저 렌더링 파이프라인 (DOM → Paint)", "difficulty": "intermediate"},
    {"category": "web", "subcategory": "browser", "title": "이벤트 루프와 비동기 처리 (콜스택, 태스크 큐)", "difficulty": "intermediate"},
    {"category": "web", "subcategory": "browser", "title": "웹 소켓 vs SSE vs Long Polling", "difficulty": "intermediate"},
    {"category": "web", "subcategory": "browser", "title": "서비스 워커와 오프라인 캐싱", "difficulty": "advanced"},

    # ── 웹: API ──
    {"category": "web", "subcategory": "api", "title": "GraphQL vs REST 트레이드오프", "difficulty": "intermediate"},
    {"category": "web", "subcategory": "api", "title": "gRPC가 빠른 이유 (Protocol Buffers, HTTP/2)", "difficulty": "intermediate"},
    {"category": "web", "subcategory": "api", "title": "API 버전 관리 전략", "difficulty": "beginner"},
    {"category": "web", "subcategory": "api", "title": "Idempotency와 안전한 API 설계", "difficulty": "intermediate"},

    # ── 네트워크: 고급 ──
    {"category": "network", "subcategory": "advanced", "title": "OSI 7계층과 TCP/IP 4계층 매핑", "difficulty": "beginner"},
    {"category": "network", "subcategory": "advanced", "title": "NAT와 포트포워딩", "difficulty": "beginner"},
    {"category": "network", "subcategory": "advanced", "title": "서브넷팅과 CIDR 표기법", "difficulty": "intermediate"},
    {"category": "network", "subcategory": "advanced", "title": "HTTP/3와 QUIC 프로토콜", "difficulty": "advanced"},

    # ── 프로그래밍 언어론 ──
    {"category": "programming", "subcategory": "concept", "title": "컴파일러 vs 인터프리터 vs JIT", "difficulty": "beginner"},
    {"category": "programming", "subcategory": "concept", "title": "가비지 컬렉션 알고리즘 (Mark-Sweep, Generational)", "difficulty": "intermediate"},
    {"category": "programming", "subcategory": "concept", "title": "동시성 모델: 멀티스레드 vs 이벤트루프 vs Actor", "difficulty": "intermediate"},
    {"category": "programming", "subcategory": "concept", "title": "직렬화(Serialization)와 데이터 포맷", "difficulty": "beginner"},
    {"category": "programming", "subcategory": "concept", "title": "함수형 프로그래밍의 핵심: 불변성과 순수 함수", "difficulty": "intermediate"},
]
