import numpy as np

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


    def _f(t):
        assert nodes_t[0] <= t <= nodes_t[-1], "Cannot interpolate outside known input range"

        # if t already in data range, return known x value
        if t in nodes_t: return nodes_x[nodes_t.index(t)];

        else:
            # gets i : t \in [a_{i-1}, a_i)
            i = np.searchsorted(nodes_t, t, side="right")
            p0 = (nodes_t[i-1], nodes_x[i-1])
            p1 = (nodes_t[i], nodes_x[i])
            return interpolate_p(t, p0, p1, mode)

    return np.vectorize(_f)

def interpolate(nodes, mode="linear", step=1/2):
    t_min, t_max = nodes[0][0], nodes[-1][0]
    n_samples = int(round((t_max - t_min)/(step))+1)
    tt = np.linspace(t_min, t_max, n_samples)
    xx = interpolate_f(nodes, mode)(tt)

    return list(zip(tt, xx))

def interpolate_C(par_nodes, mode="linear"):
    nodes_short = list(filter(lambda x : x[0] <= 0.5, par_nodes))
    CC_short = interpolate(nodes_short, mode, step=1/12)

    nodes_long = list(filter(lambda x : x[0] >= 0.5, par_nodes))
    CC_long = interpolate(nodes_long, mode, step=1/2)

    # take [:-1] since both have a point for t=0.5
    return [*CC_short[:-1], *CC_long]

# ===============================================
def bootstrap_P_from_C(C_t, freq=2):
    # C_t should be a list of (t,c_t)
    m = freq # to make formulas easier to read

    _err = "Coupon rates should be decimals (vs. percents), did you forget to multiply by 1/100?"
    assert all(c < 1.0 for _, c in C_t), _err

    C_short = list(filter(lambda x : x[0] <= 0.5, C_t))
    C_long = list(filter(lambda x : x[0] >= 0.5, C_t))

    # easy to compute these
    P_short = [(t, 1/(1+C*t)) for t, C in C_short]

    t_0 = C_long[0][0]
    C_0 = C_long[0][1]
    P_long = [(t_0, 1/(1+C_0/m))] # this is (0.5,...)

    for i in range(1, len(C_long)):
        t_i, C_i = C_long[i] # technically these are t_{i+1} is C_{t_{i+1}}, but no matter
        p_sum = sum(p for _, p in P_long[:i])
        p_i = (1 - (C_i/m)*p_sum)/(1 + (C_i/m));
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
    PREC = 15 # lets us avoid time-input rounding errors

    C_nodes = [(t, C/100) for t, C in par_nodes] # percent -> decimal
    C_t = interpolate_C(C_nodes, mode="linear")

    P_bootstrap = bootstrap_P_from_C(C_t, freq)

    # making sure that the times for our nodes align with the original
    # times from par_nodes (rounding to avoid floating-point discrepancies)
    _t_list = [round(t, 15) for t, _ in par_nodes]

    P_nodes = [(t, p) for t, p in P_bootstrap if round(t,15) in _t_list]
    P_t = interpolate(P_nodes, mode="log", step=1/12) # for plotting "continuous zero curve"

    Z_nodes = P_to_Zc(P_nodes)
    Z_t = P_to_Zc(P_t)

    # decimal -> percent
    # =============
    C_nodes = [(round(t,PREC), 100*C) for t, C in C_nodes]
    C_t = [(round(t,PREC),100*C) for t, C in C_t]
    #   Prices P do not "correspond" to percents
    Z_nodes = [(round(t,PREC), 100*z) for t, z in Z_nodes]
    Z_t = [(round(t,PREC), 100*z) for t, z in Z_t]

    return C_nodes, C_t, P_nodes, Z_nodes, Z_t