# A3. Foundational Systems and Their Modern Equivalents

Google's foundational systems address three complementary challenges: storing large files reliably, processing distributed datasets, and serving structured records efficiently. Their principles remain relevant to Company A's survey service, although modern technologies provide different execution models and operational responsibilities.

## Original Problems and Core Mechanisms

**Google File System (GFS)** addressed reliable storage of large datasets on inexpensive machines where hardware failures were expected. Files were divided into 64 MB chunks distributed across chunkservers, normally with three replicas. A single master maintained metadata, including the namespace and chunk locations, while clients transferred file data directly to chunkservers. Replication and automatic recovery maintained availability despite individual server failures. The design prioritised throughput for large sequential operations rather than low latency for numerous small files.

**MapReduce** simplified large-scale computation by hiding scheduling, communication and worker failure handling. The map function transformed input records into intermediate key-value pairs. Shuffle transferred and grouped intermediate values by key, and reduce combined each group into final results. Failed tasks were scheduled again; completed map tasks could also require re-execution when their locally stored outputs became unavailable. For survey reporting, mapping each valid response to `(rating, 1)` and reducing by addition produces rating totals. A MapReduce input split defines a processing task's input; a GFS chunk defines a storage unit. These concepts are related but are not identical.

**Bigtable** addressed scalable storage and access for structured datasets with varied latency requirements. Its data model is a sparse, sorted map indexed by row key, column key and timestamp. Row keys determine ordering and enable targeted lookups; column families group related columns; timestamps distinguish multiple versions of a cell. Tables are partitioned into tablets distributed across servers. This supports record access and range scans without requiring complete files to be processed for every request.

## Comparison with Modern Technologies

| Historical system | Current successor or equivalent | What stays the same | What changed and why |
|---|---|---|---|
| GFS | Apache Hadoop HDFS 3.5.0 | Large files are partitioned across storage workers; metadata management and replication support reliable access. | HDFS uses NameNodes and DataNodes. Configurable active/standby NameNodes support failover, reducing metadata-service downtime. HDFS is an equivalent design rather than Google's direct successor. |
| MapReduce | Apache Spark 4.3.0 | Partitioned computation, key-based shuffling and recovery through recomputation remain central. | Spark uses directed acyclic graphs (DAGs) and supports caching reusable datasets in memory, reducing repeated computation and disk access in iterative workloads. Shuffles can still involve disk. |
| Bigtable | Google Cloud Bigtable | Sorted row keys, column families and timestamped cell versions retain the original model. | Managed upgrades, configurable autoscaling and replication across clusters reduce administration and support changing workloads and availability requirements. |

## Relevance to Company A

For Company A, these ideas distinguish durable export storage, daily aggregation and individual-response lookup. Exported survey files support repeatable reporting, aggregation computes rating totals, and a live record store supports the help desk's response-ID queries. However, approximately 500 submissions per day do not justify operating large distributed clusters. The systems provide conceptual guidance; actual technology selection should match workload size and the three-person IT team's capacity. Distributed processing introduces scheduling and communication overhead, so its educational value should be distinguished from its practical necessity at this scale.
