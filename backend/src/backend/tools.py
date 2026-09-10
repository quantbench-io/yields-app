import numpy as np

def linear_interpolate(x, point0, point1):
    x0,y0 = point0;
    x1,y1 = point1;
    return y0*(x1-x)/(x1-x0) + y1*(x-x0)/(x1-x0);

def log_interpolate(x, point0, point1):
    x0,y0 = point0;
    x1,y1 = point1;
    return np.exp(np.log(y0)*(x1-x)/(x1-x0) + np.log(y1)*(x-x0)/(x1-x0))

def interpolate_f(nodes, mode):
    nodes = np.array(sorted(nodes, key=lambda x: x[0]))
    nodes_x = [node[0] for node in nodes]
    nodes_y = [node[1] for node in nodes]

    if mode=="lin":
        def _f(x):
            # if x outside data range return None;
            # if x already in data range, return known y value
            if x < nodes_x[0] or x > nodes_x[-1]: return None;
            if x in nodes_x: return nodes_y[nodes_x.index(x)];

            else:
                # gets i : x \in [a_{i-1}, a_i)
                i = np.searchsorted(nodes_x, x, side="right")
                p0 = (nodes_x[i-1], nodes_y[i-1])
                p1 = (nodes_x[i], nodes_y[i])
                return linear_interpolate(x, p0, p1)

    if mode=="log" :
        def _f(x):
            # if x outside data range return None;
            # if x already in data range, return known y value
            if x < nodes_x[0] or x > nodes_x[-1]: return None;
            if x in nodes_x:
                return nodes_y[nodes_x.index(x)];

            else:
                # gets i : x \in [a_{i-1}, a_i)
                i=np.searchsorted(nodes_x, x, side="right")
                p0=(nodes_x[i-1], nodes_y[i-1])
                p1=(nodes_x[i], nodes_y[i])
                return log_interpolate(x, p0, p1)

    return np.vectorize(_f)


def interpolate_R(par_yields, freq, mode):

    t_short, t_long = [], []
    for t, R in par_yields :
        if t <= 0.5 : t_short.append(t)
        elif t >= 0.5 : t_long.append(t) # convenient to keep 0.5 in both

    tt_short = np.arange(1/12, 1/2, 1/12)
    tt_long = np.linspace(0.5, int(t_long[-1]), int(freq*t_long[-1]))
    tt = [*tt_short, *(tt_long[1:])]

    R_interpolate = interpolate_f(par_yields, mode)
    RR = R_interpolate(tt)

    return list(zip(tt, RR))


# ===============================================
# for "continuous" monthly zero
def log_interpolate_Dm(D_t):
    nodes_t, _ = zip(*D_t)

    t_last = int(np.floor(nodes_t[-1]+0.01)) # to avoid rounding error
    tt = np.linspace(1/12, t_last, 12*t_last)

    D_inter = interpolate_f(D_t, mode="log")
    DD = D_inter(tt)

    return list(zip(tt, DD))

# ===============================================
# for "continuous" monthly zero
def lin_interpolate_Dm(D_t):
    nodes_t, _ = zip(*D_t)

    t_last = int(np.floor(nodes_t[-1]+0.01)) # to avoid rounding error
    tt = np.linspace(1/12, t_last, 12*t_last)

    D_inter = interpolate_f(D_t, mode="lin")
    DD = D_inter(tt)

    return list(zip(tt, DD))


# ===============================================
def bootstrap_D_from_R(R_t, freq):
    # R_t should be a list of (t,ρ_t)
    # freq is the number of coupon payments per year.

    R_short, R_long = [], []
    for t, R in R_t :
        if t <= 0.5 : R_short.append((t,R))
        if t >= 0.5 : R_long.append((t,R)) # convenient to keep (0.5, R_{0.5})

    # easy to compute these
    D_short = [(t, 1/(1+R*t)) for t, R in R_short]

    rho_long = [(t, R/freq) for t,R in R_long]

    D_long = [(rho_long[0][0], 1/(1+rho_long[0][1]))] # is this (0.5,...)

    for i in range(1, len(rho_long)):
        t_i, rho_i = rho_long[i] # technically these are t_{i+1} is rho_{t_{i+1}}, but no matter
        d_sum = sum(d for t,d in D_long[:i])
        d_i = (1-rho_i*d_sum)/(1+rho_i);
        D_long.append((t_i,d_i))

    return [*D_short, *(D_long[1:])]


# ===============================================
# conversions of discounts to zero rates

def D_to_Zc(D_t):
    # convert discounts to annually continuous compounding zero rates
    return [(t, -(1/t)*np.log(d_t)) for t, d_t in D_t]

def D_to_Zm(D_t, freq):
    # convert discounts to m-times-annually compounding zero rates
    m = freq;
    return [(t, m*(d_t**(-1/(m*t))-1)) for t, d_t in D_t]

def Zc_to_Zm(Zc_t, freq):
    # converts annual continuous zero-rates into m-times-annually compounding
    m = freq;
    return [(t, m*(np.exp(zc_t/m)-1)) for t, zc_t in Zc_t]

def Zm_to_Zc(Zm_t, freq):
    # converts m-times-annually compounding rates into annual continuous zero-rates
    m = freq;
    return [(t, m*np.log(1+zm_t/m)) for t, zm_t in Zm_t]


# ===============================================
# the "main" functions
def bootstrap_D_from_par_yields(par_nodes, freq=2, returnR=False, percentize=True):
    # freq is the number of coupon payments per year.
    if percentize:
        nodes = [(t, R/100) for t, R in par_nodes]

    nodes_t = [t for t, r in nodes]

    R_t = interpolate_R(nodes, freq, mode="lin")
    D_t = bootstrap_D_from_R(R_t, freq)

    if returnR : return R_t, D_t
    else : return D_t

# nice wrapper for the main logic
def zeros_from_pars(par_yields, freq=2):
    R_t, D_t = bootstrap_D_from_par_yields(
        par_yields, freq, returnR=True, percentize=True
    )

    # conversions and interpolations
    _t = [t for t, _ in par_yields]
    D_nodes = [(t, d) for t, d in D_t if t in _t]

    Z_nodes = D_to_Zc(D_nodes)
    Z_nodes = [(t,100*z) for t,z in Z_nodes] # percent

    # for plotting "continuous zero curve"
    D_log = log_interpolate_Dm(D_nodes)
    Z_log = D_to_Zc(D_log)
    Z_log = [(t,100*z) for t,z in Z_log] # percent

    return D_nodes, Z_nodes, Z_log