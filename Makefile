.PHONY: setup test check

# Install dependencies and the pre-commit hooks (privacy layer 3, DESIGN §13.2).
setup:
	@command -v gitleaks >/dev/null || { echo "gitleaks is missing: brew install gitleaks"; exit 1; }
	uv sync
	uv run pre-commit install

test:
	uv run pytest

# Local version of the CI checks: staged files plus every commit not yet on main.
check:
	uv run python scripts/check_private.py --staged
	gitleaks git --pre-commit --staged --redact --no-banner
	@if git rev-parse --verify --quiet main >/dev/null; then \
		base=$$(git merge-base main HEAD) && \
		uv run python scripts/check_private.py --commits "$$base" HEAD && \
		gitleaks git --redact --no-banner --log-opts="$$base..HEAD" . && \
		uv run python scripts/check_decisions.py --base "$$base"; \
	else \
		uv run python scripts/check_decisions.py; \
	fi
	uv run pytest
