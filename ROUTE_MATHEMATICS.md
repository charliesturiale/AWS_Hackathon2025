# SafePath SF - Route Calculation Mathematics

## 📐 Mathematical Foundation for Safe Route Planning

### Table of Contents
1. [Core Algorithm Overview](#core-algorithm-overview)
2. [Safety Score Calculation](#safety-score-calculation)
3. [Route Optimization](#route-optimization)
4. [Graph Theory Implementation](#graph-theory-implementation)
5. [Machine Learning Models](#machine-learning-models)
6. [Time-Safety Trade-off](#time-safety-trade-off)

---

## Core Algorithm Overview

SafePath SF uses a modified **A* (A-star)** pathfinding algorithm that optimizes for both safety and efficiency. Unlike traditional navigation that minimizes distance or time, we minimize a composite risk function.

### Base Cost Function
```
f(n) = g(n) + h(n) + s(n)
```
Where:
- `f(n)` = Total cost of node n
- `g(n)` = Distance from start to node n
- `h(n)` = Heuristic estimate from n to goal (Euclidean distance)
- `s(n)` = Safety penalty for node n

---

## Safety Score Calculation

### 1. Grid-Based Risk Assessment

The city is divided into a grid where each cell has a safety score based on historical crime data:

```python
# Safety score for grid cell (i, j)
S(i,j) = 1 - (W_crime * C(i,j) + W_time * T(i,j) + W_light * L(i,j))
```

Where:
- `C(i,j)` = Normalized crime rate [0,1]
- `T(i,j)` = Time-based risk factor [0,1]
- `L(i,j)` = Lighting conditions factor [0,1]
- `W_crime`, `W_time`, `W_light` = Weight coefficients (sum to 1)

### 2. Crime Density Calculation

Crime density uses **Kernel Density Estimation (KDE)**:

```
ρ(x,y) = (1/nh²) * Σ K((x-xi)/h, (y-yi)/h)
```

Where:
- `K` = Gaussian kernel function
- `h` = Bandwidth parameter (typically 500m for urban areas)
- `(xi, yi)` = Location of crime incident i
- `n` = Total number of incidents

### 3. Temporal Risk Factor

Time-based risk using **Poisson distribution**:

```
P(k crimes in time t) = (λt)^k * e^(-λt) / k!
```

Where:
- `λ` = Average crime rate per hour
- `t` = Time window (hours)
- `k` = Number of crimes

---

## Route Optimization

### 1. Modified Dijkstra's Algorithm

We use a weighted graph where edge weights incorporate safety scores:

```python
# Edge weight between nodes u and v
w(u,v) = d(u,v) * (1 + α * (1 - S_avg(u,v)))
```

Where:
- `d(u,v)` = Physical distance between nodes
- `S_avg(u,v)` = Average safety score along edge
- `α` = Safety importance factor (user-adjustable, 0-10)

### 2. Dynamic Programming Approach

For multi-waypoint routes, we solve using dynamic programming:

```
OPT(i,S) = min{OPT(j,S\{i}) + w(j,i)} for all j in S\{i}
```

Where:
- `OPT(i,S)` = Optimal path ending at i, visiting all nodes in set S
- `S\{i}` = Set S excluding node i

---

## Graph Theory Implementation

### 1. Graph Construction

Streets are represented as a weighted directed graph G(V,E):

```
G = (V, E, W)
V = {intersection points}
E = {street segments}
W = {safety-weighted distances}
```

### 2. Betweenness Centrality

We calculate street importance using betweenness centrality:

```
CB(v) = Σ(s≠v≠t) [σst(v) / σst]
```

Where:
- `σst` = Total shortest paths from s to t
- `σst(v)` = Shortest paths from s to t passing through v

### 3. Community Detection

Safe zones are identified using **Louvain modularity**:

```
Q = (1/2m) * Σij [Aij - (ki*kj)/(2m)] * δ(ci,cj)
```

Where:
- `Aij` = Adjacency matrix
- `ki` = Degree of node i
- `m` = Total number of edges
- `δ(ci,cj)` = 1 if nodes i,j are in same community, 0 otherwise

---

## Machine Learning Models

### 1. Logistic Regression for Risk Prediction

```
P(crime) = 1 / (1 + e^(-(β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ)))
```

Features include:
- Distance to police stations
- Proximity to businesses (24hr vs closed)
- Historical crime patterns
- Street lighting density
- Foot traffic estimates

### 2. Random Forest for Route Classification

The model uses **Gini impurity** for splits:

```
Gini = 1 - Σ(pi)²
```

Where `pi` = Proportion of samples in class i

### 3. Neural Network Architecture

Three-layer feedforward network:
```
Input Layer (7 features) → Hidden Layer (64 neurons, ReLU) → 
Hidden Layer (32 neurons, ReLU) → Output Layer (safety score)
```

Activation function (ReLU):
```
f(x) = max(0, x)
```

Loss function (MSE):
```
L = (1/n) * Σ(yi - ŷi)²
```

---

## Time-Safety Trade-off

### 1. Pareto Optimization

We find Pareto-optimal routes where no objective can be improved without worsening another:

```
minimize: [T(route), R(route)]
```
Where:
- `T(route)` = Total travel time
- `R(route)` = Total risk score

### 2. Weighted Sum Method

User preference α ∈ [0,1] balances time vs safety:

```
Score(route) = α * T_norm(route) + (1-α) * R_norm(route)
```

Where normalized values are:
```
T_norm = (T - T_min) / (T_max - T_min)
R_norm = (R - R_min) / (R_max - R_min)
```

### 3. Constraint Satisfaction

Routes must satisfy:
```
T(route) ≤ T_max = T_shortest * (1 + β)
R(route) ≤ R_threshold
```
Where β = Maximum time increase factor (typically 0.3 or 30%)

---

## Statistical Analysis

### 1. Bayesian Inference for Real-time Updates

Prior probability updated with new crime data:

```
P(safe|data) = P(data|safe) * P(safe) / P(data)
```

### 2. Confidence Intervals

95% confidence interval for safety scores:

```
CI = μ ± 1.96 * (σ/√n)
```

### 3. Spatial Autocorrelation (Moran's I)

Testing for crime clustering:

```
I = (n/W) * [Σij wij(xi-x̄)(xj-x̄)] / [Σi(xi-x̄)²]
```

Where:
- `wij` = Spatial weight between zones i and j
- `W` = Sum of all spatial weights
- `x̄` = Mean crime rate

---

## Implementation Example

```python
def calculate_safe_route(start, end, time_of_day):
    # Build graph with safety weights
    G = build_weighted_graph(city_map, crime_data, time_of_day)
    
    # A* with safety heuristic
    def safety_cost(node):
        base_cost = euclidean_distance(node, end)
        safety_penalty = (1 - get_safety_score(node)) * SAFETY_WEIGHT
        return base_cost + safety_penalty
    
    # Find optimal path
    path = a_star(G, start, end, heuristic=safety_cost)
    
    # Calculate metrics
    total_distance = sum(G[u][v]['distance'] for u,v in path)
    avg_safety = mean([get_safety_score(n) for n in path])
    estimated_time = total_distance / WALKING_SPEED
    
    return {
        'path': path,
        'distance': total_distance,
        'safety_score': avg_safety,
        'estimated_time': estimated_time
    }
```

---

## Performance Metrics

### Algorithm Complexity
- **Dijkstra's**: O(E log V) with binary heap
- **A***: O(E log V) with admissible heuristic
- **KDE calculation**: O(n²) for n crime points
- **Random Forest**: O(m * n * log n) for m trees

### Optimization Techniques
1. **Spatial indexing** using R-trees: O(log n) lookups
2. **Caching** frequently requested routes
3. **Hierarchical pathfinding** for long distances
4. **Parallel processing** for multiple route options

---

## References

1. Hart, P. E.; Nilsson, N. J.; Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"
2. Silverman, B. W. (1986). "Density Estimation for Statistics and Data Analysis"
3. Newman, M. E. J. (2006). "Modularity and community structure in networks"
4. Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs"

---

## Future Improvements

1. **Reinforcement Learning**: Q-learning for adaptive route optimization
2. **Graph Neural Networks**: Better feature extraction from street networks
3. **Ensemble Methods**: Combining multiple ML models for robust predictions
4. **Real-time Streaming**: Apache Kafka for live crime data integration
5. **Quantum Computing**: Exploring quantum annealing for NP-hard routing problems

---

*This mathematical framework ensures SafePath SF provides optimal routes that balance safety and efficiency using rigorous algorithmic approaches.*