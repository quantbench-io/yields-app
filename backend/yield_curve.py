import numpy as np
import matplotlib.pyplot as plt

def linear_interpolate(x, point0, point1):
  x0,y0 = point0;
  x1,y1 = point1;
  return y0*(x1-x)/(x1-x0) + y1*(x-x0)/(x1-x0);

def log_interpolate(x, point0, point1):
  x0,y0 = point0;
  x1,y1 = point1;
  return np.exp(np.log(y0)*(x1-x)/(x1-x0) + np.log(y1)*(x-x0)/(x1-x0))

def f_interpolate(nodes, mode="linear"):
  nodes = np.array(sorted(nodes, key=lambda x: x[0]))
  nodes_x = [node[0] for node in nodes]
  nodes_y = [node[1] for node in nodes]

  def f_inter(x):
    # if x outside data range return None;
    # if x already in data range, return known y value
    if x < nodes_x[0] or x > nodes_x[-1]: return None;
    if x in nodes_x: return nodes_y[nodes_x.index(x)];

    else:
      # gets i : x \in [a_{i-1}, a_i)
      i = np.searchsorted(nodes_x, x, side="right")
      p0 = (nodes_x[i-1], nodes_y[i-1])
      p1 = (nodes_x[i], nodes_y[i])

      if mode=="linear" : return linear_interpolate(x, p0, p1)
      if mode=="log" : return log_interpolate(x, p0, p1)

  return np.vectorize(f_inter)


def R_curve(par_yields, frequency):
  nodes_tau, nodes_R = zip(*par_yields)

  tt = np.linspace(nodes_tau[0], nodes_tau[-1], frequency * nodes_tau[-1])
  R_interpl = f_interpolate(par_yields, mode="linear")
  RR = R_interpl(tt)

  return list(zip(tt, RR))


def D_bootstrap(R_t):
  # coupon_pars should be a list of (t,ρ_t)
  taus, Rvals = zip(*R_t)
  rhos = [R/2 for R in Rvals]

  rho_1 = rhos[0]
  d_factors = [1/(1+rho_1)]

  for i in range(1, len(rhos)):
    rho_i = rhos[i]  # technically this is rho_{t_{i+1}}, but no matter
    d_i = (1-rho_i*sum(d_factors[:i]))/(1+rho_i);
    d_factors.append(d_i)

  return list(zip(taus, d_factors))


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

def Zm_to_Zc(Zc_t, freq):
  # converts m-times-annually compounding rates into annual continuous zero-rates
  m = freq;
  return [(t, m*np.log(1+zm_t/m)) for t, zm_t in Zm_t]


# ===============================================

def main():
  pars=[
    # (0.125, 4.7),
    # (0.25, 4.63),
    (0.5, 4.44),
    (1.0, 4.33),
    (2.0, 4.29),
    (3.0, 4.25),
    (5.0, 4.28),
    (7.0, 4.35),
    (10.0, 4.42),
    (20, 4.7),
    (30, 4.61)
  ]
  pars = [(tau, R/100) for tau,R in pars]
  nodes_t = [t for t, r in pars]

  freq = 2

  R_t = R_curve(pars, freq)
  D_t = D_bootstrap(R_t)
  Zc_t = D_to_Zc(D_t)
  Zm_t = D_to_Zm(D_t, 12)

  print("tau,\t R_t,\t\t D_t,\t\t\t Z_t")
  print("=====================================")
  for i in range(len(D_t)):
    r = R_t[i]
    d = D_t[i]
    z = Zc_t[i]

    if r[0] in [0.5,1.0,2.0,3.0,5.0] :
      print(f"{r[0]:.3f},\t {r[1]:.4f},\t {d[1]:.7f},\t {z[1]/12:.5%}")
  print()

  # ===========================================
  # Plotting
  # xx, yy = zip(*R_t)
  #
  # xx=[12*x for x in xx] # tau -> months
  # yy=[100*y for y in yy] # percentage

  # fig, ax = plt.subplots(1,1,figsize=plt.figaspect(0.5))
  # ax.plot(xx, yy)
  # ax.set_ylim(4.10, 4.80)
  # ax.minorticks_on()
  # ax.grid(axis="y")
  # plt.show()

 0.9381868


main()