import sqlite3

def main():
    conn = sqlite3.connect("db01")
    cur = conn.cursor()

    # note: cur.execute is more like an 'initialized iterator' for your query. It doesn't actually pull the data
    # until you do something like `cur.fetchall()` or `cur.fetchone()` or `cur.fetchmany()` (??).
    # this prevents something like trying to pull in a list of millions of entries all at once.
    # cur.execute("SELECT * FROM pars202411 WHERE age > ?", (18,))
    cur.execute("SELECT * FROM pars202411")

    row = cur.fetchone()
    print(type(row))
    print(type(row[0]), "\t", type(row[1]))

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()