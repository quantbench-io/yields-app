from src.backend.tools import *

nodes = {'2024-11-18': [(0.08333333333333333, 4.7),
  (0.16666666666666666, 4.65),
  (0.25, 4.63),
  (0.3333333333333333, 4.52),
  (0.5, 4.44),
  (1.0, 4.33),
  (2.0, 4.29),
  (3.0, 4.25),
  (5.0, 4.28),
  (7.0, 4.35),
  (10.0, 4.42),
  (20.0, 4.7),
  (30.0, 4.61)]
}

def lprint(l):
    for x in l:
        print(x)

def main():
    par_nodes = nodes['2024-11-18']

    R_t, P_t, Z_t, Z_log_perc = zeros_from_par_nodes(par_nodes, freq=2)

    for i in range(len(par_nodes)):
        t = par_nodes[i][0]
        R = par_nodes[i][1]
        P = P_t[i][1]
        Z = Z_t[i][1]
        print(f"{t:.3f},\t {R:.3}%,\t {P:.3},\t {Z:.3}%")
    print()
    print(len(Z_log_perc))

if __name__ == "__main__":
    main()