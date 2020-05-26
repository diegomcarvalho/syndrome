import ray
import time

import data as dt
import countryprocessor as cp
import paramprocessor as pp

import curses

def main():
    ray.init(address='10.155.1.10:6379', redis_password='dc')
    ray.timeline(filename="timeline.json")

    start_time = time.time()

    paramp = pp.ParamProcessor.remote()

    workload = dt.build_database()

    workerlist = list()

    filter_list = ['Brasil', 'Santa_Catarina','Alagoas', 'Minas_Gerais', 'Espirito_Santo', 'Tocantins', 'Afghanistan', 'Distrito_Federal']
    #filter_list = dt.brasilian_regions()
    #filter_list = workload.keys()

    for ct, data in sorted(workload.items(), key=lambda x: x[1]['ACCASES']):
        if ct in filter_list:
            print(f'Submiting {ct}')
            wid = cp.process_country.remote(ct, data['DATA'], data['DATE'], paramp)
            workerlist.append(wid)
    
    screen = curses.initscr()
    with open('log/processed.log', 'w') as f:
        loops = 0
        while len(workerlist) > 0:
            num_returns = 8 if len(workerlist) >= 8 else len(workerlist)
            ready, not_ready = ray.wait(workerlist, num_returns=num_returns)

            done = ray.get(ready)
            screen.clear()
            screen.addstr(3, 0, f'Iteration             : {loops}')
            screen.addstr(4, 0, f'Ready length, regions : {len(ready)}')
            screen.addstr(5, 0, f'Not Ready length      : {len(not_ready)}')
            screen.addstr(4,40, 'Ready List')
            for pos, i in enumerate(done):
                screen.addstr(5+pos,40, f'{i}')
            elapsed_time = time.time() - start_time
            stetime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            screen.addstr(7, 0, f'Elapsed time          : {stetime}')
            screen.refresh()

            for nct in done:
                f.write(f'{nct}\n')

            workerlist = not_ready
            time.sleep(15)
            loops += 1

    curses.endwin()

    elapsed_time = time.time() - start_time
    stetime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    print(f'Loops to process = {loops} in {stetime}.')

    paramp.dump.remote('log/param.csv')

    return


if __name__ == "__main__":
	main()
