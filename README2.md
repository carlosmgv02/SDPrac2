# Sharded Storage System Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Features and Goals](#system-features-and-goals)
3. [System Implementation](#system-implementation)
   - [ Vertical and Horizontal Scalability](#vertical-and-horizontal-scalability)
   - [Sharding Technique](#sharding-technique)
   - [Fault Tolerance](#fault-tolerance)
4. [Real Examples of Sharded Storage Systems](#real-examples-of-sharded-storage-systems)
   - [Example 1: MongoDB](#example-1-mongodb)
   - [Example 2: Apache Cassandra](#example-2-apache-cassandra)
5. [Fault Tolerance and Replica Group Management](#fault-tolerance-and-replica-group-management)
6. [Conclusion](#conclusion)
7. [References](#references)
8. [Authors](#authors)

## Introduction <a name="introduction"></a>
The Sharded Storage System is a scalable and fault-tolerant solution designed to store and access large volumes of data efficiently. It utilizes sharding techniques to partition data into smaller subsets called shards, which can be distributed across multiple servers. The system aims to achieve high performance, horizontal scalability, and fault tolerance.

## System Features and Goals <a name="system-features-and-goals"></a>
The key features and goals of the Sharded Storage System are as follows:

- **Scalability**: The system should be able to handle increasing data volumes and request loads by scaling both vertically and horizontally.
- **Efficient Data Distribution**: Data should be evenly distributed across shards and servers to optimize data access and avoid hotspots.
- **Fault Tolerance**: The system should be resilient to server failures and ensure high availability of data and operations.
- **Automatic Failure Detection**: The system should detect server failures automatically to maintain data consistency and availability.
- **Dynamic Replica Group Management**: In the event of a replica master failure, the system should be able to elect a new master among the remaining replicas.

## System Implementation <a name="system-implementation"></a>

### Vertical and Horizontal Scalability <a name="vertical-and-horizontal-scalability"></a>
The Sharded Storage System is designed to horizontally scalable.

- **Horizontal Scalability**: The system achieves horizontal scalability by distributing data across multiple servers. It makes use of a hashing algorithm to determine shard placement. Each server has a key range, which is stored using a tuple to indicate min and max value saved. By adding more servers to the system, the data and request loads can be distributed across multiple machines, ensuring scalability.

### Sharding Technique <a name="sharding-technique"></a>
Sharding is a technique used to partition data into smaller subsets called shards. Each shard contains a subset of the data, and multiple shards collectively hold the entire dataset.

- **Query Routing**: When a client sends a query, the system uses the shard key to determine the target shard(s) for the query. By knowing which shard holds the relevant data, the query is routed directly to the appropriate shard(s), minimizing the need for scanning the entire dataset.

### Fault Tolerance <a name="fault-tolerance"></a>
The Sharded Storage System incorporates fault tolerance mechanisms to ensure high availability and data consistency.

- **Replication**: Each shard in the system maintains multiple replicas to provide redundancy. Replicas are copies of the shard's data stored on different servers. If a server hosting a replica fails, the system can rely on other replicas to continue serving data and processing requests.

- **Automatic Failure Detection**: To detect server failures, the system uses heartbeat messages or monitoring processes. Each server periodically sends heartbeat messages to its replicas or a monitoring process. If a heartbeat is not received within a certain time period, the server is considered failed, and appropriate actions are taken.

- **Master Election**: In the event of a replica master failure, the remaining replicas participate in an election process to select a new replica master. Various algorithms can be used, such as the Raft algorithm or the Paxos algorithm, to achieve consensus among the replicas and elect a new master. The elected replica takes over the responsibilities of the failed master.

## Real Examples of Sharded Storage Systems <a name="real-examples-of-sharded-storage-systems"></a>

### Example 1: MongoDB <a name="example-1-mongodb"></a>
MongoDB is a popular document-oriented database that utilizes sharding for scalability and performance.

**Architecture Diagram:**
```
+-----------------+         +---------------------+
|                 |         |                     |
|   MongoDB       |         |  MongoDB            |
|   Query Router  +---------> Shard 1             |
|   (mongos)      |         |                     |
|                 |         +---------------------+
|                 |
|                 |         +---------------------+
|                 |         |                     |
|                 +---------> Shard 2             |
|                 |         |                     |
|                 |         +---------------------+
|                 |
|                 |         +---------------------+
|                 |         |                     |
|                 +---------> Shard 3             |
|                 |         |                     |
|                 |         +---------------------+
+-----------------+
```
In MongoDB, sharding is achieved by dividing data into chunks based on a shard key. Each shard is a separate MongoDB replica set that contains a subset of the data. The system uses a configuration server to track metadata about the sharded data, including chunk ranges and shard mappings. The query router, known as the `mongos` process, receives queries from clients and routes them to the appropriate shards based on the shard key.

### Example 2: Apache Cassandra <a name="example-2-apache-cassandra"></a>
Apache Cassandra is a distributed and highly scalable NoSQL database that utilizes a decentralized peer-to-peer architecture.

**Architecture Diagram:**
```text
+-----------------+
|                 |
|   Apache        |
|   Cassandra     |
|                 |
|                 |
|    +-----------+-------------+
|    |           |             |
|    |   Node 1  |   Node 2    |
|    |           |             |
|    +-----------+-------------+
|                 |
|    +-----------+-------------+
|    |           |             |
|    |   Node 3  |   Node 4    |
|    |           |             |
|    +-----------+-------------+
|                 |
|    +-----------+-------------+
|    |           |             |
|    |   Node 5  |   Node 6    |
|    |           |             |
|    +-----------+-------------+
|                 |
+-----------------+
```

In Cassandra, data is distributed across multiple nodes in a ring-based architecture. Each node in the cluster is responsible for a portion of the data based on a partition key. The system uses a gossip protocol for failure detection and membership management. The replicas are distributed across multiple nodes using a replication strategy, such as SimpleStrategy or NetworkTopologyStrategy, to ensure fault tolerance and data redundancy.

## Fault Tolerance and Replica Group Management <a name="fault-tolerance-and-replica-group-management"></a>
For fault tolerance and replica group management, the Sharded Storage System implements the following strategies:

- **Automatic Failure Detection**: The system regularly sends heartbeat messages or monitors the health of each server in the replica group. If a server fails to respond within a specified time, it is considered failed, and appropriate actions are taken.

- **Master Election**: In the event of a replica master failure, the remaining replicas participate in an election process to select a new replica master. Consensus algorithms such as Raft or Paxos can be used to ensure agreement among the replicas. Once a new master is elected, it assumes the responsibilities of the failed master.

## Conclusion <a name="conclusion"></a>
The Sharded Storage System is designed to provide scalability, fault tolerance, and high performance for storing and accessing large volumes of data. By utilizing sharding techniques, the system distributes data across multiple servers, allowing for both vertical and horizontal scalability. Fault tolerance mechanisms, including replication and automatic failure detection, ensure high availability and data consistency. Real-world examples such as MongoDB and Apache Cassandra demonstrate the practical implementations of sharded storage systems.

By addressing the system's features and goals, explaining the design choices, and discussing fault tolerance mechanisms, this document provides an overview of the Sharded Storage System's architecture and functionality.

## References <a name="references"></a>
1. [Redis](https://redis.io/)
2. [MongoBD](https://www.mongodb.com/cloud/atlas/lp/try4?utm_source=google&utm_campaign=search_gs_pl_evergreen_atlas_core_prosp-brand_gic-null_emea-es_ps-all_desktop_eng_lead&utm_term=mongodb&utm_medium=cpc_paid_search&utm_ad=e&utm_ad_campaign_id=12212624563&adgroup=115749706983&cq_cmp=12212624563&gad=1&gclid=CjwKCAjwkLCkBhA9EiwAka9QRgSOtDPauzwqJCFJhDZwq-UKtwqfU2BhelTBW2yCQ4Xtn0jjZIi9pxoCXr8QAvD_BwE)
3. [Apache Cassandra](https://cassandra.apache.org/_/index.html)

## Authors
* Carlos Martínez: [carlosmgv02](https://github.com/carlosmgv02)
* Nil Monfort: [nilm9](https://github.com/nilm9) 
