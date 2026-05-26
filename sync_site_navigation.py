from __future__ import annotations

import sync_footer_badge
import sync_nontechnical_sidebar
import sync_technical_sidebar


def main() -> None:
    sync_technical_sidebar.main()
    sync_nontechnical_sidebar.main()
    sync_footer_badge.main()


if __name__ == "__main__":
    main()