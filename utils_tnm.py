
from typing import Optional

def tnm_stage_group(T: str, N: str, M: str) -> str:
    """AJCC 8th (NSCLC) stage grouping for common T categories used in this helper."""
    if M == "M1c":
        return "Stage IVB"
    if M in ("M1a", "M1b"):
        return "Stage IVA"
    if M != "M0":
        return "Check TNM"

    if T == "TX" or not T:
        return "Check TNM"

    if N == "N0":
        if T == "Tis":
            return "Stage 0"
        if T == "T1mi":
            return "Stage IA1"
        if T == "T1a":
            return "Stage IA1"
        if T == "T1b":
            return "Stage IA2"
        if T == "T1c":
            return "Stage IA3"
        if T == "T2a":
            return "Stage IB"
        if T == "T2b":
            return "Stage IIA"
        if T == "T3":
            return "Stage IIB"
        if T == "T4":
            return "Stage IIIA"
    if N == "N1":
        if T in ("T1mi", "T1a", "T1b", "T1c"):
            return "Stage IIB"
        if T == "T2a":
            return "Stage IIB"
        if T == "T2b":
            return "Stage IIB"
        if T == "T3":
            return "Stage IIIA"
        if T == "T4":
            return "Stage IIIA"
    if N == "N2":
        if T in ("T1mi", "T1a", "T1b", "T1c"):
            return "Stage IIIA"
        if T == "T2a":
            return "Stage IIIA"
        if T == "T2b":
            return "Stage IIIA"
        if T == "T3":
            return "Stage IIIB"
        if T == "T4":
            return "Stage IIIB"
    if N == "N3":
        if T in ("T1mi", "T1a", "T1b", "T1c", "T2a"):
            return "Stage IIIB"
        if T in ("T2b", "T3", "T4"):
            return "Stage IIIC"

    return "Check TNM"

def parse_size_cm(s: str) -> Optional[float]:
    s = (s or "").strip()
    if not s:
        return None
    # allow commas
    s = s.replace(",", ".")
    try:
        v = float(s)
        if v <= 0:
            return None
        return v
    except ValueError:
        return None

def compute_T(
    size_cm: Optional[float],
    mia: bool,
    main_bronchus: bool,
    visceral_pleura: bool,
    atelectasis: bool,
    chest_wall: bool,
    same_lobe_nodule: bool,
    diff_lobe_nodule: bool,
    critical_organs: bool,
    tis: bool,
) -> str:
    # Priorities follow the desktop helper logic
    if tis:
        return "Tis"

    # T4
    if critical_organs or diff_lobe_nodule:
        return "T4"
    # T3
    if chest_wall or same_lobe_nodule:
        return "T3"

    # T2 features OR size > 3
    if main_bronchus or visceral_pleura or atelectasis or (size_cm is not None and size_cm > 3):
        if size_cm is not None and size_cm > 4:
            return "T2b"
        return "T2a"

    # Size-based T1
    if size_cm is None:
        return "TX"

    if mia and size_cm <= 0.5:
        return "T1mi"
    if size_cm <= 1:
        return "T1a"
    if size_cm <= 2:
        return "T1b"
    if size_cm <= 3:
        return "T1c"
    return "TX"
