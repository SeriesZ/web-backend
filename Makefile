# Makefile

# 사용할 도구
AUTOFLAKE = autoflake
BLACK = black
ISORT = isort

# 코드가 있는 디렉토리
SRC_DIR = .

# .py 파일을 대상으로 지정
PY_FILES = $(shell find $(SRC_DIR) -path $(SRC_DIR)/venv -prune -o -name "*.py" -print)

# 기본 목표: format
format: format-autoflake format-black format-isort

# autoflake: 사용하지 않는 임포트 및 변수를 제거
format-autoflake:
	@echo "Removing unused imports and variables with autoflake..."
	$(AUTOFLAKE) --exclude=venv --in-place --remove-all-unused-imports --remove-unused-variables --recursive $(SRC_DIR)

# black: 코드 포매팅
format-black:
	@echo "Using black at: $(BLACK)"
	@echo "Formatting code with black..."
	$(BLACK) $(PY_FILES) --line-length 79

# isort: 임포트 정리
format-isort:
	@echo "Sorting imports with isort..."
	$(ISORT) $(SRC_DIR)

.PHONY: format format-autoflake format-black format-isort