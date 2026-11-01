from scripts.audit_10k_quota_bottlenecks import State, choose, select_with_attribution


def row(uid, product, cluster=None, category="A", platform="p", text=None):
    return {"row_uid": uid, "platform": platform, "product_id": product,
            "normalized_category": category, "normalized_content_hash": text or uid,
            "cluster_id": cluster}


def config(**updates):
    value = {"product_cap": 2, "cluster_cap": 1, "text_cap": 1, "ordering": "round_robin"}
    value.update(updates); return value


def test_sequential_attribution_sums_to_unfilled_without_double_counting():
    state = State(); state.used.add("used")
    state.products[("p", "full")] = 2
    rows = [row("used", "x"), row("product", "full"), row("cluster1", "c1", "dup", text="h"), row("cluster2", "c2", "dup", text="h"), row("ok", "c3")]
    selected, diagnostic = select_with_attribution("source", rows, 5, state, config())
    losses = diagnostic["sequential_loss_attribution"]
    assert diagnostic["selected"] == len(selected)
    assert sum(losses.values()) == diagnostic["unfilled"]
    assert losses["row_uid_collision"] >= 1
    assert losses["product_cap"] >= 1


def test_product_cap_sensitivity_is_monotonic_for_same_pool():
    rows = [row(f"r{i}", "same") for i in range(6)]
    counts = [len(choose(rows, 6, State(), cap, None, None, "round_robin")) for cap in (1,2,3,5)]
    assert counts == [1,2,3,5]


def test_cluster_and_text_caps_are_separately_configurable():
    rows = [row("a", "p1", "cluster", text="hash"), row("b", "p2", "cluster", text="hash")]
    assert len(choose(rows, 2, State(), None, 1, 2, "round_robin")) == 1
    assert len(choose(rows, 2, State(), None, 2, 1, "round_robin")) == 1
    assert len(choose(rows, 2, State(), None, 2, 2, "round_robin")) == 2


def test_round_robin_changes_order_but_does_not_reject_rows_without_caps():
    rows = [row("a1", "p1", category="A"), row("a2", "p2", category="A"), row("b1", "p3", category="B")]
    assert len(choose(rows, 3, State(), None, None, None, "round_robin")) == 3
    assert len(choose(rows, 3, State(), None, None, None, "flat")) == 3
