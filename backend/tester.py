from backend.tools import *

# 11/18/24
par_yields = [
    (1/12, 4.7),
    (0.25, 4.63),
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



# ===============================================
def main():

    # freq=2
    # nodes = [(t, R/100) for t, R in par_yields]
    # nodes_t = [t for t, r in nodes]
    #
    # R_t = interpolate_R(nodes, freq)
    # D_t = bootstrap_D_from_R(R_t, freq)

    R_t, D_t = bootstrap_D_from_par_yields(par_yields, freq=2, returnR=True, percentize=True)

    Zc_t = D_to_Zc(D_t)
    Zm_t = D_to_Zm(D_t, 12)



    print("tau,\t R_t,\t\t D_t,\t\t\t Zm_t")
    print("=====================================")
    for i in range(len(D_t)):
        r = R_t[i]
        d = D_t[i]
        z = Zm_t[i]

        if r[0] in [0.5,1.0,2.0,3.0,5.0] :
            print(f"{r[0]:.3f},\t {r[1]:.4f},\t {d[1]:.7f},\t {z[1]/12:.5%}")
    print()


# ===============================================
if __name__ == "__main__":
    main()