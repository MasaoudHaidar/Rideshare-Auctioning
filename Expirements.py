from Simulation import run
from util import mean, stddev

def main():
    n_sims = int(input("Number of sims:"))
    strategy_driver = int(input("1 for strategy driver, 0 for diverse drivers:"))
    strategy_driver = strategy_driver > 0
    all_results = dict()
    all_revenues = []
    for i in range(n_sims):
        cur_revenue, cur_results = run(strategy_driver)
        all_revenues.append(cur_revenue)
        if i == 0:
            for k, v in cur_results.items():
                all_results[k] = [v]
        else:
            for k, v in cur_results.items():
                all_results[k].append(v)
    print(f"Mean Revenue (STDDEV): {mean(all_revenues)} ({stddev(all_revenues)})")
    for k, v in all_results.items():
        cur_money = [x[0] for x in v]
        cur_time = [x[1] for x in v]
        cur_rate = [x[2] for x in v]
        print(f"Current Driver: {k}")
        print(f"Mean Money (STDDEV): {mean(cur_money)} ({stddev(cur_money)})")
        print(f"Mean Time (STDDEV): {mean(cur_time)} ({stddev(cur_time)})")
        print(f"Mean Rate (STDDEV): {mean(cur_rate)} ({stddev(cur_rate)})")

main()