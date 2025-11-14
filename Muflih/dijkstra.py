import heapq

def dijkstra(n:int,edges: list[list[int]],src:int) -> dict[int,int]:

    adj ={}

    for i in range(n):
        adj[i] = []
    
    for u,v,w in edges:
        adj[u].append([v,w])


    shortest = {}   
    minHeap = [[0,src]]

    while minHeap:
        w1,n1 = heapq.heappop(minHeap)
        if n1 in shortest:
            continue
        shortest[n1] = w1

        for n2,w2 in adj[n1]:
            if n2 not in shortest:
                heapq.heappush(minHeap,[w1+w2,n2])

    for i in range(n):
            if i not in shortest:
                shortest[i] = -1

    return shortest


adj = [[0,1,4],[0,2,6],[0,3,9],[1,0,4],[1,2,1],[2,0,6],[2,1,1],[2,3,2],[3,2,2],[3,0,9]]
n = 4
src = 0

print(dijkstra(n,adj,src))