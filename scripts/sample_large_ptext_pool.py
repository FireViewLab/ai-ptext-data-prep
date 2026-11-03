"""Build a deterministic, unlabeled large-review sampling pool safely.

The canonical manifest and raw CSV files are read-only inputs. Selection is
performed in a new staging SQLite database, and a final directory is published
only after every selected CSV row matches the manifest identity and normalized
content fingerprint. Candidate/control/diversity are sampling purposes, never
human or model labels.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass, field
from hashlib import sha256
import heapq
import json
import math
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from typing import Iterable
from uuid import uuid4

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_new_review_inventory import (  # noqa: E402
    canonical_identifier,
    normalize_content,
)


PROJECT_ROOT = SCRIPTS_DIR.parent
PRIVATE_OUTPUT_ROOT = PROJECT_ROOT / "private_outputs"
DEFAULT_DATABASE = PROJECT_ROOT / "outputs" / "large_human_review_candidate_manifest_20261028.sqlite3"
PLATFORMS = ("elevenst", "kurly", "musinsa", "naver", "ohouse", "oliveyoung")
DEFAULT_RAW_ROOT = Path(r"C:\Users\kimha\OneDrive\Desktop\review-export-20261017\review-export-20261017")
DEFAULT_POLICY_VERSION = "ptext-large-pool-v1"
DEFAULT_TARGETS = {"CANDIDATE": 60_000, "CONTROL": 70_000, "DIVERSITY": 20_000}
PILOT_TARGETS = {"CANDIDATE": 400, "CONTROL": 467, "DIVERSITY": 133}
REQUIRED_COLUMNS = ("platform", "product_id", "review_id", "content", "product_category")
OUTPUT_FIELDS = (
    "pool_id", "row_uid", "sampling_group", "sampling_reason", "label_status",
    "platform", "source_row", "product_id", "review_id", "product_category_raw",
    "normalized_category", "content", "normalized_content_hash", "content_length",
    "duplicate_cluster_id", "candidate_sources", "original_candidate_member",
    "original_control_eligible", "seed", "policy_version",
)
DISK_ESTIMATE = {
    "staging_bytes_per_manifest_row": 1_024,
    "output_bytes_per_selected_row": 4_096,
    "fixed_overhead_bytes": 64 * 1024 * 1024,
    "safety_multiplier": 1.25,
}


class PipelineError(RuntimeError):
    """A fail-closed pipeline error whose message is safe for console output."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def raw_csv_path(root: Path, platform: str) -> Path:
    """Resolve both the documented nested export and a flat fixture layout."""
    name = f"reviews_{platform}.csv"
    nested = root / name / name
    return nested if nested.exists() else root / name


def content_fingerprint(value: str | None) -> tuple[str | None, int | None]:
    normalized = normalize_content(value)
    if normalized is None:
        return None, None
    return sha256(normalized.encode("utf-8")).hexdigest(), len(normalized)


def stable_priority(seed: int, policy_version: str, group: str, row_uid: str) -> str:
    payload = "\x1f".join((policy_version, str(seed), group, row_uid))
    return sha256(payload.encode("utf-8")).hexdigest()


def stable_stratum_key(seed: int, policy_version: str, group: str, key: tuple[str, str]) -> str:
    payload = "\x1f".join((policy_version, str(seed), group, key[0], key[1]))
    return sha256(payload.encode("utf-8")).hexdigest()


def connect_read_only(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise PipelineError("CANONICAL_DATABASE_NOT_FOUND")
    db = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
    db.execute("PRAGMA query_only=ON")
    db.execute("PRAGMA temp_store=MEMORY")
    if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
        db.close()
        raise PipelineError("CANONICAL_DATABASE_QUICK_CHECK_FAILED")
    return db


def load_canonical_contract(db: sqlite3.Connection) -> dict:
    """Load and validate the source-signature contract without assuming it exists."""
    try:
        row = db.execute("SELECT value FROM metadata WHERE key='summary_json'").fetchone()
    except sqlite3.Error as exc:
        raise PipelineError("CANONICAL_SOURCE_SIGNATURES_MISSING") from exc
    if row is None:
        raise PipelineError("CANONICAL_SOURCE_SIGNATURES_MISSING")
    try:
        summary = json.loads(row[0])
        signatures = summary["execution"]["source_signatures_before"]
    except (TypeError, ValueError, KeyError) as exc:
        raise PipelineError("CANONICAL_SOURCE_SIGNATURES_MISSING") from exc
    if not isinstance(signatures, dict) or not signatures:
        raise PipelineError("CANONICAL_SOURCE_SIGNATURES_MISSING")
    normalized = {}
    for platform, signature in signatures.items():
        if (
            not isinstance(platform, str)
            or not isinstance(signature, dict)
            or type(signature.get("size")) is not int
            or type(signature.get("mtime_ns")) is not int
        ):
            raise PipelineError("CANONICAL_SOURCE_SIGNATURES_INVALID")
        normalized[platform] = {
            "size": signature["size"],
            "mtime_ns": signature["mtime_ns"],
        }
    manifest_counts = dict(db.execute(
        "SELECT platform,COUNT(*) FROM review_index GROUP BY platform ORDER BY platform"
    ))
    if not manifest_counts or set(manifest_counts) != set(normalized):
        raise PipelineError("CANONICAL_PLATFORM_CONTRACT_MISMATCH")
    return {"stored_signatures": normalized, "manifest_platform_rows": manifest_counts}


def verify_raw_preflight(canonical_path: Path, raw_paths: dict[str, Path]) -> dict:
    """Verify current raw signatures, platform identity, and full row counts."""
    db = connect_read_only(canonical_path)
    try:
        contract = load_canonical_contract(db)
    finally:
        db.close()
    stored = contract["stored_signatures"]
    manifest_counts = contract["manifest_platform_rows"]
    if set(raw_paths) != set(stored):
        raise PipelineError("RAW_PLATFORM_SET_MISMATCH")
    current_signatures = {}
    observed_counts = {}
    for platform in sorted(stored):
        path = raw_paths[platform]
        if not path.is_file():
            raise PipelineError("RAW_CSV_NOT_FOUND")
        before = file_signature(path)
        if before["size"] != stored[platform]["size"]:
            raise PipelineError("RAW_SOURCE_SIZE_MISMATCH")
        if before["mtime_ns"] != stored[platform]["mtime_ns"]:
            raise PipelineError("RAW_SOURCE_MTIME_MISMATCH")
        count = 0
        with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [
                name for name in REQUIRED_COLUMNS
                if not reader.fieldnames or reader.fieldnames.count(name) != 1
            ]
            if missing or (reader.fieldnames and len(reader.fieldnames) != len(set(reader.fieldnames))):
                raise PipelineError("RAW_CSV_HEADER_INVALID")
            for row in reader:
                count += 1
                if canonical_identifier(row.get("platform")) != platform:
                    raise PipelineError("RAW_PLATFORM_IDENTITY_MISMATCH")
        after = file_signature(path)
        if after != before:
            raise PipelineError("RAW_CSV_CHANGED_DURING_PREFLIGHT")
        if count != manifest_counts[platform]:
            raise PipelineError("RAW_MANIFEST_ROW_COUNT_MISMATCH")
        current_signatures[platform] = before
        observed_counts[platform] = count
    return {
        "status": "VERIFIED",
        "signature_method": "size_and_mtime_ns",
        "file_sha256_verified": False,
        "assurance_limit": (
            "size+mtime detects ordinary replacement or modification but is not cryptographic; "
            "an attacker or tool able to preserve both values could evade this check. Selected rows "
            "are additionally verified by normalized-content SHA-256 and exact identity fields."
        ),
        "manifest_platform_rows": manifest_counts,
        "observed_platform_rows": observed_counts,
        "stored_signatures": stored,
        "current_signatures": current_signatures,
        "total_manifest_rows": sum(manifest_counts.values()),
    }


def nearest_existing_directory(path: Path) -> Path:
    candidate = path.resolve()
    while not candidate.exists():
        parent = candidate.parent
        if parent == candidate:
            raise PipelineError("DISK_CHECK_PATH_NOT_FOUND")
        candidate = parent
    if not candidate.is_dir():
        candidate = candidate.parent
    return candidate


def check_disk_capacity(output_parent: Path, manifest_rows: int, selected_rows: int) -> dict:
    basis = dict(DISK_ESTIMATE)
    staging = manifest_rows * basis["staging_bytes_per_manifest_row"]
    output = selected_rows * basis["output_bytes_per_selected_row"]
    subtotal = staging + output + basis["fixed_overhead_bytes"]
    required = math.ceil(subtotal * basis["safety_multiplier"])
    usage = shutil.disk_usage(nearest_existing_directory(output_parent))
    report = {
        "status": "SUFFICIENT" if usage.free >= required else "INSUFFICIENT",
        "free_bytes": usage.free,
        "required_minimum_bytes": required,
        "estimated_staging_wal_and_indexes_bytes": staging,
        "estimated_output_csv_bytes": output,
        "fixed_overhead_bytes": basis["fixed_overhead_bytes"],
        "safety_multiplier": basis["safety_multiplier"],
        "includes": ["staging SQLite", "indexes", "journal/WAL", "output CSV", "safety margin"],
        "sqlite_temp_policy": "connection-local PRAGMA temp_store=MEMORY; no global environment change",
        "assurance_limit": (
            "free space can change after this check because of concurrent processes; estimates are "
            "conservative planning values, not a hard upper bound for unusually long review text"
        ),
    }
    if report["status"] != "SUFFICIENT":
        raise PipelineError("INSUFFICIENT_DISK_SPACE")
    return report


def file_signature(path: Path) -> dict[str, int]:
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def assert_git_ignored(path: Path, project_root: Path = PROJECT_ROOT) -> None:
    try:
        relative = path.resolve().relative_to(project_root.resolve())
    except ValueError as exc:
        raise PipelineError("OUTPUT_OUTSIDE_PROJECT_PRIVATE_ROOT") from exc
    if not relative.parts or relative.parts[0] != "private_outputs":
        raise PipelineError("OUTPUT_OUTSIDE_PROJECT_PRIVATE_ROOT")
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", str(relative)],
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise PipelineError("PRIVATE_OUTPUT_NOT_GIT_IGNORED")


def validate_targets(targets: dict[str, int]) -> None:
    if set(targets) != set(DEFAULT_TARGETS):
        raise PipelineError("INVALID_GROUP_TARGETS")
    if any(type(value) is not int or value < 0 for value in targets.values()):
        raise PipelineError("INVALID_GROUP_TARGETS")


def allocate_quotas(capacities: dict[tuple[str, str], int], target: int) -> tuple[dict[tuple[str, str], int], int]:
    """Capacity-aware square-root allocation with deterministic redistribution."""
    quotas = {key: 0 for key in capacities}
    remaining = min(target, sum(capacities.values()))
    while remaining:
        active = {key: cap - quotas[key] for key, cap in capacities.items() if cap > quotas[key]}
        if not active:
            break
        weights = {key: math.sqrt(value) for key, value in active.items()}
        denominator = sum(weights.values())
        ideals = {key: remaining * weight / denominator for key, weight in weights.items()}
        additions = {
            key: min(active[key], int(ideal))
            for key, ideal in ideals.items()
        }
        added = sum(additions.values())
        if added:
            for key, value in additions.items():
                quotas[key] += value
            remaining -= added
            continue
        key = min(
            active,
            key=lambda item: (-(ideals[item] - int(ideals[item])), item[0], item[1]),
        )
        quotas[key] += 1
        remaining -= 1
    return quotas, target - sum(quotas.values())


def create_staging_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;
        PRAGMA temp_store=MEMORY;
        CREATE TABLE eligible (
          row_uid TEXT PRIMARY KEY, platform TEXT NOT NULL, source_row INTEGER NOT NULL,
          product_id TEXT NOT NULL, review_id TEXT NOT NULL, product_category_raw TEXT NOT NULL,
          normalized_category TEXT NOT NULL, normalized_content_hash TEXT NOT NULL,
          content_length INTEGER NOT NULL, cluster_id TEXT, candidate_member INTEGER NOT NULL,
          control_member INTEGER NOT NULL, candidate_sources TEXT NOT NULL,
          priority_candidate TEXT NOT NULL, priority_control TEXT NOT NULL,
          priority_diversity TEXT NOT NULL
        ) WITHOUT ROWID;
        CREATE TABLE selection (
          row_uid TEXT PRIMARY KEY, sampling_group TEXT NOT NULL, sampling_reason TEXT NOT NULL,
          platform TEXT NOT NULL, source_row INTEGER NOT NULL, product_id TEXT NOT NULL,
          review_id TEXT NOT NULL, product_category_raw TEXT NOT NULL,
          normalized_category TEXT NOT NULL, normalized_content_hash TEXT NOT NULL,
          content_length INTEGER NOT NULL, cluster_id TEXT, candidate_sources TEXT NOT NULL,
          original_candidate_member INTEGER NOT NULL, original_control_eligible INTEGER NOT NULL,
          priority TEXT NOT NULL
        ) WITHOUT ROWID;
        CREATE UNIQUE INDEX selection_platform_row_idx ON selection(platform, source_row);
        CREATE INDEX eligible_candidate_stratum_idx
          ON eligible(candidate_member, platform, normalized_category, priority_candidate);
        CREATE INDEX eligible_control_stratum_idx
          ON eligible(control_member, candidate_member, platform, normalized_category, priority_control);
        CREATE INDEX eligible_diversity_stratum_idx
          ON eligible(platform, normalized_category, priority_diversity);
        """
    )


def stream_manifest_to_staging(
    canonical: sqlite3.Connection,
    staging: sqlite3.Connection,
    seed: int,
    policy_version: str,
    chunk_size: int = 5_000,
) -> dict[str, int]:
    sql = """
      SELECT r.row_uid,r.platform,r.source_row,r.product_id,r.review_id,
             r.product_category_raw,r.normalized_category,r.normalized_content_hash,
             r.content_length,dm.cluster_id,
             CASE WHEN c.row_uid IS NULL THEN 0 ELSE 1 END,
             CASE WHEN e.row_uid IS NULL THEN 0 ELSE 1 END,
             COALESCE(s.candidate_sources,'')
      FROM review_index r
      LEFT JOIN candidate_content c USING(row_uid)
      LEFT JOIN random_control_eligible e USING(row_uid)
      LEFT JOIN duplicate_members dm USING(row_uid)
      LEFT JOIN (
        SELECT row_uid,GROUP_CONCAT(candidate_source,'|') AS candidate_sources
        FROM (SELECT row_uid,candidate_source FROM source_evidence ORDER BY row_uid,candidate_source)
        GROUP BY row_uid
      ) s USING(row_uid)
      WHERE r.valid_identity=1 AND r.valid_content=1
    """
    cursor = canonical.execute(sql)
    counts = Counter()
    while True:
        batch = cursor.fetchmany(chunk_size)
        if not batch:
            break
        prepared = []
        for row in batch:
            row_uid = row[0]
            if None in (row[3], row[4], row[7], row[8]):
                continue
            prepared.append(tuple(row) + (
                stable_priority(seed, policy_version, "CANDIDATE", row_uid),
                stable_priority(seed, policy_version, "CONTROL", row_uid),
                stable_priority(seed, policy_version, "DIVERSITY", row_uid),
            ))
            counts["eligible"] += 1
            counts["candidate"] += row[10]
            counts["control_raw"] += row[11]
            counts["candidate_control_overlap"] += int(row[10] and row[11])
        staging.executemany("INSERT INTO eligible VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", prepared)
        staging.commit()
    return dict(counts)


@dataclass
class SelectionState:
    hash_cap: int
    cluster_cap: int
    product_cap: int
    used: set[str] = field(default_factory=set)
    hashes: Counter = field(default_factory=Counter)
    clusters: Counter = field(default_factory=Counter)
    products: Counter = field(default_factory=Counter)

    def accept(self, row: sqlite3.Row) -> tuple[bool, str | None]:
        uid = row["row_uid"]
        product = (row["platform"], row["product_id"])
        digest = row["normalized_content_hash"]
        cluster = row["cluster_id"]
        if uid in self.used:
            return False, "row_uid"
        if self.hashes[digest] >= self.hash_cap:
            return False, "normalized_hash_cap"
        if cluster and self.clusters[cluster] >= self.cluster_cap:
            return False, "cluster_cap"
        if self.products[product] >= self.product_cap:
            return False, "product_cap"
        self.used.add(uid)
        self.hashes[digest] += 1
        if cluster:
            self.clusters[cluster] += 1
        self.products[product] += 1
        return True, None


ELIGIBLE_COLUMNS = (
    "row_uid,platform,source_row,product_id,review_id,product_category_raw,"
    "normalized_category,normalized_content_hash,content_length,cluster_id,"
    "candidate_member,control_member,candidate_sources"
)


def group_predicate(group: str) -> tuple[str, str]:
    if group == "CANDIDATE":
        return "candidate_member=1", "priority_candidate"
    if group == "CONTROL":
        return "control_member=1 AND candidate_member=0", "priority_control"
    if group == "DIVERSITY":
        return "1=1", "priority_diversity"
    raise PipelineError("INVALID_GROUP")


def insert_selection(db: sqlite3.Connection, row: sqlite3.Row, group: str, reason: str, priority: str) -> None:
    db.execute(
        "INSERT INTO selection VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            row["row_uid"], group, reason, row["platform"], row["source_row"],
            row["product_id"], row["review_id"], row["product_category_raw"],
            row["normalized_category"], row["normalized_content_hash"],
            row["content_length"], row["cluster_id"], row["candidate_sources"],
            row["candidate_member"], row["control_member"], priority,
        ),
    )


def select_group(
    db: sqlite3.Connection,
    group: str,
    target: int,
    state: SelectionState,
    seed: int,
    policy_version: str,
) -> dict:
    predicate, priority_column = group_predicate(group)
    capacity_rows = db.execute(
        f"SELECT platform,normalized_category,COUNT(*) FROM eligible "
        f"WHERE {predicate} AND row_uid NOT IN (SELECT row_uid FROM selection) "
        "GROUP BY platform,normalized_category"
    ).fetchall()
    capacities = {(row[0], row[1]): row[2] for row in capacity_rows}
    quotas, availability_shortfall = allocate_quotas(capacities, target)
    selected_by_stratum = Counter()
    rejected = Counter()
    selected = 0
    strata = sorted(
        capacities,
        key=lambda key: stable_stratum_key(seed, policy_version, group, key),
    )
    for platform, category in strata:
        quota = quotas[(platform, category)]
        if quota <= 0:
            continue
        cursor = db.execute(
            f"SELECT {ELIGIBLE_COLUMNS},{priority_column} AS priority FROM eligible "
            f"WHERE {predicate} AND platform=? AND normalized_category=? "
            f"ORDER BY {priority_column},row_uid",
            (platform, category),
        )
        for row in cursor:
            accepted, reason = state.accept(row)
            if not accepted:
                rejected[reason] += 1
                continue
            insert_selection(db, row, group, "STRATUM_QUOTA", row["priority"])
            selected += 1
            selected_by_stratum[(platform, category)] += 1
            if selected_by_stratum[(platform, category)] >= quota:
                break

    initial_selected = selected
    if selected < target:
        # Merge the already-indexed per-stratum streams in priority order. This
        # avoids one corpus-wide SQLite ORDER BY and its potentially external
        # temporary file while keeping deterministic redistribution semantics.
        streams = []
        heap = []

        def push_next(index: int) -> None:
            cursor = streams[index]
            for candidate in cursor:
                if candidate["row_uid"] not in state.used:
                    heapq.heappush(
                        heap,
                        (candidate["priority"], candidate["row_uid"], index, candidate),
                    )
                    return

        for platform, category in strata:
            cursor = db.execute(
                f"SELECT {ELIGIBLE_COLUMNS},{priority_column} AS priority FROM eligible "
                f"WHERE {predicate} AND platform=? AND normalized_category=? "
                f"ORDER BY {priority_column},row_uid",
                (platform, category),
            )
            streams.append(cursor)
            push_next(len(streams) - 1)
        while heap and selected < target:
            _, _, index, row = heapq.heappop(heap)
            accepted, reason = state.accept(row)
            if not accepted:
                rejected[reason] += 1
            else:
                insert_selection(db, row, group, "DETERMINISTIC_REDISTRIBUTION", row["priority"])
                selected += 1
                selected_by_stratum[(row["platform"], row["normalized_category"])] += 1
            push_next(index)
    db.commit()
    rejection_attempts = dict(sorted(rejected.items()))
    return {
        "target": target,
        "selected": selected,
        "shortfall": target - selected,
        "availability_shortfall_before_caps": availability_shortfall,
        "initial_quota_selected": initial_selected,
        "redistributed_selected": selected - initial_selected,
        "capacities": {f"{p}|{c}": n for (p, c), n in sorted(capacities.items())},
        "quotas": {f"{p}|{c}": n for (p, c), n in sorted(quotas.items())},
        "selected_by_stratum": {
            f"{p}|{c}": n for (p, c), n in sorted(selected_by_stratum.items())
        },
        "cap_rejection_attempts": rejection_attempts,
        "cap_rejection_metric": "selection attempts; the same row may be attempted in quota and redistribution phases",
        "cap_rejections": rejection_attempts,
        "cap_rejections_compatibility": "deprecated alias of cap_rejection_attempts",
    }


def selection_report(db: sqlite3.Connection, group_reports: dict, import_counts: dict, targets: dict) -> dict:
    group_counts = dict(db.execute("SELECT sampling_group,COUNT(*) FROM selection GROUP BY sampling_group"))
    platform = {}
    category = {}
    for group in targets:
        platform[group] = dict(db.execute(
            "SELECT platform,COUNT(*) FROM selection WHERE sampling_group=? GROUP BY platform ORDER BY platform",
            (group,),
        ))
        category[group] = dict(db.execute(
            "SELECT normalized_category,COUNT(*) FROM selection WHERE sampling_group=? GROUP BY normalized_category ORDER BY normalized_category",
            (group,),
        ))
    source_counts = dict(db.execute(
        "SELECT value,COUNT(*) FROM ("
        "SELECT CASE WHEN candidate_sources='' THEN '<NONE>' ELSE candidate_sources END value "
        "FROM selection WHERE sampling_group='CANDIDATE') GROUP BY value ORDER BY value"
    ))
    individual_sources = Counter()
    for (sources,) in db.execute(
        "SELECT candidate_sources FROM selection WHERE sampling_group='CANDIDATE'"
    ):
        for source in filter(None, sources.split("|")):
            individual_sources[source] += 1
    multi_source = db.execute(
        "SELECT COUNT(*) FROM selection WHERE sampling_group='CANDIDATE' AND candidate_sources LIKE '%|%'"
    ).fetchone()[0]
    diversity_membership = {
        "candidate_member": db.execute(
            "SELECT COUNT(*) FROM selection WHERE sampling_group='DIVERSITY' AND original_candidate_member=1"
        ).fetchone()[0],
        "control_eligible": db.execute(
            "SELECT COUNT(*) FROM selection WHERE sampling_group='DIVERSITY' AND original_control_eligible=1"
        ).fetchone()[0],
    }
    total = sum(group_counts.values())
    unique = db.execute("SELECT COUNT(DISTINCT row_uid) FROM selection").fetchone()[0]
    control_candidate_overlap = db.execute(
        "SELECT COUNT(*) FROM selection WHERE sampling_group='CONTROL' AND original_candidate_member=1"
    ).fetchone()[0]
    status = "READY" if all(group_counts.get(group, 0) == target for group, target in targets.items()) else "INSUFFICIENT_CAPACITY"
    return {
        "status": status,
        "targets": targets,
        "selected": group_counts,
        "total_selected": total,
        "unique_row_uid": unique,
        "row_uid_overlap_count": total - unique,
        "control_candidate_overlap_count": control_candidate_overlap,
        "import_counts": import_counts,
        "groups": group_reports,
        "coverage": {"platform": platform, "normalized_category": category},
        "candidate_source_combinations": source_counts,
        "candidate_source_counts": dict(sorted(individual_sources.items())),
        "candidate_multi_source_count": multi_source,
        "diversity_original_membership": diversity_membership,
    }


def select_pool(
    canonical_path: Path,
    staging_path: Path,
    targets: dict[str, int],
    seed: int,
    policy_version: str,
    hash_cap: int,
    cluster_cap: int,
    product_cap: int,
) -> dict:
    validate_targets(targets)
    if min(hash_cap, cluster_cap, product_cap) < 1:
        raise PipelineError("INVALID_CAP")
    if staging_path.exists():
        raise PipelineError("STAGING_PATH_ALREADY_EXISTS")
    canonical = connect_read_only(canonical_path)
    staging = sqlite3.connect(staging_path)
    staging.row_factory = sqlite3.Row
    try:
        create_staging_schema(staging)
        import_counts = stream_manifest_to_staging(canonical, staging, seed, policy_version)
        state = SelectionState(hash_cap, cluster_cap, product_cap)
        group_reports = {}
        for group in ("CANDIDATE", "CONTROL", "DIVERSITY"):
            group_reports[group] = select_group(
                staging, group, targets[group], state, seed, policy_version
            )
        report = selection_report(staging, group_reports, import_counts, targets)
        report["seed"] = seed
        report["policy_version"] = policy_version
        if report["row_uid_overlap_count"] or report["control_candidate_overlap_count"]:
            raise PipelineError("GROUP_SEPARATION_INVARIANT_FAILED")
        staging.execute("CREATE TABLE run_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID")
        staging.executemany(
            "INSERT INTO run_metadata VALUES(?,?)",
            (
                ("seed", str(seed)),
                ("policy_version", policy_version),
                ("selection_report", json.dumps(report, ensure_ascii=False, separators=(",", ":"))),
            ),
        )
        staging.commit()
        return report
    finally:
        canonical.close()
        staging.close()


def safe_json_write(path: Path, value: dict) -> None:
    if path.exists():
        raise PipelineError("OUTPUT_FILE_ALREADY_EXISTS")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def materialize_selected_rows(
    staging_path: Path,
    raw_paths: dict[str, Path],
    output_csv: Path,
    seed: int,
    policy_version: str,
) -> dict:
    if output_csv.exists():
        raise PipelineError("OUTPUT_FILE_ALREADY_EXISTS")
    db = sqlite3.connect(f"file:{staging_path.resolve().as_posix()}?mode=ro", uri=True)
    db.execute("PRAGMA query_only=ON")
    db.execute("PRAGMA temp_store=MEMORY")
    db.row_factory = sqlite3.Row
    signatures_before = {}
    signatures_after = {}
    written = Counter()
    hasher = sha256()
    try:
        with output_csv.open("x", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            for platform in sorted(raw_paths):
                path = raw_paths[platform]
                if not path.is_file():
                    raise PipelineError("RAW_CSV_NOT_FOUND")
                signatures_before[platform] = file_signature(path)
                selected = iter(db.execute(
                    "SELECT * FROM selection WHERE platform=? ORDER BY source_row",
                    (platform,),
                ))
                expected = next(selected, None)
                with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as raw:
                    reader = csv.DictReader(raw)
                    missing = [name for name in REQUIRED_COLUMNS if not reader.fieldnames or reader.fieldnames.count(name) != 1]
                    if missing or (reader.fieldnames and len(reader.fieldnames) != len(set(reader.fieldnames))):
                        raise PipelineError("RAW_CSV_HEADER_INVALID")
                    for source_row, row in enumerate(reader, start=2):
                        if expected is None:
                            break
                        if source_row < expected["source_row"]:
                            continue
                        if source_row > expected["source_row"]:
                            raise PipelineError("SELECTED_SOURCE_ROW_NOT_FOUND")
                        actual_platform = canonical_identifier(row.get("platform"))
                        actual_product = canonical_identifier(row.get("product_id"))
                        actual_review = canonical_identifier(row.get("review_id"))
                        actual_category = row.get("product_category") or ""
                        digest, length = content_fingerprint(row.get("content"))
                        if (
                            actual_platform != expected["platform"]
                            or actual_product != expected["product_id"]
                            or actual_review != expected["review_id"]
                            or actual_category != expected["product_category_raw"]
                            or digest != expected["normalized_content_hash"]
                            or length != expected["content_length"]
                            or expected["row_uid"] != f"{platform}:{source_row}"
                        ):
                            raise PipelineError("CSV_SQLITE_LINKAGE_MISMATCH")
                        pool_id = f"PTEXT-{written.total()+1:06d}"
                        out = {
                            "pool_id": pool_id,
                            "row_uid": expected["row_uid"],
                            "sampling_group": expected["sampling_group"],
                            "sampling_reason": expected["sampling_reason"],
                            "label_status": "UNLABELED",
                            "platform": expected["platform"],
                            "source_row": expected["source_row"],
                            "product_id": expected["product_id"],
                            "review_id": expected["review_id"],
                            "product_category_raw": expected["product_category_raw"],
                            "normalized_category": expected["normalized_category"],
                            "content": row.get("content") or "",
                            "normalized_content_hash": expected["normalized_content_hash"],
                            "content_length": expected["content_length"],
                            "duplicate_cluster_id": expected["cluster_id"] or "",
                            "candidate_sources": expected["candidate_sources"],
                            "original_candidate_member": expected["original_candidate_member"],
                            "original_control_eligible": expected["original_control_eligible"],
                            "seed": seed,
                            "policy_version": policy_version,
                        }
                        writer.writerow(out)
                        written[expected["sampling_group"]] += 1
                        expected = next(selected, None)
                if expected is not None:
                    raise PipelineError("SELECTED_SOURCE_ROW_NOT_FOUND")
                signatures_after[platform] = file_signature(path)
                if signatures_before[platform] != signatures_after[platform]:
                    raise PipelineError("RAW_CSV_CHANGED_DURING_RUN")
        with output_csv.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(block)
        expected_counts = dict(db.execute("SELECT sampling_group,COUNT(*) FROM selection GROUP BY sampling_group"))
        if dict(written) != expected_counts:
            raise PipelineError("MATERIALIZED_COUNT_MISMATCH")
        return {
            "rows": written.total(),
            "groups": dict(written),
            "csv_sha256": hasher.hexdigest(),
            "raw_signatures_before": signatures_before,
            "raw_signatures_after": signatures_after,
            "all_label_status_unlabeled": True,
            "linkage_verified": True,
        }
    finally:
        db.close()


def update_staging_report(staging_path: Path, report: dict) -> None:
    db = sqlite3.connect(staging_path)
    try:
        db.execute(
            "UPDATE run_metadata SET value=? WHERE key='selection_report'",
            (json.dumps(report, ensure_ascii=False, separators=(",", ":")),),
        )
        db.commit()
    finally:
        db.close()


def promote_staging(staging_dir: Path, output_dir: Path) -> None:
    """Atomically publish a complete directory; destination must not exist."""
    if output_dir.exists():
        raise PipelineError("FINAL_OUTPUT_PATH_ALREADY_EXISTS")
    staging_dir.rename(output_dir)


def run_pipeline(
    canonical_path: Path,
    raw_paths: dict[str, Path],
    output_dir: Path,
    targets: dict[str, int],
    seed: int,
    policy_version: str = DEFAULT_POLICY_VERSION,
    hash_cap: int = 1,
    cluster_cap: int = 1,
    product_cap: int = 2,
    *,
    enforce_git_ignore: bool = True,
) -> dict:
    validate_targets(targets)
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise PipelineError("FINAL_OUTPUT_PATH_ALREADY_EXISTS")
    if enforce_git_ignore:
        assert_git_ignored(output_dir)
    preflight = verify_raw_preflight(canonical_path, raw_paths)
    disk = check_disk_capacity(
        output_dir.parent,
        preflight["total_manifest_rows"],
        sum(targets.values()),
    )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_dir = output_dir.parent / f".{output_dir.name}.staging-{uuid4().hex}"
    if staging_dir.exists():
        raise PipelineError("STAGING_PATH_ALREADY_EXISTS")
    staging_dir.mkdir()
    staging_db = staging_dir / "selection.sqlite3"
    try:
        report = select_pool(
            canonical_path, staging_db, targets, seed, policy_version,
            hash_cap, cluster_cap, product_cap,
        )
        report["input_preflight"] = preflight
        report["disk_capacity"] = disk
        update_staging_report(staging_db, report)
        safe_json_write(staging_dir / "selection_report.json", report)
        if report["status"] != "READY":
            safe_json_write(staging_dir / "FAILURE.json", {
                "status": "INSUFFICIENT_CAPACITY",
                "targets": targets,
                "selected": report["selected"],
                "shortfalls": {group: report["groups"][group]["shortfall"] for group in targets},
            })
            return {"status": "INSUFFICIENT_CAPACITY", "staging_dir": staging_dir, "report": report}
        materialized = materialize_selected_rows(
            staging_db, raw_paths, staging_dir / "ptext_unlabeled_pool.csv", seed, policy_version
        )
        success = {
            "status": "SUCCESS",
            "seed": seed,
            "policy_version": policy_version,
            "targets": targets,
            "selected": report["selected"],
            "materialization": materialized,
            "input_preflight": preflight,
            "disk_capacity": disk,
        }
        # SUCCESS is part of the fully validated staging directory. The final
        # path appears only through the last atomic directory rename.
        safe_json_write(staging_dir / "SUCCESS.json", success)
        promote_staging(staging_dir, output_dir)
        success["output_dir"] = output_dir
        return success
    except Exception:
        # Fail closed: the uniquely named staging directory is never promoted.
        raise


def parse_targets(value: str) -> dict[str, int]:
    if value == "150k":
        return dict(DEFAULT_TARGETS)
    if value == "1k":
        return dict(PILOT_TARGETS)
    raise argparse.ArgumentTypeError("targets must be '1k' or '150k'")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a deterministic UNLABELED P_text review pool")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-name", required=True, help="new directory name under private_outputs/")
    parser.add_argument("--targets", type=parse_targets, choices=None, default=dict(DEFAULT_TARGETS))
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--policy-version", default=DEFAULT_POLICY_VERSION)
    parser.add_argument("--normalized-hash-cap", type=int, default=1)
    parser.add_argument("--duplicate-cluster-cap", type=int, default=1)
    parser.add_argument("--product-cap", type=int, default=2)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if Path(args.output_name).name != args.output_name or args.output_name in (".", ".."):
            raise PipelineError("INVALID_OUTPUT_NAME")
        raw_paths = {platform: raw_csv_path(args.raw_root, platform) for platform in PLATFORMS}
        result = run_pipeline(
            args.database,
            raw_paths,
            PRIVATE_OUTPUT_ROOT / args.output_name,
            args.targets,
            args.seed,
            args.policy_version,
            args.normalized_hash_cap,
            args.duplicate_cluster_cap,
            args.product_cap,
        )
        summary = {
            "status": result["status"],
            "selected": result.get("selected") or result["report"]["selected"],
            "automatic_labels_created": False,
        }
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if result["status"] == "SUCCESS" else 2
    except PipelineError as exc:
        print(json.dumps({"status": "FAILED", "error_code": exc.code}), file=sys.stderr)
        return 1
    except Exception:
        print(json.dumps({"status": "FAILED", "error_code": "UNEXPECTED_PIPELINE_ERROR"}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
