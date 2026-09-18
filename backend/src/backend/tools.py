import numpy as np
from decimal import Decimal
#############################
# PRECISION
#
# In some of our interpolations we want to avoid float/rounding trouble with the inputs, so we
# use Python's `decimal.Decimal` class for better precision-control. For our purposes
# here, rounding to 15 decimal places is fine for now.
# 10**(-15) * (365*24*60*60) = 3.1536e-08, so ~30 nanoseconds.

PREC = 17 # decimal places to round to
EPS = Decimal(str(10**(-PREC))) # "epsilon", our precision cutoff

def sharp_interval(a, b, *, step=None, samples=None, out_type='float'):
    """
    Makes a "precise" sequence of evenly spaced points between (and including) `a` and `b`.
    `out_type` can be either 'float' (default) or 'decimal'.
    """
    assert (step is None) or (samples is None), "Have to use either `step` or `samples`, and not both."

    # re-casting to be certain
    A = Decimal(str(a))
    B = Decimal(str(b))

    if step is not None:
        STEP = Decimal(str(step))
        samples = int(round((B-A)/STEP)+1)
        intv = np.linspace(A, B, samples)

    if samples is not None:
        samples = int(samples)
        intv = np.linspace(A, B, samples)

    diffs = [(intv[i]-intv[i-1]).quantize(EPS) for i in range(1, len(intv))]
    assert all(dif == diffs[0] for dif in diffs), "Uneven interval sizes"

    if out_type == 'decimal' :
        assert (A in intv) and (B in intv), "Trouble with endpoints of interval"
        return intv
    elif out_type == 'float' :
        intv = np.array([float(x.quantize(EPS)) for x in intv])
        a = float(A.quantize(EPS))
        b = float(B.quantize(EPS))
        assert (float(a) in intv) and (float(b) in intv), "Trouble with endpoints of interval"
        return intv
    else:
        raise TypeError("out_type must be either 'float' (default) or 'decimal'.")

# ====================================================

def interpolate_p(t, point0, point1, mode):
    t0, x0 = point0;
    t1, x1 = point1;
    lambd = (t-t0)/(t1-t0); # lambda

    if mode == "linear" :
        return (1-lambd)*x0 + lambd*x1
    if mode == "log" :
        return np.exp((1-lambd)*np.log(x0) + lambd*np.log(x1))

def interpolate_f(nodes, mode):
    """
    Return a function which interpolates values based on `nodes`
    :param nodes:
        List of points to interpolate values with.
        Can be list of tuples (t,x) or list of lists [t,x]
    :param mode:
        Interpolation method to use.
        Currently only supports modes "linear" and "log".
    :return:
        Function built by interpolating values using `nodes`.
    """
    nodes = np.array(sorted(nodes, key=lambda x: x[0]))
    nodes_t = [node[0] for node in nodes]
    nodes_x = [node[1] for node in nodes]

    if mode=="linear":
        def _f(t):
            assert nodes_t[0] <= t <= nodes_t[-1], "Cannot interpolate outside known input range"

            # if t already in data range, return known x value
            if t in nodes_t: return nodes_x[nodes_t.index(t)];

            else:
                # gets i : t \in [a_{i-1}, a_i)
                i = np.searchsorted(nodes_t, t, side="right")
                p0 = (nodes_t[i-1], nodes_x[i-1])
                p1 = (nodes_t[i], nodes_x[i])
                return interpolate_p(t, p0, p1, mode="linear")

    if mode=="log" :
        def _f(t):
            assert nodes_t[0] <= t <= nodes_t[-1], "Cannot interpolate outside known input range"

            # if x already in data range, return known y value
            if t in nodes_t:
                return nodes_x[nodes_t.index(t)];

            else:
                # gets i : t \in [a_{i-1}, a_i)
                i=np.searchsorted(nodes_t, t, side="right")
                p0=(nodes_t[i-1], nodes_x[i-1])
                p1=(nodes_t[i], nodes_x[i])
                return interpolate_p(t, p0, p1, mode="log")

    return np.vectorize(_f)

def interpolate_R(par_nodes, freq, mode):
    t_min = par_nodes[0][0];
    tt_short = sharp_interval(t_min, 1/2, step=1/12) # gets an evenly spaced interval

    t_max = par_nodes[-1][0];
    tt_long = sharp_interval(0.5, t_max, step=1/freq)

    tt = [*tt_short[:-1], *tt_long] # [-1] to remove the duplicate 1/2

    # for `interpolate_f` to work properly, we want `tt` and the `par_nodes` to have the same time precision
    par_nodes = [(round(t, PREC), r) for t, r in par_nodes]
    assert all(t in tt for t, r in par_nodes), "t-range `tt` does not match times in rounded-time-`par_nodes`"

    _R = interpolate_f(par_nodes, mode)
    RR = _R(tt)

    return list(zip(tt, RR))

# ===============================================
# for "continuous" monthly zero
def interpolate_monthly_P(P_t, mode):
    nodes_t, _ = zip(*P_t)

    t_min = nodes_t[0]
    t_max = nodes_t[-1]
    tt = sharp_interval(t_min, t_max, step=1/12)

    P_t = [(round(t, PREC), p) for t, p in P_t]

    _P = interpolate_f(P_t, mode)
    PP = _P(tt)

    return list(zip(tt, PP))

# ===============================================
def bootstrap_P_from_R(R_t, freq=2):
    # R_t should be a list of (t,ρ_t)
    # freq is the number of coupon payments per year.

    _err = "Coupon rates should be decimals (vs. percents), did you forget to multiply by 1/100?"
    assert all(r < 1.0 for _, r in R_t), _err

    R_short, R_long = [], []
    for t, R in R_t :
        if t <= 0.5 : R_short.append((t,R))
        if t >= 0.5 : R_long.append((t,R)) # convenient to keep (0.5, R_{0.5})

    # easy to compute these
    P_short = [(t, 1/(1+R*t)) for t, R in R_short]

    rhos = [(t, R/freq) for t, R in R_long] # per-period coupon payment
    P_long = [(rhos[0][0], 1/(1+rhos[0][1]))] # this is (0.5,...)

    for i in range(1, len(rhos)):
        t_i, rho_i = rhos[i] # technically these are t_{i+1} is rho_{t_{i+1}}, but no matter
        p_sum = sum(p for _, p in P_long[:i])
        p_i = (1 - rho_i*p_sum)/(1 + rho_i);
        P_long.append((t_i, p_i))

    return [*P_short[:-1], *P_long]


# ===============================================
# conversions of discounts to zero rates

def P_to_Zc(P_t):
    # convert discounts to annual continuous compounding zero-rates
    return [(t, -(1/t)*np.log(p_t)) for t, p_t in P_t]

def P_to_Zm(P_t, freq):
    # convert discounts to m-times-annually compounding zero-rates
    m = freq;
    return [(t, m*(p_t**(-1/(m*t))-1)) for t, p_t in P_t]

def Zc_to_Zm(Zc_t, freq):
    # converts annual continuous zero-rates into m-times-annually compounding
    m = freq;
    return [(t, m*(np.exp(zc_t/m)-1)) for t, zc_t in Zc_t]

def Zm_to_Zc(Zm_t, freq):
    # converts m-times-annually compounding rates into annual continuous zero-rates
    m = freq;
    return [(t, m*np.log(1+zm_t/m)) for t, zm_t in Zm_t]


# nice wrapper for the main logic
def zeros_from_par_nodes(par_nodes, freq=2):
    # percent -> decimals
    R_nodes = [(round(t, PREC), R/100) for t, R in par_nodes]
    nodes_t = [t for t, _ in R_nodes]

    R_t = interpolate_R(R_nodes, freq, mode="linear")
    P_bootstrap = bootstrap_P_from_R(R_t, freq)

    # making sure that the times for our nodes align with
    # the original times from par_nodes
    t_list = [t for t, _ in P_bootstrap]
    assert all(t in t_list for t in nodes_t), "Mismatched times"

    P_nodes = [(t, p) for t, p in P_bootstrap if t in nodes_t]
    Z_nodes = P_to_Zc(P_nodes)

    # for plotting "continuous zero curve"
    P_t = interpolate_monthly_P(P_nodes, mode="log")
    Z_t = P_to_Zc(P_t)

    # decimal -> percent
    # =============
    R_nodes = [(t, 100*R) for t, R in R_nodes]
    R_t = [(t,100*R) for t, R in R_t]
    #   Prices P do not "correspond" to percents
    Z_nodes = [(t, 100*z) for t, z in Z_nodes]
    Z_t = [(t, 100*z) for t, z in Z_t]

    return R_nodes, R_t, P_nodes, Z_nodes, Z_t