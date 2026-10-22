import hashlib
from pathlib import Path

from evidence_packet import build, sha256_of


def test_build_packet(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "receipt.txt").write_text("paid $1,250.47")
    sub = src / "emails"
    sub.mkdir()
    (sub / "denial.eml").write_text("we regret to inform you")

    out = tmp_path / "packet"
    entries = build(src, out, "Test Dispute", "Tester")

    assert len(entries) == 2
    assert (out / "INDEX.md").exists()
    assert (out / "index.csv").exists()
    assert (out / "files" / "receipt.txt").read_text() == "paid $1,250.47"
    assert entries[0].sha256 == sha256_of(src / entries[0].rel_path)


def test_hash_matches_manual(tmp_path: Path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"\x00\x01\x02")
    assert sha256_of(p) == hashlib.sha256(b"\x00\x01\x02").hexdigest()
