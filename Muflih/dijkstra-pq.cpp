#include <bits/stdc++.h>
using namespace std;

vector<int> dijkstra(int V,vector<pair<int,int>> adj[],int S){

    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
    vector<int> dist(V);
    for (int i=0;i<V;i++) dist[i] = 1e9;

    dist[S] = 0;
    pq.push({0,S});

    while (!pq.empty()){
        int dis = pq.top().first;
        int node = pq.top().second;
        pq.pop();

        for(auto it:adj[node]){
            int edgeWeight = it.second;
            int adjNode = it.first;

            if (dis + edgeWeight < dist[adjNode]){
                dist[adjNode] = dis + edgeWeight;
                pq.push({dist[adjNode],adjNode});
            }
        }
    }
    return dist;
}

int main() {
    int V = 5;
    vector<pair<int,int>> adj[V];

    // Example edges (u, v, weight)
    adj[0].push_back({1, 2});
    adj[0].push_back({4, 1});
    adj[1].push_back({2, 3});
    adj[4].push_back({2, 2});
    adj[2].push_back({3, 6});

    vector<int> res = dijkstra(V, adj, 0);

    for (int i = 0; i < V; i++) cout << res[i] << " ";
}
