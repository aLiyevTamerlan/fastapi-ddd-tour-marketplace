def normalize_text(value: str) -> str:
    """Trim and collapse inner whitespace, so ``"  Qəbələ   turu "`` and ``"Qəbələ turu"`` are one value."""
    return " ".join(value.split())
