import ray
import time

import data as dt
import countryprocessor as cp
import paramprocessor as pp

def printx(y, x, s): 
    print(' ' * x, s)
    return

def apply_filter(workload, filter_list):
    del_list = list()
    for ct, data in workload.items():
        if ct not in filter_list:
            del_list.append(ct)

    for i in del_list:
        del workload[i]

def submit_work(workload, filter_list, workerlist, paramp, work_todo, chunk):
    qnt = 0
    for ct, data in sorted(workload.items(), key=lambda x: x[1]['ACCASES']):
        print(f'Submiting {ct}')
        wid = cp.process_country.remote(ct, data['DATA'], data['DATE'], paramp, work_todo)
        workerlist.append(wid)
        del workload[ct]
        qnt += 1
        if qnt >= chunk:
            break
    return qnt


def main():
    ray.init(address='10.155.1.10:6379', redis_password='dc')
    ray.timeline(filename="timeline.json")

    start_time = time.time()

    var_names = ['beta', 'theta', 'p', 'sigma', 'rho', 'epsilonA', 'epsilonI',
        'lambda0', 'gammaA', 'gammaI', 'gammaD', 'cD', 'dD', 'dI', 'delta',
        'S0', 'R0', 'Q0', 'E0', 'A0', 'I0', 'D0', 'day']

    paramp = pp.ParamProcessor.remote('memory-edo', var_names)

    workload = dt.build_database(False)

    workerlist = list()

    cpu = 0
    for node in ray.nodes():
        cpu += int(node['Resources']['CPU'])


    filter_list = ['Distrito_Federal', 'Goias', 'Sao_Paulo', 'Egypt', 'Ethiopia', 'France',
 'Guatemala', 'Japan', 'Kuwait', 'Libya', 'Malawi',  'Mauritania', 'Nepal', 'Switzerland', 'Venezuela']
    #filter_list = dt.brasilian_regions()
    #filter_list = workload.keys()

    apply_filter(workload, filter_list)

    print(f'Workload is {len(workload)}')

    work_chunk = submit_work(workload, filter_list, workerlist, paramp, [0,1,2,3,4,5,6,7,9], cpu+4)

    print(f'Submitting {work_chunk} tasks ({len(workload)}/{len(workerlist)} to go).')
    
    check_size = 4

    with open('log/processed.log', 'w') as f:
        loops = 0
        while len(workerlist) > 0:
            num_returns = check_size if len(workerlist) >= check_size else len(workerlist)
            ready, not_ready = ray.wait(workerlist, num_returns=num_returns)

            done = ray.get(ready)
            printx(3, 0, f'Iteration             : {loops}')
            printx(4, 0, f'Ready length, regions : {len(ready)}')
            printx(5, 0, f'Not Ready length      : {len(not_ready)}')
            printx(5, 0, f'Workload              : {len(workload)}')
            printx(4,40, 'Ready List')
            for pos, i in enumerate(done):
                printx(5+pos,40, f'{i}')
            elapsed_time = time.time() - start_time
            stetime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            printx(7, 0, f'Elapsed time          : {stetime}')

            for nct in done:
                f.write(f'{nct}\n')

            workerlist = not_ready

            if len(workerlist) < cpu:
                submit_work(workload, filter_list, workerlist, paramp, [0,1,2,3,4,5,6,7,9], cpu - len(workerlist))
            f.flush()
            time.sleep(15)
            loops += 1

    elapsed_time = time.time() - start_time
    stetime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    print(f'Loops to process = {loops} in {stetime}.')

    paramp.dump.remote('log/param.csv')

    return


if __name__ == "__main__":
    main()
