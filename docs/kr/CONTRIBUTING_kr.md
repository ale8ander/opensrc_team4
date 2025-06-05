# 프로젝트 기여 가이드

**모든 형태의 기여를 환영합니다!**

설치에 어려움을 겪고 있다면 [INSTALL.md](../INSTALL.md)를 참고하세요.

## 기여 가능한 영역

* [ ] 버그 제보 (예: 프로그램 크래시, 잘못된 제스처 인식, 호환성 문제 등)
* [ ] 기존 기능 또는 아키텍처 개선 제안
* [ ] 문서 개선 또는 초보자를 위한 설명 추가
* [ ] 코드 주석 또는 문서 내 오탈자 및 문법 오류 수정
* [ ] 새로운 기능 구현 (예: 더 많은 제스처 지원, 동적 제스처, 다중 손 인식 등)
* [ ] 기존 코드 리팩터링 또는 최적화 (성능, 가독성, 유지보수성 향상 등)
* *[ROADMAP.md](../ROADMAP.md)도 참고하시면 좋습니다.*

---

## 코드 스타일 가이드

* [PEP 8 Python Style Guide](https://peps.python.org/pep-0008/)를 준수해주세요.
* 가능하다면 함수, 클래스, 모듈에 docstring을 추가하여 코드의 가독성과 유지보수성을 높여주세요.

---

## 기여 방법

* Issue 작성
* 해당 레포지토리 `Fork`
* 새 브랜치 생성: `git checkout -b feature/your-feature-name (or issue#)`
* 변경사항 커밋: `git commit -m "Add feature xyz"`
* 본인 Fork 저장소에 푸시: `git push origin feature/your-feature-name`
* 메인 레포지토리에 Pull Request (PR) 생성

### 기여 절차 (상세)

#### 1. Issue 작성

* 먼저 `GitHub Issue`를 작성해주세요.
* 기여하고자 하는 내용을 ***자세히*** 설명해주세요.

  * Issue에 충분히 설명한 경우, PR에서는 간단히 Issue만 링크하셔도 됩니다.
  * *설명이 자세할수록 PR이 거절될 가능성이 낮아집니다.*

#### 2. Fork 및 브랜치 생성

* 프로젝트를 Fork 해주세요.
* 본인의 Fork 저장소를 로컬에 클론한 후, 새 브랜치를 생성하세요:

```bash
git clone {forked repository URL}
cd {repository folder}
git checkout -b feature/issue#-number
```

#### 3. 변경사항 구현

* 필요한 수정사항을 적용하거나 새로운 기능을 추가하세요.

#### 4. 커밋 작성

* 아래 스타일을 참고하여 커밋 메시지를 작성해주세요:

  * feat(issue#N): 새로운 기능 추가

  * fix(issue#N): 제스처 인식 버그 수정

  * docs(issue#N): 문서 개선

#### 5. 본인 Fork 저장소에 푸시

```bash
git push origin feature/issue#-number
```

#### 6. 메인 레포지토리에 Pull Request 생성

* 본인의 Fork 저장소에서 GitHub에 접속하세요.
* `Compare & pull request` 버튼을 클릭하세요.
* PR의 목적을 명확하게 작성하고, 관련된 Issue를 반드시 링크해주세요.

  * Issue에 충분한 설명이 있다면 PR 설명은 간단하게 작성하거나 생략하셔도 됩니다.
  * PR 생성 시 반드시 ***관련 Issue 링크***를 추가해주세요 (예: Closes #12).
* 필요하다면 스크린샷이나 로그도 첨부해주세요.

---

## 라이선스

* 본 프로젝트는 MIT License 하에 운영됩니다.
* 모든 기여는 해당 라이선스에 따라 적용됩니다.
