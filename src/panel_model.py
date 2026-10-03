"""Cox model with early/late effects for covariates violating proportional hazards.

The spell is split at `cut` years: covariates in `nph` get one hazard ratio before
the cut (`v`) and a multiplicative change after it (`v_x_late`). The model is fitted
with CoxPHFitter(entry_col='entry'), so the late rows are left-truncated at `cut`.
"""
import numpy as np
import pandas as pd


def split_early_late(df, cut, nph, duration_col='duration', event_col='event'):
    """Split each spell into [0, cut] and (cut, duration] and add `v_x_late` terms."""
    early = df.copy()
    early['entry'] = 0.0
    early['late'] = 0.0
    early.loc[early[duration_col] > cut, event_col] = 0
    early[duration_col] = early[duration_col].clip(upper=cut)

    late = df[df[duration_col] > cut].copy()
    late['entry'] = float(cut)
    late['late'] = 1.0

    out = pd.concat([early, late]).reset_index(drop=True)
    for v in nph:
        out[f"{v}_x_late"] = out[v] * out['late']
    return out.drop(columns='late')


def late_hazard_ratios(model, nph):
    """Hazard ratio of each `nph` covariate before and after the cut, with 95% CI."""
    V = model.variance_matrix_
    rows = []
    for v in nph:
        inter = f"{v}_x_late"
        b_early = model.params_[v]
        b_late = b_early + model.params_[inter]
        se_early = np.sqrt(V.loc[v, v])
        se_late = np.sqrt(V.loc[v, v] + V.loc[inter, inter] + 2 * V.loc[v, inter])
        for period, b, se in [('early', b_early, se_early), ('late', b_late, se_late)]:
            rows.append({
                'covariate': v, 'period': period, 'HR': np.exp(b),
                'lower 95%': np.exp(b - 1.96 * se), 'upper 95%': np.exp(b + 1.96 * se),
            })
    return pd.DataFrame(rows).set_index(['covariate', 'period'])


def predict_survival(model, profile, times, cut, nph):
    """Survival probability at `times` (years in power) for one covariate profile.

    `profile` maps each base covariate (without `_x_late` terms) to its value.
    The profile's early risk applies up to `cut`, its late risk afterwards.
    """
    x = pd.DataFrame([profile], dtype=float)
    early, late = x.copy(), x.copy()
    for v in nph:
        early[f"{v}_x_late"] = 0.0
        late[f"{v}_x_late"] = x[v]
    cols = model.params_.index
    risk_early = float(model.predict_partial_hazard(early[cols]).iloc[0])
    risk_late = float(model.predict_partial_hazard(late[cols]).iloc[0])

    H0 = model.baseline_cumulative_hazard_.iloc[:, 0]

    def H0_at(t):
        before = H0[H0.index <= t]
        return float(before.iloc[-1]) if len(before) else 0.0

    H0_cut = H0_at(cut)
    surv = []
    for t in np.atleast_1d(times):
        H0_t = H0_at(t)
        if t <= cut:
            H = risk_early * H0_t
        else:
            H = risk_early * H0_cut + risk_late * (H0_t - H0_cut)
        surv.append(np.exp(-H))
    return pd.Series(surv, index=np.atleast_1d(times), name='survival')
