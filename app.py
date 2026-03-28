from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def _merge_log_entries(log):
    """Merge consecutive identical process entries in gantt log"""
    if not log:
        return log
    merged = [log[0]]
    for entry in log[1:]:
        if merged[-1]['id'] == entry['id']:
            merged[-1]['end'] = entry['end']
        else:
            merged.append(entry)
    return merged

def fcfs(ps):
    """First Come First Serve - Non-preemptive"""
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    
    for p in sorted(ps, key=lambda x: (x['at'], x['id'])):
        if t < p['at']:
            log.append({'id': -1, 'start': t, 'end': p['at']})
            t = p['at']
        log.append({'id': p['id'], 'start': t, 'end': t + p['bt']})
        t += p['bt']
        res[p['id']]['ct'] = t
        res[p['id']]['tat'] = t - p['at']
        res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
    
    return _merge_log_entries(log), res

def sjf(ps):
    """Shortest Job First - Non-preemptive"""
    ps2 = [{**p, 'rem': p['bt'], 'done': False} for p in ps]
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    done = 0
    
    while done < len(ps):
        avail = [p for p in ps2 if not p['done'] and p['at'] <= t]
        if not avail:
            nxt_procs = [p for p in ps2 if not p['done']]
            if not nxt_procs:
                break
            nxt = min(nxt_procs, key=lambda x: x['at'])
            log.append({'id': -1, 'start': t, 'end': nxt['at']})
            t = nxt['at']
            continue
        
        p = min(avail, key=lambda x: (x['bt'], x['at']))
        log.append({'id': p['id'], 'start': t, 'end': t + p['bt']})
        t += p['bt']
        p['done'] = True
        done += 1
        res[p['id']]['ct'] = t
        res[p['id']]['tat'] = t - p['at']
        res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
    
    return _merge_log_entries(log), res

def srtf(ps):
    """Shortest Remaining Time First - Preemptive"""
    if not ps:
        return [], {}
    
    ps2 = [{**p, 'rem': p['bt'], 'done': False, 'start_time': None} for p in ps]
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    done = 0
    max_t = sum(p['bt'] for p in ps) + max(p['at'] for p in ps) + 1
    
    while done < len(ps) and t < max_t:
        avail = [p for p in ps2 if not p['done'] and p['at'] <= t and p['rem'] > 0]
        
        if not avail:
            nxt_procs = [p for p in ps2 if not p['done'] and p['at'] > t]
            if nxt_procs:
                nxt = min(nxt_procs, key=lambda x: x['at'])
                log.append({'id': -1, 'start': t, 'end': nxt['at']})
                t = nxt['at']
            else:
                break
            continue
        
        p = min(avail, key=lambda x: (x['rem'], x['at']))
        if p['start_time'] is None:
            p['start_time'] = t
        
        log.append({'id': p['id'], 'start': t, 'end': t + 1})
        p['rem'] -= 1
        t += 1
        
        if p['rem'] == 0:
            p['done'] = True
            done += 1
            res[p['id']]['ct'] = t
            res[p['id']]['tat'] = t - p['at']
            res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
    
    return _merge_log_entries(log), res

def rr(ps, q=4):
    """Round Robin - Preemptive"""
    if not ps or q <= 0:
        return [], {}
    
    ps2 = [{**p, 'rem': p['bt'], 'done': False} for p in ps]
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    queue = []
    done = 0
    
    sorted_ps = sorted(ps2, key=lambda x: x['at'])
    si = 0
    
    # Add initial processes
    while si < len(sorted_ps) and sorted_ps[si]['at'] <= t:
        queue.append(sorted_ps[si])
        si += 1
    
    if not queue and si < len(sorted_ps):
        t = sorted_ps[si]['at']
        queue.append(sorted_ps[si])
        si += 1
    
    while done < len(ps):
        if not queue:
            nxt = next((p for p in sorted_ps if not p['done'] and p['at'] > t), None)
            if nxt:
                log.append({'id': -1, 'start': t, 'end': nxt['at']})
                t = nxt['at']
                while si < len(sorted_ps) and sorted_ps[si]['at'] <= t:
                    queue.append(sorted_ps[si])
                    si += 1
            else:
                break
            continue
        
        p = queue.pop(0)
        ex = min(q, p['rem'])
        log.append({'id': p['id'], 'start': t, 'end': t + ex})
        t += ex
        p['rem'] -= ex
        
        # Add newly arrived processes
        while si < len(sorted_ps) and sorted_ps[si]['at'] <= t:
            queue.append(sorted_ps[si])
            si += 1
        
        if p['rem'] > 0:
            queue.append(p)
        else:
            p['done'] = True
            done += 1
            res[p['id']]['ct'] = t
            res[p['id']]['tat'] = t - p['at']
            res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
    
    return _merge_log_entries(log), res

def priority_np(ps):
    """Non-preemptive Priority Scheduling"""
    ps2 = [{**p, 'done': False} for p in ps]
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    done = 0
    
    while done < len(ps):
        avail = [p for p in ps2 if not p['done'] and p['at'] <= t]
        if not avail:
            nxt_procs = [p for p in ps2 if not p['done']]
            if not nxt_procs:
                break
            nxt = min(nxt_procs, key=lambda x: x['at'])
            log.append({'id': -1, 'start': t, 'end': nxt['at']})
            t = nxt['at']
            continue
        
        p = min(avail, key=lambda x: (x['pr'], x['at']))
        log.append({'id': p['id'], 'start': t, 'end': t + p['bt']})
        t += p['bt']
        p['done'] = True
        done += 1
        res[p['id']]['ct'] = t
        res[p['id']]['tat'] = t - p['at']
        res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
    
    return _merge_log_entries(log), res

def pp(ps):
    """Preemptive Priority Scheduling"""
    if not ps:
        return [], {}
    
    ps2 = [{**p, 'rem': p['bt'], 'done': False, 'start_time': None} for p in ps]
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    done = 0
    max_t = sum(p['bt'] for p in ps) + max(p['at'] for p in ps) + 1
    
    while done < len(ps) and t < max_t:
        avail = [p for p in ps2 if not p['done'] and p['at'] <= t and p['rem'] > 0]
        
        if not avail:
            nxt_procs = [p for p in ps2 if not p['done'] and p['at'] > t]
            if nxt_procs:
                nxt = min(nxt_procs, key=lambda x: x['at'])
                log.append({'id': -1, 'start': t, 'end': nxt['at']})
                t = nxt['at']
            else:
                break
            continue
        
        p = min(avail, key=lambda x: (x['pr'], x['at']))
        if p['start_time'] is None:
            p['start_time'] = t
        
        log.append({'id': p['id'], 'start': t, 'end': t + 1})
        p['rem'] -= 1
        t += 1
        
        if p['rem'] == 0:
            p['done'] = True
            done += 1
            res[p['id']]['ct'] = t
            res[p['id']]['tat'] = t - p['at']
            res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
    
    return _merge_log_entries(log), res

def mlfq(ps):
    """Multi-Level Feedback Queue - 3 queues"""
    if not ps:
        return [], {}
    
    ps2 = [{**p, 'rem': p['bt'], 'done': False, 'level': 0} for p in ps]
    t = 0
    log = []
    res = {p['id']: {'wt': 0, 'tat': 0, 'ct': 0} for p in ps}
    qs = [[], [], []]  # 3 priority queues
    qq = [2, 4, 8]  # Time quantum for each queue
    sorted_ps = sorted(ps2, key=lambda x: x['at'])
    si = 0
    done = 0
    
    # Add initial processes to queue 0
    while si < len(sorted_ps) and sorted_ps[si]['at'] <= t:
        qs[0].append(sorted_ps[si])
        si += 1
    
    if not qs[0] and si < len(sorted_ps):
        t = sorted_ps[si]['at']
        qs[0].append(sorted_ps[si])
        si += 1
    
    max_t = sum(p['bt'] * 2 for p in ps) + max(p['at'] for p in ps) + 10
    
    while done < len(ps) and t < max_t:
        found = False
        
        for qi in range(3):
            if not qs[qi]:
                continue
            
            p = qs[qi].pop(0)
            q = qq[qi]
            ex = min(q, p['rem'])
            
            log.append({'id': p['id'], 'start': t, 'end': t + ex})
            t += ex
            p['rem'] -= ex
            
            # Add newly arrived processes to queue 0
            while si < len(sorted_ps) and sorted_ps[si]['at'] <= t:
                qs[0].append(sorted_ps[si])
                si += 1
            
            if p['rem'] > 0:
                # Demote to lower priority queue
                next_level = min(p['level'] + 1, 2)
                p['level'] = next_level
                qs[next_level].append(p)
            else:
                p['done'] = True
                done += 1
                res[p['id']]['ct'] = t
                res[p['id']]['tat'] = t - p['at']
                res[p['id']]['wt'] = res[p['id']]['tat'] - p['bt']
            
            found = True
            break
        
        if not found:
            nxt_procs = [p for p in ps2 if not p['done'] and p['at'] > t]
            if nxt_procs:
                nxt = min(nxt_procs, key=lambda x: x['at'])
                log.append({'id': -1, 'start': t, 'end': nxt['at']})
                t = nxt['at']
                while si < len(sorted_ps) and sorted_ps[si]['at'] <= t:
                    qs[0].append(sorted_ps[si])
                    si += 1
            else:
                break
    
    return _merge_log_entries(log), res

def calc_metrics(res, ps):
    """Calculate performance metrics"""
    if not ps:
        return {'avg_wt': 0, 'avg_tat': 0, 'cpu': 0, 'tp': 0}
    
    wts = [res[p['id']]['wt'] for p in ps if p['id'] in res]
    tats = [res[p['id']]['tat'] for p in ps if p['id'] in res]
    cts = [res[p['id']]['ct'] for p in ps if p['id'] in res]
    
    if not cts:
        return {'avg_wt': 0, 'avg_tat': 0, 'cpu': 0, 'tp': 0}
    
    avg_wt = sum(wts) / len(wts) if wts else 0
    avg_tat = sum(tats) / len(tats) if tats else 0
    max_ct = max(cts)
    total_bt = sum(p['bt'] for p in ps)
    cpu = (total_bt / max_ct * 100) if max_ct > 0 else 0
    tp = (len(ps) / max_ct) if max_ct > 0 else 0
    
    return {
        'avg_wt': round(avg_wt, 2),
        'avg_tat': round(avg_tat, 2),
        'cpu': round(cpu, 1),
        'tp': round(tp, 3)
    }

@app.route('/')
def index():
    return send_file(os.path.join(os.path.dirname(__file__), 'index.html'))

@app.route('/api/schedule', methods=['POST'])
def schedule():
    data = request.json
    algo_name = data.get('algorithm', 'fcfs')
    procs = data.get('processes', [])
    q = data.get('quantum', 4)
    
    if not procs:
        return jsonify({'gantt_log': [], 'results': {}, 'metrics': {}})
    
    if algo_name == 'fcfs':
        log, res = fcfs(procs)
    elif algo_name == 'sjf':
        log, res = sjf(procs)
    elif algo_name == 'srtf':
        log, res = srtf(procs)
    elif algo_name == 'rr':
        log, res = rr(procs, q)
    elif algo_name == 'priority':
        log, res = priority_np(procs)
    elif algo_name == 'pp':
        log, res = pp(procs)
    elif algo_name == 'mlfq':
        log, res = mlfq(procs)
    else:
        log, res = fcfs(procs)
    
    metrics = calc_metrics(res, procs)
    return jsonify({'gantt_log': log, 'results': res, 'metrics': metrics})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
